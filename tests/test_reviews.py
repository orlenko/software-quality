from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from tests.support import BOUNDARY, Fixture
from tests.test_runner import BLOCKER


class ReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name))
        self.fx.config["reviewer"]["routes"].append({"id": "second", "reviewer_id": "example-second", "boundary": BOUNDARY})
        self.fx.accept()
        _, self.initial = self.fx.check(mode="doctor")

    def records(self) -> list[dict]:
        return [{"route_id": r["id"], "reviewer_id": r["reviewer_id"], "independent": True,
                 "boundary": copy.deepcopy(r["boundary"]), "findings": [], "summary": "Invented independent replay."}
                for r in self.fx.config["reviewer"]["routes"]]

    def check_records(self, records: list, **updates: object) -> tuple[object, dict]:
        path, digest = self.fx.response(self.initial, reviews=records, **updates)
        return self.fx.check("--execute-trusted", "--review", path, "--review-sha256", digest)

    def test_two_required_routes_pass_and_missing_route_incomplete(self) -> None:
        result, report = self.check_records(self.records())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(report["review"]["records"]), 2)
        result, _ = self.check_records(self.records()[:1])
        self.assertEqual(result.returncode, 2)

    def test_invalid_other_route_does_not_erase_valid_blocker(self) -> None:
        records = self.records()
        records[0]["findings"] = [BLOCKER]
        records[1]["independent"] = False
        result, report = self.check_records(records)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["overall"], "fail")
        self.assertTrue(any(s["status"] == "incomplete" for s in report["stages"]))

    def test_duplicates_unknown_and_malformed_do_not_erase_blocker(self) -> None:
        records = self.records()
        records[0]["findings"] = [BLOCKER]
        for extra in (self.records()[0], {"route_id": "unknown"}, {"route_id": []}, ["malformed"], None):
            with self.subTest(extra=extra):
                result, report = self.check_records([*records, extra])
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(report["overall"], "fail")
        result, _ = self.check_records([*self.records(), self.records()[0]])
        self.assertEqual(result.returncode, 2)

    def test_mismatched_boundary_identity_and_context_incomplete(self) -> None:
        for key, value in (("reviewer_id", "wrong"), ("boundary", {**BOUNDARY, "network": True}), ("independent", False)):
            records = self.records()
            records[0][key] = value
            result, _ = self.check_records(records)
            self.assertEqual(result.returncode, 2)
        context = {**self.initial["context"], "head": "2" * 40}
        result, _ = self.check_records(self.records(), context=context)
        self.assertEqual(result.returncode, 2)

    def test_unknown_extra_record_without_blocker_incomplete(self) -> None:
        result, _ = self.check_records([*self.records(), {"route_id": "unknown"}])
        self.assertEqual(result.returncode, 2)

    def test_head_cannot_remove_required_route(self) -> None:
        import json
        head_config = copy.deepcopy(self.fx.config)
        head_config["reviewer"]["routes"].pop()
        self.fx.write(".quality/config.json", json.dumps(head_config))
        self.fx.head = self.fx.commit()
        _, self.initial = self.fx.check(mode="doctor")
        result, report = self.check_records(self.records()[:1])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(report["effective_plan"]["reviewer"]["routes"]), 2)

    def test_review_digest_and_outside_target_provenance_required(self) -> None:
        path, digest = self.fx.response(self.initial)
        result, _ = self.fx.check("--execute-trusted", "--review", path, "--review-sha256", "0" * 64)
        self.assertEqual(result.returncode, 2)
        target = self.fx.repo / "response.json"
        target.write_bytes(Path(path).read_bytes())
        result, _ = self.fx.check("--execute-trusted", "--review", str(target), "--review-sha256", digest)
        self.assertEqual(result.returncode, 2)

    def test_distinct_identities_and_duplicate_routes_rejected(self) -> None:
        self.fx.config["reviewer"]["routes"][1]["reviewer_id"] = "example-independent"
        self.fx.accept()
        result = self.fx.launch(*self.fx.command())
        self.assertEqual(result.returncode, 2)
        self.assertIn("distinct-reviewer-identities-required", result.stderr)

    def test_resolved_findings_require_recorded_resolution(self) -> None:
        records = self.records()
        records[0]["findings"] = [{**BLOCKER, "disposition": "resolved", "resolution": ""}]
        result, _ = self.check_records(records)
        self.assertEqual(result.returncode, 2)
        records[0]["findings"][0]["resolution"] = "Review of the bound target demonstrates the input guard."
        result, _ = self.check_records(records)
        self.assertEqual(result.returncode, 0)

    def test_invalid_json_review_is_incomplete(self) -> None:
        from quality_trust import sha
        path = self.fx.root / "invalid-review.json"
        data = b'{"schema_version":'
        path.write_bytes(data)
        result, report = self.fx.check("--execute-trusted", "--review", str(path), "--review-sha256", sha(data))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["overall"], "incomplete")

    def test_later_review_interruption_keeps_validated_blocker(self) -> None:
        from argparse import Namespace
        from contextlib import redirect_stdout
        import io
        from unittest.mock import patch
        from quality.runner import run
        from quality.schema import checked
        records = self.records()
        records[0]["findings"] = [BLOCKER]
        path, digest = self.fx.response(self.initial, reviews=records)
        args = Namespace(repo=self.fx.repo, state=self.fx.state, base=self.fx.base, head=self.fx.head,
                         identity="example/demo", command="check", execute_trusted=False,
                         review=Path(path), review_sha256=digest)
        seen = 0
        def interrupt_later(name: str, value: object) -> object:
            nonlocal seen
            if name == "review-record":
                seen += 1
                if seen == 2:
                    raise KeyboardInterrupt
            return checked(name, value)
        with patch("quality.runner.checked", side_effect=interrupt_later), redirect_stdout(io.StringIO()):
            report, _ = run(args, self.fx.digest, self.fx.source, True)
        self.assertEqual(report["overall"], "fail")
        self.assertTrue(any(s["id"] == "review:independent" and s["status"] == "fail" for s in report["stages"]))
