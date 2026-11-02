from __future__ import annotations

from copy import deepcopy
import io
from pathlib import Path
import tempfile
import os
import subprocess
import sys
import time
import signal
import unittest
from unittest.mock import patch
import zipfile

from quality_trust import VERSION, EXTERNAL_VERSION, Git, Invalid, artifact, canonical, lock_value, parse_json, sha
from quality.external_clock import Reading
from quality.external_model import bound, continuity, registry, observer_bound
from quality.external_store import ImportOutcome, checkpoint, create, import_records, load, receive, state_root
from quality.schema import checked
from tests.external_support import D, Fixture, ROOT, config
from tools.build_external import archive, payload

ARTIFACT: Path | None = None


class ExternalCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package_temp = tempfile.TemporaryDirectory()
        cls.package = Path(cls.package_temp.name).resolve() / "candidate.pyz"
        if ARTIFACT:
            data = ARTIFACT.read_bytes()
            with zipfile.ZipFile(io.BytesIO(data)) as source:
                cls.source = parse_json(source.read("manifest.json"))["source"]
        else:
            cls.source = "1" * 40
            data = archive(payload(lambda name: (ROOT / name).read_bytes()), cls.source)
        cls.package.write_bytes(data)
        cls.digest = sha(data)
        artifact(data, cls.digest, cls.source, version=EXTERNAL_VERSION, schema_version=2, entrypoint="quality/external_cli.py")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.package_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name), self.package, self.digest, self.source)

    def assert_result(self, result: object, output: dict | None, expected: str) -> dict:
        self.assertIsNotNone(output, result.stderr)
        self.assertEqual(result.returncode, {"pass": 0, "fail": 1, "incomplete": 2}[expected], result.stderr)
        self.assertEqual(output["report"]["overall"], expected)
        checked("external-report", output["report"])
        return output["report"]

