from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from quality.schema import checked
from quality_trust import canonical, parse_json, sha
from tests.support import BOUNDARY, Fixture, ROOT

BLOCKER = {"id": "f-1", "severity": "blocker", "disposition": "open", "location": "check.py:1",
           "scenario": "An invented required input is empty.", "consequence": "The required operation crashes.",
           "recommendation": "Validate the input before use.", "resolution": ""}


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name))

    def status(self, report: dict, name: str) -> str:
        return next(item["status"] for item in report["stages"] if item["id"] == name)

    def test_complete_check_and_independent_attestation_pass(self) -> None:
        result, report = self.fx.reviewed()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["overall"], "pass")
        self.assertEqual(report["review"]["evidence_kind"], "external-attestation")
        checked("report", report)
        self.assertEqual(report["effective_plan"], self.fx.config)
        self.assertEqual(self.fx.git("status", "--porcelain"), "")
        paths = list(self.fx.state.glob("*/report.json"))
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(paths[0].parent.stat().st_mode & 0o777, 0o700)

    def test_unknown_provenance_and_missing_reviewer_are_incomplete(self) -> None:
        result, report = self.fx.check()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.status(report, "check:unit"), "incomplete")
        self.assertEqual(self.status(report, "review:independent"), "incomplete")
        self.assertFalse(list(self.fx.state.glob("*/snapshot-*")))

    def test_unavailable_isolation_cannot_be_authorized_by_flag(self) -> None:
        self.fx.config["execution"]["isolation"] = "unavailable"
        self.fx.accept()
        result, report = self.fx.reviewed()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.status(report, "check:unit"), "incomplete")

    def test_required_failure_wins_over_missing_review(self) -> None:
        self.fx.write("check.py", "raise SystemExit(7)\n")
        self.fx.head = self.fx.commit()
        result, report = self.fx.check("--execute-trusted")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["overall"], "fail")
        self.assertEqual(self.status(report, "review:independent"), "incomplete")

    def test_head_cannot_select_config_lock_or_bootstrap(self) -> None:
        marker = self.fx.root / "unauthorized"
        self.fx.write("check.py", "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        self.fx.write(".quality/config.json", '{"schema_version":999,"execution":"bypass"}')
        self.fx.write(".quality/lock.json", '{"artifact_sha256":"wrong"}')
        self.fx.write("quality_launch.py", "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        self.fx.head = self.fx.commit()
        result, report = self.fx.check()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())
        self.assertEqual(report["effective_plan"], self.fx.config)
        self.assertEqual(report["context"]["artifact_sha256"], self.fx.digest)

    def test_changed_script_uses_explicit_trusted_local_gate(self) -> None:
        self.fx.write("check.py", "raise SystemExit(9)\n")
        self.fx.head = self.fx.commit()
        _, report = self.fx.check()
        self.assertEqual(self.status(report, "check:unit"), "incomplete")
        result, report = self.fx.check("--execute-trusted")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.status(report, "check:unit"), "fail")

    def test_command_environment_drops_credentials_and_redirects_roots(self) -> None:
        self.fx.write("check.py", """import os
from pathlib import Path
assert 'EXAMPLE_SECRET' not in os.environ
assert 'SSH_AUTH_SOCK' not in os.environ
assert 'PYTHONPATH' not in os.environ
root = Path(os.environ['QUALITY_STATE_ROOT'])
for key in ('HOME', 'TMPDIR', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME'):
    assert Path(os.environ[key]).is_relative_to(root)
Path(os.environ['HOME'], 'only-disposable').write_text('invented')
""")
        self.fx.head = self.fx.commit()
        result, report = self.fx.check("--execute-trusted", extra_env={"EXAMPLE_SECRET": "invented-sensitive-value", "SSH_AUTH_SOCK": "/invented/socket"})
        self.assertEqual(self.status(report, "check:unit"), "pass", result.stderr)
        self.assertNotIn("invented-sensitive-value", json.dumps(report) + result.stdout + result.stderr)

    def test_dirty_checkout_and_moving_head_invalidate_source(self) -> None:
        self.fx.write("untracked.txt", "invented dirty state")
        _, report = self.fx.reviewed()
        self.assertEqual(self.status(report, "source"), "incomplete")
        (self.fx.repo / "untracked.txt").unlink()
        old = self.fx.head
        self.fx.write("check.py", "import subprocess\nsubprocess.run(['git','-C'," + repr(str(self.fx.repo)) + ",'update-ref','HEAD'," + repr(old) + "],check=True)\n")
        self.fx.head = self.fx.commit()
        _, report = self.fx.reviewed()
        self.assertEqual(self.status(report, "source"), "incomplete")
        self.assertEqual(report["source_after"]["head"], old)

    def test_timeout_and_bounded_log_are_incomplete(self) -> None:
        self.fx.config["execution"]["checks"][0]["timeout_seconds"] = 1
        self.fx.write("check.py", "import threading\nthreading.Event().wait(30)\n")
        self.fx.accept()
        _, report = self.fx.check("--execute-trusted")
        self.assertEqual(self.status(report, "check:unit"), "incomplete")
        self.assertTrue(any(s["reason"] == "command-timeout" for s in report["stages"]))
        self.fx.write("check.py", "print('x' * 10000)\n")
        self.fx.head = self.fx.commit()
        _, report = self.fx.check("--execute-trusted")
        self.assertTrue(any(s["reason"] == "command-log-limit" for s in report["stages"]))
        self.assertLessEqual(max(p.stat().st_size for p in self.fx.state.glob("*/unit.log")), 4096)

    def test_snapshot_mutation_is_incomplete_and_checks_get_fresh_sources(self) -> None:
        first = self.fx.config["execution"]["checks"][0]
        first["argv"] = [sys.executable, "-I", "-S", "mutate.py"]
        self.fx.write("mutate.py", "from pathlib import Path\nPath('check.py').write_text('raise SystemExit(8)\\n')\n")
        second = copy.deepcopy(first)
        second["id"] = "second"
        second["argv"] = [sys.executable, "-I", "-S", "check.py"]
        self.fx.config["execution"]["checks"].append(second)
        self.fx.accept()
        _, report = self.fx.reviewed()
        self.assertEqual(self.status(report, "snapshot:unit"), "incomplete")
        self.assertEqual(self.status(report, "check:second"), "pass")
        self.assertEqual(self.status(report, "snapshot:second"), "pass")
        self.assertEqual(report["overall"], "incomplete")

    def test_definite_failure_survives_descendant_pipe_timeout(self) -> None:
        self.fx.config["execution"]["checks"][0]["timeout_seconds"] = 1
        self.fx.write("check.py", "import subprocess,sys\nsubprocess.Popen([sys.executable,'-I','-S','-c','import threading;threading.Event().wait(30)'])\nraise SystemExit(7)\n")
        self.fx.accept()
        result, report = self.fx.check("--execute-trusted")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.status(report, "check:unit"), "fail")
        self.assertEqual(self.status(report, "output:unit"), "incomplete")
        self.assertEqual(report["overall"], "fail")

    def test_missing_command_and_unsupported_snapshot_incomplete(self) -> None:
        self.fx.config["execution"]["checks"][0]["argv"] = ["/invented/missing-command"]
        self.fx.accept()
        result, report = self.fx.reviewed()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.status(report, "check:unit"), "incomplete")
        (self.fx.repo / "link").symlink_to("check.py")
        self.fx.head = self.fx.commit()
        _, report = self.fx.check("--execute-trusted")
        self.assertTrue(any(s["reason"] == "snapshot-entry-unsupported" for s in report["stages"]))

    def test_config_unknown_fields_invalid_schema_and_identity_refused(self) -> None:
        for mutation in (lambda c: c.update(unknown=True), lambda c: c.update(schema_version=2),
                         lambda c: c.update(repository="example/other")):
            with self.subTest(mutation=mutation):
                config = copy.deepcopy(self.fx.config)
                mutation(config)
                self.fx.write(".quality/config.json", json.dumps(config))
                self.fx.base = self.fx.head = self.fx.commit()
                self.assertEqual(self.fx.launch(*self.fx.command()).returncode, 2)

    def test_adapter_uses_accepted_pin_and_cannot_override_artifact(self) -> None:
        base = [sys.executable, "-I", "-S", str(ROOT / "adapters/quality.py"), "--launcher",
                str(ROOT / "quality_launch.py"), "--python", sys.executable]
        result = subprocess.run([*base, *self.fx.command("doctor")], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn(self.fx.digest, result.stdout)
        bypass = subprocess.run([*base, *self.fx.command(), "--artifact", str(self.fx.package)], capture_output=True, text=True)
        self.assertEqual(bypass.returncode, 2)
        incompatible = self.fx.launch("--adapter-protocol", "2", *self.fx.command())
        self.assertEqual(incompatible.returncode, 2)

    def test_interruption_persists_incomplete_and_releases_lock(self) -> None:
        self.fx.write("check.py", "import os,threading\nfrom pathlib import Path\nPath(os.environ['QUALITY_STATE_ROOT'],'ready').touch()\nthreading.Event().wait(30)\n")
        self.fx.head = self.fx.commit()
        # Invoke the package directly: the process being interrupted owns the run.
        args = self.fx.command("check", "--execute-trusted")
        cache_index = args.index("--cache")
        del args[cache_index:cache_index + 2]
        package = self.fx.cache / (self.fx.digest + ".pyz")
        command = [sys.executable, "-I", "-S", str(package), *args,
                   "--artifact-sha256", self.fx.digest, "--source", self.fx.source]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            deadline = time.monotonic() + 10
            while not list(self.fx.state.glob("*/state-unit/ready")):
                if process.poll() is not None or time.monotonic() > deadline:
                    process.kill()
                    self.fail("owned fixture did not start")
                time.sleep(0.01)
            busy = self.fx.launch(*self.fx.command("doctor"))
            self.assertEqual(busy.returncode, 2)
            self.assertIn("target-run-already-active", busy.stderr)
            process.send_signal(signal.SIGTERM)
            _, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 2, stderr)
        report = parse_json(next(self.fx.state.glob("*/report.json")).read_bytes())
        self.assertEqual(report["overall"], "incomplete")
        self.assertTrue(any(s["reason"] == "run-interrupted" for s in report["stages"]))
        result, _ = self.fx.check(mode="doctor")
        self.assertEqual(result.returncode, 2)

    def test_initial_report_survives_hard_termination(self) -> None:
        self.fx.write("check.py", "import os\nos.kill(os.getppid(), 9)\n")
        self.fx.head = self.fx.commit()
        result, report = self.fx.check("--execute-trusted")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report["overall"], "incomplete")
        self.assertEqual(report["finished_at"], "")

    def test_launcher_forwards_handled_termination(self) -> None:
        self.fx.write("check.py", "import os,threading\nfrom pathlib import Path\nPath(os.environ['QUALITY_STATE_ROOT'],'ready').touch()\nthreading.Event().wait(30)\n")
        self.fx.head = self.fx.commit()
        command = [sys.executable, "-I", "-S", str(ROOT / "quality_launch.py"), *self.fx.command("check", "--execute-trusted")]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            deadline = time.monotonic() + 10
            while not list(self.fx.state.glob("*/state-unit/ready")):
                if process.poll() is not None or time.monotonic() > deadline:
                    process.kill()
                    self.fail("fixture did not start through launcher")
                time.sleep(0.01)
            process.terminate()
            _, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 2, stderr)
        report = parse_json(next(self.fx.state.glob("*/report.json")).read_bytes())
        self.assertEqual(report["overall"], "incomplete")
        self.assertTrue(any(s["reason"] == "run-interrupted" for s in report["stages"]))

    def test_handled_cancellation_keeps_observed_command_failure(self) -> None:
        self.fx.write("check.py", "import os,subprocess,sys\nfrom pathlib import Path\nsubprocess.Popen([sys.executable,'-I','-S','-c','import threading;threading.Event().wait(30)'])\nPath(os.environ['QUALITY_STATE_ROOT'],'parent-pid').write_text(str(os.getpid()))\nraise SystemExit(7)\n")
        self.fx.head = self.fx.commit()
        command = [sys.executable, "-I", "-S", str(ROOT / "quality_launch.py"), *self.fx.command("check", "--execute-trusted")]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            deadline = time.monotonic() + 10
            while True:
                markers = list(self.fx.state.glob("*/state-unit/parent-pid"))
                if markers:
                    try:
                        os.kill(int(markers[0].read_text()), 0)
                    except ProcessLookupError:
                        break
                if process.poll() is not None or time.monotonic() > deadline:
                    process.kill()
                    self.fail("fixture parent did not exit and get observed")
                time.sleep(0.01)
            process.terminate()
            _, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 1, stderr)
        report = parse_json(next(self.fx.state.glob("*/report.json")).read_bytes())
        self.assertEqual(self.status(report, "check:unit"), "fail")
        self.assertEqual(self.status(report, "output:unit"), "incomplete")
        self.assertEqual(report["overall"], "fail")