class ExternalTests(ExternalCase):
    def test_bound_success_and_thin_shim(self) -> None:
        plan = self.fx.plan(shim=True)
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer, shim=True)
        report = self.assert_result(result, output, "pass")
        self.assertEqual(report["evidence_kind"], "external-attestation")
        self.assertEqual(self.fx.git("status", "--porcelain"), "")
        self.assertFalse(list(self.fx.state.glob("**/snapshot-*")))
        path = self.fx.state / plan["plan_id"] / "record.json"
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        bases = {row["evidence_basis"] for row in report["stages"]}
        self.assertIn("external-controller-observation", bases)
        self.assertIn("operator-approval", bases)

    def test_natural_failure_survives_missing_controls_output_and_malformed_extra(self) -> None:
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan, 7)
        envelope["records"][0]["output_complete"] = False
        envelope["records"][0]["coverage"]["kind"] = "partial"
        envelope["records"].append({"malformed": True})
        result, output = self.fx.receive(plan, envelope, None)
        self.assert_result(result, output, "fail")
        _, state = load(self.fx.state, plan["plan_id"])
        self.assertTrue(state["failure"])
        self.assertIn("malformed-extra-record", state["integrity_gaps"])
        result, output = self.fx.receive(plan, b"not json", None)
        self.assert_result(result, output, "fail")

    def test_idempotent_recovery_and_conflicting_success_cannot_replace_original(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        first, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(first, output, "pass")
        _, original = load(self.fx.state, plan["plan_id"])
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "pass")
        _, retried = load(self.fx.state, plan["plan_id"])
        self.assertEqual(retried["original"], original["original"])
        envelope["records"][0]["invocation_id"] = "different-invented-invocation"
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")
        _, final = load(self.fx.state, plan["plan_id"])
        self.assertEqual(final["original"], original["original"])
        self.assertIn("conflicting-producer-evidence", final["integrity_gaps"])

    def test_conflicting_failure_is_retained_and_cannot_be_erased(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "pass")
        bad = deepcopy(envelope)
        bad["records"][0]["outcome"]["exit_code"] = 9
        result, output = self.fx.receive(plan, bad, observer)
        self.assert_result(result, output, "fail")
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "fail")
        _, state = load(self.fx.state, plan["plan_id"])
        self.assertEqual(state["original"][0]["record"]["outcome"]["exit_code"], 0)
        self.assertEqual(state["failure"][0]["record"]["outcome"]["exit_code"], 9)

    def test_wrong_consumed_origin_environment_or_mechanism_never_attributes_failure(self) -> None:
        mutations = [lambda r: r["consumed"].update(origin_tree="2" * 40),
            lambda r: r["consumed"].update(environment_sha256="b" * 64),
            lambda r: r["consumed"].update(established=False),
            lambda r: r["consumed"].update(mechanism_sha256="b" * 64),
            lambda r: r["consumed"].update(after_context_sha256="b" * 64),
            lambda r: r.update(canonical_sha256="b" * 64)]
        for change in mutations:
            with self.subTest(change=change):
                plan = self.fx.plan()
                envelope, observer = self.fx.facts(plan, 7)
                change(envelope["records"][0])
                result, output = self.fx.receive(plan, envelope, observer)
                self.assert_result(result, output, "incomplete")
                _, state = load(self.fx.state, plan["plan_id"])
                self.assertFalse(state["failure"])

    def test_controller_scope_and_source_must_be_valid(self) -> None:
        mutations = [lambda o: o.update(invocation_id="other"), lambda o: o.update(observer_id="other"),
            lambda o: o.update(profile_sha256="b" * 64), lambda o: o.update(mechanism_sha256="b" * 64),
            lambda o: o.update(source_route="producer"), lambda o: o.update(basis="manual-fact"),
            lambda o: o.update(observed_from_ms=o["observed_from_ms"] + 2),
            lambda o: o.update(observed_through_ms=o["cleanup_at_ms"]),
            lambda o: o.update(cleanup_at_ms=o["cleanup_at_ms"] - 1)]
        for change in mutations:
            with self.subTest(change=change):
                plan = self.fx.plan()
                envelope, observer = self.fx.facts(plan)
                change(observer)
                result, output = self.fx.receive(plan, envelope, observer)
                self.assert_result(result, output, "incomplete")

    def test_missing_unknown_and_duplicate_controls_are_incomplete(self) -> None:
        for mode in ("missing", "unknown", "unavailable", "duplicate"):
            with self.subTest(mode=mode):
                plan = self.fx.plan()
                envelope, observer = self.fx.facts(plan)
                if mode == "missing":
                    observer["observations"].pop()
                elif mode == "duplicate":
                    observer["observations"].append(deepcopy(observer["observations"][0]))
                else:
                    observer["observations"][0]["state"] = mode
                result, output = self.fx.receive(plan, envelope, observer)
                self.assert_result(result, output, "incomplete")

    def test_unknown_provenance_requires_containment(self) -> None:
        for trust, provenance in ((True, "unknown"), (True, "untrusted"), (False, "trusted-local")):
            plan = self.fx.plan(trusted=trust)
            envelope, observer = self.fx.facts(plan)
            envelope["records"][0]["consumed"]["provenance"] = provenance
            result, output = self.fx.receive(plan, envelope, observer, trusted=trust)
            report = self.assert_result(result, output, "incomplete")
            self.assertTrue(any(row["id"] == "control:containment" and row["status"] == "incomplete" for row in report["stages"]))

    def test_registered_containment_cannot_be_removed_by_trusted_head(self) -> None:
        self.fx.config["gate"]["required_controls"].append("containment")
        self.fx.write(".quality/config.json", canonical(self.fx.config))
        self.fx.head = self.fx.base = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        observer["observations"] = [row for row in observer["observations"] if row["kind"] != "containment"]
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")

    def test_deferred_features_phase_and_non_natural_outcomes(self) -> None:
        mutations = [lambda r, f=f: r.update(features=[f]) for f in ("cache", "conditional", "cross-phase", "git-aware-execution")]
        mutations += [lambda r: r.update(phase="precommit")]
        mutations += [lambda r, kind=kind: r["outcome"].update(kind=kind, exit_code=124) for kind in ("terminated", "wrapper-error", "unknown")]
        for change in mutations:
            with self.subTest(change=change):
                plan = self.fx.plan()
                envelope, observer = self.fx.facts(plan)
                change(envelope["records"][0])
                result, output = self.fx.receive(plan, envelope, observer)
                self.assert_result(result, output, "incomplete")

    def test_future_prechallenge_clock_and_elapsed_budget(self) -> None:
        mutations = [lambda r, p: r["timing"].update(started_ms=p["issued_wall_ms"] - 10),
            lambda r, p: r["timing"].update(finished_ms=p["issued_wall_ms"] + 1000000),
            lambda r, p: r["timing"]["clock"].update(boot_sha256="b" * 64),
            lambda r, p: r["timing"].update(elapsed_ms=20000)]
        for change in mutations:
            with self.subTest(change=change):
                plan = self.fx.plan()
                envelope, observer = self.fx.facts(plan)
                change(envelope["records"][0], plan)
                result, output = self.fx.receive(plan, envelope, observer)
                self.assert_result(result, output, "incomplete")

    def test_partial_coverage_effects_and_output_never_pass(self) -> None:
        mutations = [lambda r: r["coverage"].update(kind="partial"), lambda r: r["coverage"].update(sha256="b" * 64),
            lambda r: r.update(effects=["disposable-files"]), lambda r: r.update(output_complete=False)]
        for change in mutations:
            plan = self.fx.plan()
            envelope, observer = self.fx.facts(plan)
            change(envelope["records"][0])
            result, output = self.fx.receive(plan, envelope, observer)
            self.assert_result(result, output, "incomplete")

    def test_malformed_common_frame_and_wrong_challenge_are_not_salvaged(self) -> None:
        for mode in ("syntax", "duplicate-key", "challenge", "context", "schema", "protocol"):
            plan = self.fx.plan()
            envelope, observer = self.fx.facts(plan, 7)
            if mode == "syntax":
                envelope = canonical(envelope)[:-2]
            elif mode == "duplicate-key":
                envelope = b'{"schema_version":2,' + canonical(envelope)[1:]
            elif mode == "challenge":
                envelope["challenge"] = "b" * 64
            elif mode == "context":
                envelope["context_sha256"] = "b" * 64
            elif mode == "schema":
                envelope["schema_version"] = 1
            else:
                envelope["protocol"] = "old"
            result, output = self.fx.receive(plan, envelope, observer)
            self.assert_result(result, output, "incomplete")
            _, state = load(self.fx.state, plan["plan_id"])
            self.assertFalse(state["failure"])

    def test_duplicate_extra_record_is_incomplete(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        envelope["records"].append(deepcopy(envelope["records"][0]))
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")

    def test_head_side_policy_launcher_and_lock_are_only_data(self) -> None:
        self.fx.write(".quality/config.json", '{"schema_version":999}')
        self.fx.write(".quality/lock.json", '{"version":"forged"}')
        self.fx.write("quality_external_launch.py", "Invented inert text, never loaded.\n")
        self.fx.head = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "pass")
        self.assertEqual(plan["registry"], self.fx.config)

    def test_dirty_moving_head_ref_and_index_invalidate_context(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        self.fx.write("new.txt", "Invented new subject.\n")
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")
        self.fx.git("add", "new.txt")
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")
        self.fx.head = self.fx.commit()
        before = (self.fx.state / plan["plan_id"] / "record.json").read_bytes()
        result, output = self.fx.receive(plan, envelope, observer)
        # A different immutable request cannot activate or mutate this ledger.
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIsNone(output)
        self.assertEqual((self.fx.state / plan["plan_id"] / "record.json").read_bytes(), before)
        self.fx.git("update-ref", "refs/heads/main", self.fx.base)
        self.fx.git("reset", "--hard", self.fx.base)
        self.fx.head = self.fx.base
        self.fx.git("update-ref", "refs/heads/observed", self.fx.base)
        self.fx.config["gate"]["refs"].append("refs/heads/observed")
        self.fx.write(".quality/config.json", canonical(self.fx.config))
        self.fx.head = self.fx.base = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        self.fx.git("update-ref", "refs/heads/observed", self.fx.head)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")

    def test_input_approval_and_path_boundaries(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        args = self.fx.inputs(envelope, observer)
        for flag, bad in (("--evidence-sha256", "b" * 64), ("--approved-producer", "other"),
                          ("--observations-sha256", "b" * 64), ("--approved-observer", "other")):
            changed = list(args)
            changed[changed.index(flag) + 1] = bad
            result, output = self.fx.run("import", "--plan", plan["plan_id"], *changed)
            self.assert_result(result, output, "incomplete")
        link = self.fx.root / "receipt-link.json"
        link.symlink_to(self.fx.root / "receipt.json")
        args[args.index("--evidence") + 1] = str(link)
        result, output = self.fx.run("import", "--plan", plan["plan_id"], *args)
        self.assert_result(result, output, "incomplete")
        with self.assertRaises(Invalid):
            state_root(self.fx.repo / "unsafe", [self.fx.repo])
        with self.assertRaises(Invalid):
            state_root(self.fx.root, [self.fx.repo])

    def test_corrupt_state_refused_without_overwriting(self) -> None:
        plan = self.fx.plan()
        path = self.fx.state / plan["plan_id"] / "record.json"
        corrupted = canonical({**plan, "challenge": "b" * 64})
        path.write_bytes(corrupted)
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(output)
        self.assertEqual(path.read_bytes(), corrupted)

    def test_interruption_after_failure_checkpoint_recovers(self) -> None:
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan, 7)
        args = self.fx.inputs(envelope, None)
        clock = self.fx.clock(plan)
        real_checkpoint = checkpoint
        def interrupted(path: Path, state: dict, reading: Reading) -> None:
            real_checkpoint(path, state, reading)
            if state["failure"] and "import-interrupted" not in state["request_gaps"]:
                raise KeyboardInterrupt
        with patch("quality.external_store.checkpoint", interrupted):
            state = receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], clock,
                [self.fx.repo, self.fx.cache, self.fx.state], evidence=Path(args[1]), evidence_sha256=args[3],
                producer=args[5], final_clock=lambda: clock)
        self.assertEqual(state["report"]["overall"], "fail")
        result, output = self.fx.receive(plan, envelope, None)
        self.assert_result(result, output, "fail")

    def test_clock_rollback_expiry_and_persisted_failure(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "pass")
        args = self.fx.inputs(envelope, observer)
        for delta, mono_delta in ((61003, 61003), (-1, 10), (5000, 10)):
            clock = Reading(plan["issued_wall_ms"] + delta, plan["issued_mono_ms"] + mono_delta,
                            plan["context"]["clock"]["boot_sha256"])
            state = receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], clock,
                [self.fx.repo, self.fx.cache, self.fx.state], evidence=Path(args[1]), evidence_sha256=args[3], producer=args[5], final_clock=lambda: clock)
            self.assertEqual(state["report"]["overall"], "incomplete")
            load(self.fx.state, plan["plan_id"])
        envelope["records"][0]["outcome"]["exit_code"] = 7
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "fail")
        path, state = load(self.fx.state, plan["plan_id"])
        checkpoint(path, state, Reading(plan["issued_wall_ms"] - 1, plan["issued_mono_ms"] + 100, "b" * 64))
        _, persisted = load(self.fx.state, plan["plan_id"])
        self.assertEqual(persisted["report"]["overall"], "fail")

    def test_unsupported_obligations_are_explicit_incomplete(self) -> None:
        self.fx.config["unsupported_obligations"] = [{"id": "actual-index", "description": "Invented unsupported actual-index obligation"}]
        self.fx.write(".quality/config.json", canonical(self.fx.config))
        self.fx.head = self.fx.base = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        report = self.assert_result(result, output, "incomplete")
        self.assertTrue(any(row["id"] == "unsupported:actual-index" for row in report["stages"]))

    def test_registry_bounds_and_v1_defaults_reject_cross_version(self) -> None:
        value = config()
        registry(value)
        for field, values in (("budget_seconds", (0, 3601)), ("import_window_seconds", (0, 901))):
            for number in values:
                bad = deepcopy(value)
                bad["gate"][field] = number
                with self.assertRaises(Invalid):
                    registry(bad)
        for mutation in (lambda c: c["gate"].update(required_controls=["deadline", "deadline"]),
            lambda c: c["gate"].update(trust_rule="always-contained"),
            lambda c: c["gate"].update(observer_id=c["gate"]["producer_id"])):
            bad = deepcopy(value)
            mutation(bad)
            with self.assertRaises(Invalid):
                registry(bad)
        pin = {"schema_version": 1, "publisher": "orlenko/software-quality", "source": "1" * 40,
               "artifact_sha256": D, "version": VERSION, "policy_version": "0.1"}
        self.assertEqual(lock_value(canonical(pin)), pin)
        with self.assertRaises(Invalid):
            lock_value(canonical(pin), version=EXTERNAL_VERSION, schema_version=2)
        with self.assertRaises(Invalid):
            artifact(self.package.read_bytes(), self.digest, self.source)

    def test_package_is_deterministic_and_has_no_execution_route(self) -> None:
        files = payload(lambda name: (ROOT / name).read_bytes())
        self.assertEqual(archive(files, "1" * 40), archive(files, "1" * 40))
        with zipfile.ZipFile(self.package) as package:
            self.assertFalse({"quality/runner.py", "quality/process.py", "quality/cli.py"} & set(package.namelist()))
            self.assertEqual(package.read("policy/development-standard.md"), (ROOT / "docs/development-standard.md").read_bytes())
        altered = self.package.read_bytes() + b"invented tamper"
        with self.assertRaises(Invalid):
            artifact(altered, self.digest, self.source, version=EXTERNAL_VERSION, schema_version=2, entrypoint="quality/external_cli.py")

    def test_explicit_deadline_cleanup_and_observer_conflict(self) -> None:
        for field, value in (("deadline_at_ms", 0), ("deadline_at_ms", 9007199254740991), ("cleanup_state", "unknown")):
            plan = self.fx.plan()
            envelope, observer = self.fx.facts(plan)
            observer[field] = value
            result, output = self.fx.receive(plan, envelope, observer)
            self.assert_result(result, output, "incomplete")
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        observer["observations"][0]["state"] = "unknown"
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")
        observer["observations"][0]["state"] = "enforced"
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "incomplete")
        _, state = load(self.fx.state, plan["plan_id"])
        self.assertIn("conflicting-controller-evidence", state["integrity_gaps"])
        self.assertEqual(state["observer"][0]["document"]["observations"][0]["state"], "unknown")

    def test_old_protocol_wrong_identity_and_pin_refused(self) -> None:
        result = self.fx.command("--adapter-protocol", "1", "doctor")
        self.assertEqual(result.returncode, 2)
        result, output = self.fx.run("doctor", "--identity", "example/other")
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(output)
        cached = self.fx.cache / (self.digest + ".pyz")
        cached.chmod(0o600)
        cached.write_bytes(cached.read_bytes() + b"invented tamper")
        result, output = self.fx.run("doctor")
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(output)

    def test_replay_to_another_plan_is_incomplete(self) -> None:
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan, 7)
        other = self.fx.plan()
        result, output = self.fx.receive(other, envelope, observer)
        self.assert_result(result, output, "incomplete")
        _, state = load(self.fx.state, other["plan_id"])
        self.assertFalse(state["failure"])

    def test_atomic_save_cleanup_and_locked_route(self) -> None:
        from quality.evidence import save, target_lock
        plan = self.fx.plan()
        path = self.fx.state / plan["plan_id"] / "record.json"
        old = path.read_bytes()
        with patch("quality.evidence.os.replace", side_effect=OSError("invented interruption")):
            with self.assertRaises(OSError):
                save(path, plan, "external-state")
        self.assertEqual(path.read_bytes(), old)
        self.assertFalse(list(path.parent.glob(".report-*")))
        with target_lock(self.fx.state, path.parent):
            with self.assertRaises(Invalid):
                with target_lock(self.fx.state, path.parent):
                    self.fail("contending route acquired")

    def test_target_ancestor_alias_chain_is_refused_and_var_alias_is_safe(self) -> None:
        outside = self.fx.root / "external"
        outside.mkdir()
        (self.fx.repo / "back").symlink_to(outside, target_is_directory=True)
        alias = self.fx.root / "alias"
        alias.symlink_to(self.fx.repo, target_is_directory=True)
        self.fx.head = self.fx.base = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        args = self.fx.inputs(envelope, observer)
        (outside / "receipt.json").write_bytes(canonical(envelope))
        args[args.index("--evidence") + 1] = str(alias / "back" / "receipt.json")
        result, output = self.fx.run("import", "--plan", plan["plan_id"], *args)
        self.assert_result(result, output, "incomplete")
        result, output = self.fx.run("doctor", "--state", str(alias / "back" / "state"))
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(output)
        self.assertFalse((outside / "state").exists())
        if str(self.fx.root).startswith("/private/var/"):
            args = self.fx.inputs(envelope, observer)
            args[args.index("--evidence") + 1] = str(self.fx.root / "receipt.json").replace("/private/var/", "/var/", 1)
            result, output = self.fx.run("import", "--plan", plan["plan_id"], *args)
            self.assert_result(result, output, "pass")

    def test_issuance_follows_durable_challenge_not_inspection_start(self) -> None:
        plan = self.fx.plan()
        before = self.fx.clock(plan, 100)
        issued = self.fx.clock(plan, 1000)
        state = create(self.fx.state, plan["context"], plan["registry"], before, issuance_clock=lambda: issued, protected_roots=[self.fx.repo])
        envelope, _ = self.fx.facts(state, 7)
        record = envelope["records"][0]
        record["timing"].update(started_ms=before.wall_ms + 10, finished_ms=issued.wall_ms + 10,
                               started_mono_ms=before.mono_ms + 10, finished_mono_ms=issued.mono_ms + 10)
        self.assertFalse(bound(state, record, issued.wall_ms + 100, issued.mono_ms + 100))
        path = self.fx.state / state["plan_id"] / "record.json"
        state["issued"] = False
        checkpoint(path, state, issued)
        with self.assertRaises(Invalid):
            load(self.fx.state, state["plan_id"])

    def test_within_tolerance_wall_rollback_cannot_extend_window(self) -> None:
        self.fx.config["gate"]["import_window_seconds"] = 1
        self.fx.write(".quality/config.json", canonical(self.fx.config))
        self.fx.head = self.fx.base = self.fx.commit()
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        result, output = self.fx.receive(plan, envelope, observer)
        self.assert_result(result, output, "pass")
        args = self.fx.inputs(envelope, observer)
        clock = Reading(plan["issued_wall_ms"] + 510, plan["issued_mono_ms"] + 1510, plan["context"]["clock"]["boot_sha256"])
        self.assertTrue(continuity(plan, clock))
        state = receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], clock,
            [self.fx.repo, self.fx.cache, self.fx.state], evidence=Path(args[1]), evidence_sha256=args[3], producer=args[5], final_clock=lambda: clock)
        self.assertEqual(state["report"]["overall"], "incomplete")

    def test_late_deadline_contradiction_does_not_pass_or_erase_failure(self) -> None:
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, observer = self.fx.facts(plan, code)
            timing = envelope["records"][0]["timing"]
            timing["finished_ms"] = timing["started_ms"] + 500
            timing["finished_mono_ms"] = timing["started_mono_ms"] + 500
            timing["elapsed_ms"] = 500
            observer["deadline_at_ms"] = timing["started_ms"] + 1
            observer["deadline_at_mono_ms"] = timing["started_mono_ms"] + 1
            observer["cleanup_at_ms"] = timing["finished_ms"]
            observer["cleanup_at_mono_ms"] = timing["finished_mono_ms"]
            observer["observed_through_ms"] = timing["finished_ms"] + 1
            observer["observed_through_mono_ms"] = timing["finished_mono_ms"] + 1
            # JSON fact timestamps must precede actual import, no producer runs.
            while int(time.time_ns() / 1000000) <= timing["finished_ms"] + 1:
                time.sleep(0.01)
            result, output = self.fx.receive(plan, envelope, observer)
            self.assert_result(result, output, "fail" if code else "incomplete")

    def test_late_clock_and_metadata_errors_preserve_known_failure(self) -> None:
        for failure in ("clock", "metadata"):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, 7)
            args = self.fx.inputs(envelope, None)
            clock = self.fx.clock(plan)
            def broken_clock() -> Reading:
                raise Invalid("invented-clock-failure")
            with patch("quality.external_store.metadata", side_effect=subprocess.TimeoutExpired("invented-git-inspection", 30)) if failure == "metadata" else patch("quality.external_store.metadata", return_value=plan["context"]["metadata"]):
                state = receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], clock,
                    [self.fx.repo, self.fx.cache, self.fx.state], evidence=Path(args[1]), evidence_sha256=args[3], producer=args[5],
                    final_clock=broken_clock if failure == "clock" else lambda: clock)
            self.assertEqual(state["report"]["overall"], "fail")
            _, durable = load(self.fx.state, plan["plan_id"])
            self.assertEqual(durable["report"]["overall"], "fail")

    def test_actual_cli_interrupt_after_checkpoint_preserves_failure(self) -> None:
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, code)
            # Eight bounded records provide independent parsing/checkpoint work.
            for index in range(7):
                extra = deepcopy(envelope["records"][0])
                extra["invocation_id"] = "invented-extra-" + str(index)
                extra["note"] = "invented " * 100
                envelope["records"].append(extra)
            args = self.fx.inputs(envelope, None)
            package = self.fx.cache / (self.digest + ".pyz")
            command = [sys.executable, "-I", "-S", str(package), "import", "--repo", str(self.fx.repo),
                       "--base", self.fx.base, "--head", self.fx.head, "--identity", "example/invented", "--state", str(self.fx.state),
                       "--artifact-sha256", self.digest, "--source", self.source, "--trusted-head", self.fx.head,
                       "--plan", plan["plan_id"], *args]
            path = self.fx.state / plan["plan_id"] / "record.json"
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={"PATH": os.defpath, "LC_ALL": "C"}) as process:
                deadline = time.monotonic() + 20
                observed = False
                while time.monotonic() < deadline and process.poll() is None:
                    state = parse_json(path.read_bytes())
                    if state["failure"] if code else state["original"]:
                        observed = True
                        process.send_signal(signal.SIGTERM)
                        break
                    time.sleep(0.001)
                output, error = process.communicate(timeout=20)
                self.assertTrue(observed, error.decode())
                self.assertEqual(process.returncode, 1 if code else 2, error.decode())
                delivered = parse_json(output)
                self.assertTrue(any("import-interrupted" in row["reason"] for row in delivered["report"]["stages"]),
                                "current invocation did not demonstrate handled cancellation")
            _, state = load(self.fx.state, plan["plan_id"])
            self.assertEqual(state["report"]["overall"], "fail" if code else "incomplete")
            result, output = self.fx.receive(plan, envelope, None)
            self.assert_result(result, output, "fail" if code else "incomplete")

    def test_observer_clock_pairs_must_describe_supported_instants(self) -> None:
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, observer = self.fx.facts(plan, code)
            observer["deadline_at_mono_ms"] -= 8000
            result, output = self.fx.receive(plan, envelope, observer)
            self.assert_result(result, output, "fail" if code else "incomplete")
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        wall, mono = plan["issued_wall_ms"], plan["issued_mono_ms"]
        timing = envelope["records"][0]["timing"]
        timing.update(started_ms=wall+10000, finished_ms=wall+11000,
                      started_mono_ms=mono+10000, finished_mono_ms=mono+11000, elapsed_ms=1000)
        plan["original"] = [{"record": envelope["records"][0]}]
        observer.update(observed_from_ms=wall+1000, observed_from_mono_ms=mono+1000,
                        observed_through_ms=wall+28000, observed_through_mono_ms=mono+28000,
                        cleanup_at_ms=wall+11000, cleanup_at_mono_ms=mono+11000,
                        deadline_at_ms=wall+20000, deadline_at_mono_ms=mono+20000)
        self.assertTrue(observer_bound(plan, observer, wall+50000, mono+50000))
        for prefix, amount in (("observed_from", 5000), ("observed_through", -8000), ("cleanup_at", 8000), ("deadline_at", -8000)):
            bad = deepcopy(observer)
            bad[prefix + "_mono_ms"] += amount
            self.assertFalse(observer_bound(plan, bad, wall+50000, mono+50000), prefix)
        timing.update(started_ms=wall, started_mono_ms=mono)
        self.assertFalse(bound(plan, envelope["records"][0], wall+50000, mono+50000))

    def test_symlink_parent_components_cannot_hide_target_paths(self) -> None:
        child = self.fx.repo / "child"
        child.mkdir()
        alias = self.fx.root / "parent-alias"
        alias.symlink_to(child, target_is_directory=True)
        plan = self.fx.plan()
        envelope, observer = self.fx.facts(plan)
        args = self.fx.inputs(envelope, observer)
        # The effective file would be target/receipt.json, not root/receipt.json.
        # Do not create it: refusal must precede target-controlled file access.
        args[args.index("--evidence") + 1] = str(alias / ".." / "receipt.json")
        result, output = self.fx.run("import", "--plan", plan["plan_id"], *args)
        self.assert_result(result, output, "incomplete")
        result, output = self.fx.run("doctor", "--state", str(alias / ".." / "state"))
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(output)
        self.assertFalse((self.fx.repo / "state").exists())
        from quality_trust import outside_path
        with self.assertRaises(Invalid):
            outside_path(alias / ".." / "receipt.json", [self.fx.repo])

    def test_shared_evidence_exports_remain_v1_compatible(self) -> None:
        from quality import evidence, runner
        self.assertIs(runner.stage, evidence.stage)
        self.assertIs(runner.save, evidence.save)
        self.assertEqual(evidence.verdict([evidence.stage("failure", "fail"), evidence.stage("gap")]), "fail")
        with self.assertRaises(Invalid):
            parse_json(b'{"invented":1,"invented":2}')


class FinalizationTests(ExternalCase):
    def receive_local(self, plan, envelope, *, final_clock=None, outcome=None):
        args = self.fx.inputs(envelope, None)
        clock = self.fx.clock(plan)
        return receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], clock,
            [self.fx.repo, self.fx.cache, self.fx.state], evidence=Path(args[1]), evidence_sha256=args[3],
            producer=args[5], final_clock=final_clock or (lambda: clock), outcome=outcome)

    def test_final_clock_interruption_returns_current_failure_or_incomplete(self):
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, code)
            def interrupted():
                raise KeyboardInterrupt
            state = self.receive_local(plan, envelope, final_clock=interrupted)
            self.assertEqual(state["report"]["overall"], "fail" if code else "incomplete")
            self.assertIn("import-interrupted", state["request_gaps"])
            _, stored = load(self.fx.state, plan["plan_id"])
            self.assertEqual(stored["report"]["overall"], state["report"]["overall"])

    def test_uncommitted_positive_not_consumed_during_interrupted_recovery(self):
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan)
        real_replace = __import__("os").replace
        fired = False
        def before_publish(source, destination):
            nonlocal fired
            if not fired:
                fired = True
                raise KeyboardInterrupt
            return real_replace(source, destination)
        with patch("quality.evidence.os.replace", before_publish):
            state = self.receive_local(plan, envelope)
        self.assertFalse(state["original"])
        self.assertEqual(state["report"]["overall"], "incomplete")
        _, stored = load(self.fx.state, plan["plan_id"])
        self.assertFalse(stored["original"])

    def test_published_positive_reconciled_without_rollback(self):
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan)
        real_replace = __import__("os").replace
        fired = False
        def after_publish(source, destination):
            nonlocal fired
            result = real_replace(source, destination)
            if not fired:
                fired = True
                raise KeyboardInterrupt
            return result
        with patch("quality.evidence.os.replace", after_publish):
            state = self.receive_local(plan, envelope)
        self.assertTrue(state["original"])
        self.assertEqual(state["report"]["overall"], "incomplete")
        _, stored = load(self.fx.state, plan["plan_id"])
        self.assertEqual(stored["original"], state["original"])

    def test_known_failure_survives_save_before_and_after_publication(self):
        from quality.evidence import SaveFailure
        for phase in ("file-sync", "replace", "sync", "cleanup"):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, 7)
            if phase == "file-sync":
                manager = patch("quality.evidence.os.fsync", side_effect=OSError("invented before publication fsync"))
            elif phase == "replace":
                manager = patch("quality.evidence.os.replace", side_effect=OSError("invented before publication"))
            elif phase == "sync":
                manager = patch("quality.evidence.sync_directory", side_effect=OSError("invented after publication"))
            else:
                manager = patch("quality.evidence.Path.unlink", side_effect=OSError("invented temporary cleanup"))
            outcome = ImportOutcome()
            with manager:
                state = self.receive_local(plan, envelope, outcome=outcome)
            self.assertEqual(state["report"]["overall"], "fail")
            self.assertTrue(outcome.failure)
            if phase == "cleanup":
                self.assertIn("temporary-cleanup-unconfirmed", state["request_gaps"])
            else:
                self.assertIn("state-persistence-unconfirmed", state["request_gaps"])
            _, stored = load(self.fx.state, plan["plan_id"])
            self.assertEqual(bool(stored["failure"]), phase not in ("replace", "file-sync"))

    def test_unbound_or_mismatched_request_cannot_activate_known_failure(self):
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan, 7)
        envelope["records"][0]["consumed"]["origin_tree"] = "f"*40
        state = self.receive_local(plan, envelope)
        self.assertEqual(state["report"]["overall"], "incomplete")
        self.assertFalse(state["failure"])
        envelope, _ = self.fx.facts(plan, 7)
        self.receive_local(plan, envelope)
        outcome = ImportOutcome()
        wrong = {key: plan["context"][key] for key in ("repository", "base", "head", "artifact_sha256", "toolkit_source")}
        wrong["head"] = "f"*40
        with self.assertRaises(Invalid):
            receive(self.fx.state, plan["plan_id"], Git(self.fx.repo), plan["context"], plan["registry"], self.fx.clock(plan),
                    [self.fx.repo,self.fx.cache,self.fx.state], request=wrong, outcome=outcome)
        self.assertIsNone(outcome.state)
        self.assertIsNone(outcome.failure)

    def test_changed_unpersisted_recovery_report_marks_durability_gap(self):
        plan = self.fx.plan()
        envelope, _ = self.fx.facts(plan, 7)
        outcome = ImportOutcome()
        self.receive_local(plan, envelope, outcome=outcome)
        self.assertTrue(outcome.durable)
        before = (self.fx.state/plan["plan_id"]/"record.json").read_bytes()
        state = outcome.recover("report-output-unavailable", persist=False)
        self.assertFalse(outcome.durable)
        self.assertIn("state-persistence-unconfirmed", state["request_gaps"])
        self.assertEqual(state["report"]["overall"], "fail")
        self.assertEqual((self.fx.state/plan["plan_id"]/"record.json").read_bytes(), before)

    def test_actual_package_cli_final_clock_interrupt_exit_not_just_retry(self):
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, code)
            inputs = self.fx.inputs(envelope, None)
            package = self.fx.cache/(self.digest+".pyz")
            argv = [str(package),"import","--repo",str(self.fx.repo),"--base",self.fx.base,"--head",self.fx.head,
                    "--identity","example/invented","--state",str(self.fx.state),"--artifact-sha256",self.digest,
                    "--source",self.source,"--trusted-head",self.fx.head,"--plan",plan["plan_id"],*inputs]
            driver = self.fx.root/("fault-"+str(code)+".py")
            driver.write_text("""import sys
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from quality.external_cli import main
from quality.external_store import receive as actual_receive
sys.argv=sys.argv[1:]
def interrupted(): raise KeyboardInterrupt
def invoke(*args,**kwargs):
    kwargs['final_clock']=interrupted
    return actual_receive(*args,**kwargs)
with patch('quality.external_cli.receive',invoke):
    raise SystemExit(main())
""")
            result = subprocess.run([sys.executable,"-I","-S",str(driver),*argv],env={"PATH":os.defpath,"LC_ALL":"C"},capture_output=True,text=True,timeout=30)
            output = parse_json(result.stdout.encode())
            self.assert_result(result, output, "fail" if code else "incomplete")
            self.assertIn("import-interrupted", [s["reason"] for s in output["report"]["stages"]][1])

    def test_actual_package_output_error_then_diagnostic_interrupt_retains_exit(self):
        for code in (0, 7):
            plan = self.fx.plan()
            envelope, _ = self.fx.facts(plan, code)
            inputs = self.fx.inputs(envelope, None)
            package = self.fx.cache/(self.digest+".pyz")
            argv = [str(package),"import","--repo",str(self.fx.repo),"--base",self.fx.base,"--head",self.fx.head,
                    "--identity","example/invented","--state",str(self.fx.state),"--artifact-sha256",self.digest,
                    "--source",self.source,"--trusted-head",self.fx.head,"--plan",plan["plan_id"],*inputs]
            driver = self.fx.root/("delivery-fault-"+str(code)+".py")
            driver.write_text("""import sys
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from quality.external_cli import main
sys.argv=sys.argv[1:]
with patch('quality.external_cli.emit',side_effect=OSError('invented output error')), patch('quality.external_cli.write_output',side_effect=KeyboardInterrupt):
    raise SystemExit(main())
""")
            result = subprocess.run([sys.executable,"-I","-S",str(driver),*argv],env={"PATH":os.defpath,"LC_ALL":"C"},capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,1 if code else 2,result.stderr)
            self.assertEqual(result.stdout,"")
            _,stored=load(self.fx.state,plan["plan_id"])
            self.assertEqual(stored["report"]["overall"],"fail" if code else "incomplete")


class ApprovedPathTests(ExternalCase):
    def test_hidden_receipt_and_observer_hops_do_not_consume_facts(self):
        a,b=self.fx.root/"outside-a",self.fx.root/"outside-b"
        for directory in (a,b):(directory/"subdir").mkdir(parents=True)
        hop=self.fx.repo/"traversal";hop.symlink_to(a/"subdir",target_is_directory=True)
        alias=self.fx.root/"outside-alias";alias.symlink_to(hop,target_is_directory=True)
        for role in ("--evidence","--observations"):
            for parent in (False,True):
                literal=alias/".."/"input.json" if parent else alias/"input.json"
                for destination in (a,b):
                    with self.subTest(role=role,parent=parent,destination=destination.name):
                        hop.unlink();hop.symlink_to(destination/"subdir",target_is_directory=True)
                        self.fx.head=self.fx.commit()
                        plan=self.fx.plan()
                        envelope,observer=self.fx.facts(plan,7 if role=="--evidence" else 0)
                        arguments=self.fx.inputs(envelope,None if role=="--evidence" else observer)
                        index=arguments.index(role)+1
                        selected=destination/"input.json" if parent else destination/"subdir/input.json"
                        selected.write_bytes(Path(arguments[index]).read_bytes())
                        arguments[index]=str(literal)
                        result,output=self.fx.run("import","--plan",plan["plan_id"],*arguments)
                        report=self.assert_result(result,output,"incomplete")
                        reasons=",".join(row["reason"] for row in report["stages"])
                        self.assertNotIn("current-subject-mismatch",reasons)
                        self.assertNotIn("source-moved",reasons)
                        self.assertIn("producer-input-unavailable-or-invalid" if role=="--evidence" else "controller-input-unavailable-or-invalid",reasons)
                        _,stored=load(self.fx.state,plan["plan_id"])
                        self.assertFalse(stored["failure"])
                        self.assertEqual(bool(stored["original"]),role=="--observations")
                        self.assertFalse(stored["observer"])

    def test_hidden_state_hop_refuses_before_plan_write(self):
        a,b=self.fx.root/"outside-a",self.fx.root/"outside-b"
        for directory in (a,b):(directory/"subdir").mkdir(parents=True)
        hop=self.fx.repo/"traversal";hop.symlink_to(a/"subdir",target_is_directory=True)
        alias=self.fx.root/"outside-alias";alias.symlink_to(hop,target_is_directory=True)
        for parent in (False,True):
            literal=alias/".."/"state" if parent else alias/"state"
            for destination in (a,b):
                hop.unlink();hop.symlink_to(destination/"subdir",target_is_directory=True)
                self.fx.head=self.fx.commit()
                result,output=self.fx.run("doctor","--state",str(literal))
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertIsNone(output)
                self.assertFalse((destination/"state").exists())
                self.assertFalse((destination/"subdir/state").exists())

    def test_default_issuance_and_final_clock_keep_original_subject_roots(self):
        plan=self.fx.plan();clock=self.fx.clock(plan)
        observed=[]
        def checked_clock(*,protected_roots):
            observed.append(protected_roots)
            return clock
        with patch("quality.external_store.read_clock",side_effect=checked_clock):
            create(self.fx.state,plan["context"],plan["registry"],clock,protected_roots=[self.fx.repo])
            receive(self.fx.state,plan["plan_id"],Git(self.fx.repo),plan["context"],plan["registry"],clock,
                    [self.fx.repo,self.fx.cache,self.fx.state])
        self.assertEqual(observed,[[self.fx.repo],[self.fx.repo]])
        before=set(self.fx.state.iterdir())
        with self.assertRaises(Invalid):
            create(self.fx.state,plan["context"],plan["registry"],clock,protected_roots=[])
        self.assertEqual(set(self.fx.state.iterdir()),before)

    def test_hidden_receipt_refusal_retains_previously_validated_failure(self):
        directory=self.fx.root/"outside";(directory/"subdir").mkdir(parents=True)
        hop=self.fx.repo/"traversal";hop.symlink_to(directory/"subdir",target_is_directory=True)
        self.fx.head=self.fx.commit()
        alias=self.fx.root/"outside-alias";alias.symlink_to(hop,target_is_directory=True)
        plan=self.fx.plan();envelope,_=self.fx.facts(plan,7)
        result,output=self.fx.receive(plan,envelope,None)
        self.assert_result(result,output,"fail")
        _,before=load(self.fx.state,plan["plan_id"])
        for parent in (False,True):
            arguments=self.fx.inputs(envelope,None)
            target=directory/"receipt.json" if parent else directory/"subdir/receipt.json"
            target.write_bytes(Path(arguments[1]).read_bytes())
            arguments[1]=str(alias/".."/"receipt.json" if parent else alias/"receipt.json")
            result,output=self.fx.run("import","--plan",plan["plan_id"],*arguments)
            report=self.assert_result(result,output,"fail")
            self.assertTrue(any("producer-input-unavailable-or-invalid" in row["reason"] for row in report["stages"]))
            _,after=load(self.fx.state,plan["plan_id"])
            self.assertEqual(after["failure"],before["failure"])
            self.assertEqual(after["original"],before["original"])

    def test_archive_and_receipt_terminal_links_remain_refused(self):
        archive=self.fx.root/"archive-alias.pyz";archive.symlink_to(self.package)
        cache=self.fx.root/"new-cache"
        result=self.fx.command("install","--artifact",str(archive),"--sha256",self.digest,"--source",self.source,"--cache",str(cache))
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(cache.exists())
        plan=self.fx.plan();envelope,_=self.fx.facts(plan,7)
        arguments=self.fx.inputs(envelope,None)
        link=self.fx.root/"receipt-alias.json";link.symlink_to(Path(arguments[1]));arguments[1]=str(link)
        result,output=self.fx.run("import","--plan",plan["plan_id"],*arguments)
        self.assert_result(result,output,"incomplete")
        _,stored=load(self.fx.state,plan["plan_id"])
        self.assertFalse(stored["original"])
        self.assertFalse(stored["failure"])

    def test_actual_archive_clock_defaults_refuse_hidden_helper_at_each_phase(self):
        import shlex
        outside=self.fx.root/"outside";(outside/"subdir").mkdir(parents=True)
        marker=self.fx.root/"clock-marker"
        body=outside/"subdir/helper.py";body.write_text("from pathlib import Path\nPath("+repr(str(marker))+").touch()\nraise SystemExit(9)\n")
        helper=outside/"subdir/helper";helper.write_text("#!/bin/sh\nexec "+shlex.quote(str(Path(sys.executable).resolve()))+" -I -S "+shlex.quote(str(body))+" \"$@\"\n");helper.chmod(0o700)
        hop=self.fx.repo/"traversal";hop.symlink_to(outside/"subdir",target_is_directory=True)
        self.fx.head=self.fx.commit()
        alias=self.fx.root/"outside-alias";alias.symlink_to(hop,target_is_directory=True)
        unsafe=alias/"helper"
        for phase in ("initial","issuance","final"):
            with self.subTest(phase=phase):
                extra=[]
                if phase=="final":
                    plan=self.fx.plan();envelope,_=self.fx.facts(plan,7)
                    result,output=self.fx.receive(plan,envelope,None)
                    self.assert_result(result,output,"fail")
                    extra=["--plan",plan["plan_id"],*self.fx.inputs(envelope,None)]
                package=self.fx.cache/(self.digest+".pyz")
                command="import" if phase=="final" else "doctor"
                argv=[str(package),command,"--repo",str(self.fx.repo),"--base",self.fx.base,"--head",self.fx.head,
                      "--identity","example/invented","--state",str(self.fx.state),"--artifact-sha256",self.digest,
                      "--source",self.source,"--trusted-head",self.fx.head,*extra]
                driver=self.fx.root/("clock-"+phase+".py")
                driver.write_text("""import sys
from pathlib import Path
from unittest.mock import patch
package,unsafe,phase=sys.argv[1:4]
sys.path.insert(0,package)
from quality.external_cli import main
import quality.external_clock as clock
sys.argv=[package,*sys.argv[4:]]
calls=0
selected_unsafe=False
def selected(value):
    global calls,selected_unsafe
    if value=='/usr/sbin/sysctl':
        calls+=1
        if calls==(1 if phase=='initial' else 2):
            selected_unsafe=True
            return Path(unsafe)
    return Path(value)
with patch.object(clock.sys,'platform','darwin'),patch.object(clock,'Path',side_effect=selected):
    try: code=main()
    except SystemExit as exc: code=exc.code
    assert selected_unsafe,'unsafe clock selector injection was not reached'
    raise SystemExit(code)
""")
                result=subprocess.run([sys.executable,"-I","-S",str(driver),str(package),str(unsafe),phase,*argv[1:]],capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,1 if phase=="final" else 2,result.stderr)
                self.assertFalse(marker.exists(),"unsafe clock helper executed")
                if phase=="final":
                    output=parse_json(result.stdout.encode())
                    self.assertEqual(output["report"]["overall"],"fail")
                    self.assertTrue(any("final-clock-unavailable" in row["reason"] for row in output["report"]["stages"]))
