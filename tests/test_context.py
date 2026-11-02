from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
import tempfile
import unittest

import tests
from quality_trust import parse_json
from tests.support import Fixture, ROOT

FAKE_GH = """import json,os,subprocess,sys,threading
from pathlib import Path
root=Path(os.environ['GH_CONFIG_DIR'])
spec=json.loads((root/'responses.json').read_text())
counter=root/'counter.txt'
number=int(counter.read_text())+1 if counter.exists() else 1
counter.write_text(str(number))
with (root/'calls.jsonl').open('a') as stream:
    stream.write(json.dumps({'argv':sys.argv[1:],'env':dict(os.environ)})+'\\n')
if number==spec.get('mutate_at'):
    subprocess.run(spec['mutate_argv'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if number==spec.get('fail_at'):
    raise SystemExit(5)
if number==spec.get('helper_at'):
    child=subprocess.Popen([sys.executable,'-I','-S','-c','import threading;threading.Event().wait(30)'])
    (root/'helper-pid').write_text(str(child.pid))
    (root/'metadata-ready').touch()
if number==spec.get('overflow_at'):
    sys.stdout.write('x'*(2*1024*1024+65536))
    sys.stdout.flush()
if number==spec.get('wait_at'):
    threading.Event().wait(30)
items=spec['responses']
print(json.dumps(items[min(number-1,len(items)-1)]))
"""


class ContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name))
        self.directory = tests.ADAPTER_ROOT or ROOT / "adapters"
        self.frontend = self.directory / ("bin/quality_context.py" if tests.ADAPTER_ROOT else "quality_context.py")
        self.config = self.fx.root / "metadata-auth"
        self.config.mkdir()
        self.gh = self.fx.root / "approved-gh"
        program = self.fx.root / "fake_metadata.py"
        program.write_text(FAKE_GH)
        self.gh.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + " -I -S " + shlex.quote(str(program)) + ' "$@"\n')
        self.gh.chmod(0o700)

    def pr(self, **changes: object) -> dict:
        value = {"number": 7, "state": "open", "base_repository": "example/demo", "base": self.fx.base,
                 "head_repository": "example/demo", "head": self.fx.head,
                 "head_ref": self.fx.git("symbolic-ref", "--short", "HEAD")}
        value.update(changes)
        return value

    def responses(self, values: list, **changes: object) -> None:
        (self.config / "responses.json").write_text(json.dumps({"responses": values, **changes}))
        for name in ("counter.txt", "calls.jsonl", "helper-pid", "metadata-ready"):
            (self.config / name).unlink(missing_ok=True)

    def command(self, *extra: str, explicit: bool = False, personal: bool = True) -> list[str]:
        command = [sys.executable, "-I", "-S", str(self.frontend), "--launcher", str(ROOT / "quality_launch.py"),
                   "--python", sys.executable, "--repo", str(self.fx.repo), "--identity", "example/demo",
                   "--base", self.fx.base, "--cache", str(self.fx.cache), "--state", str(self.fx.state)]
        if explicit:
            command.extend(["--head", self.fx.head])
        else:
            command.extend(["--github-cli", str(self.gh), "--github-config", str(self.config), "--allow-github-metadata"])
        if personal:
            command.append("--personal")
        return [*command, *extra]

    def invoke(self, *extra: str, explicit: bool = False, personal: bool = True, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(self.command(*extra, explicit=explicit, personal=personal), env={"PATH": os.defpath, **(env or {})}, capture_output=True, text=True, timeout=20)
        rows = [line[len("context "):] for line in result.stdout.splitlines() if line.startswith("context ")]
        if not rows:
            self.fail(result.stderr)
        return result, json.loads(rows[-1])

    def assert_helper_stopped(self) -> None:
        pid = int((self.config / "helper-pid").read_text())
        deadline = time.monotonic() + 5
        while True:
            result = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True,
                                    env={"PATH": os.defpath}, timeout=2)
            if result.returncode or not result.stdout.strip() or result.stdout.strip().startswith("Z"):
                return
            if time.monotonic() >= deadline:
                self.fail("owned metadata helper remained alive")
            time.sleep(0.01)

    def latest(self) -> dict:
        path = max(self.fx.state.glob("*/report.json"), key=lambda p: p.stat().st_mtime_ns)
        return parse_json(path.read_bytes())

    def test_offline_explicit_fallback_equivalent_to_core(self) -> None:
        _, direct = self.fx.check(mode="doctor")
        result, receipt = self.invoke(explicit=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["context_status"], "complete")
        self.assertEqual(receipt["pr_freshness"], "not-requested")
        self.assertEqual(direct["context"], self.latest()["context"])
        self.assertFalse((self.config / "calls.jsonl").exists())

    def test_explicit_pr_plan_uses_fixed_host_and_controlled_auth(self) -> None:
        self.responses([self.pr()])
        result, receipt = self.invoke("--pr", "7", env={"GH_HOST": "evil.invalid", "GH_CONFIG_DIR": str(self.fx.repo),
            "GH_TOKEN": "invented-token", "GH_DEBUG": "api", "HTTPS_PROXY": "https://proxy.invalid"})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["context_status"], "complete")
        self.assertEqual(receipt["pr_freshness"], "stable-observed")
        calls = [json.loads(line) for line in (self.config / "calls.jsonl").read_text().splitlines()]
        self.assertEqual(len(calls), 3)
        for call in calls:
            self.assertEqual(call["env"]["GH_HOST"], "github.com")
            self.assertEqual(call["env"]["GH_CONFIG_DIR"], str(self.config.resolve()))
            self.assertTrue(all(name not in call["env"] for name in ("GH_TOKEN", "GH_DEBUG", "HTTPS_PROXY")))
            self.assertEqual(call["env"]["GH_TELEMETRY"], "false")
            self.assertEqual(call["env"]["GH_NO_UPDATE_NOTIFIER"], "1")
            self.assertIn("repos/example/demo/pulls/7", call["argv"])
            self.assertEqual(call["argv"][call["argv"].index("--method") + 1], "GET")

    def test_wrong_repository_and_absent_local_object_refused(self) -> None:
        for record in (self.pr(base_repository="example/other"), self.pr(head="2" * 40)):
            self.responses([record])
            result, receipt = self.invoke("--pr", "7")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(receipt["context_status"], "incomplete")
            self.assertIsNone(receipt["core_exit"])

    def test_missing_prerequisite_or_permission_does_not_launch(self) -> None:
        self.responses([self.pr()])
        result, receipt = self.invoke("--pr", "7", "--github-cli", str(self.fx.root / "missing"))
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(receipt["core_exit"])
        self.assertFalse((self.config / "calls.jsonl").exists())
        result, receipt = self.invoke("--pr", "7", explicit=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("approved-metadata-route", receipt["reason"])

    def test_current_pr_ambiguous_missing_truncated_or_fork_refused(self) -> None:
        for candidates in ([], [self.pr(), self.pr(number=8)], [self.pr()] * 100, [self.pr(head_repository="example/fork")]):
            self.responses([candidates])
            result, receipt = self.invoke("--current-pr")
            self.assertEqual(result.returncode, 2)
            self.assertIsNone(receipt["core_exit"])

    def test_current_pr_and_local_branch_stability(self) -> None:
        record = self.pr()
        self.responses([[record], record, record, record])
        _, receipt = self.invoke("--current-pr")
        self.assertEqual(receipt["context_status"], "complete")
        self.fx.git("branch", "other")
        self.responses([[record], record, record, record], mutate_at=4,
                       mutate_argv=["git", "-C", str(self.fx.repo), "symbolic-ref", "HEAD", "refs/heads/other"])
        result, receipt = self.invoke("--current-pr")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["reason"], "local-branch-moved-after-launch")

    def test_current_branch_unicode_whitespace_is_preserved(self) -> None:
        branch = "topic\u00a0"
        self.fx.git("branch", branch)
        self.fx.git("symbolic-ref", "HEAD", "refs/heads/" + branch)
        wrong = self.pr(head_ref="topic")
        self.responses([[wrong], wrong])
        _, receipt = self.invoke("--current-pr")
        self.assertIsNone(receipt["core_exit"])
        record = self.pr(head_ref=branch)
        self.responses([[record], record, record, record])
        _, receipt = self.invoke("--current-pr")
        self.assertEqual(receipt["context_status"], "complete")
        self.assertEqual(receipt["target"]["local_ref"], "refs/heads/" + branch)
        call = json.loads((self.config / "calls.jsonl").read_text().splitlines()[0])
        self.assertIn("head=example:" + branch, call["argv"])

    def test_moving_pr_before_and_after_launch(self) -> None:
        original = self.pr()
        for responses, reason in (([original, self.pr(head="2" * 40)], "pr-moved-before-launch"),
                                  ([original, original, self.pr(base="2" * 40)], "pr-number-or-accepted-base-mismatch")):
            self.responses(responses)
            result, receipt = self.invoke("--pr", "7")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(receipt["reason"], reason)

    def test_closed_pr_and_changed_current_selection_refused(self) -> None:
        self.responses([self.pr(state="closed")])
        _, receipt = self.invoke("--pr", "7")
        self.assertIsNone(receipt["core_exit"])
        self.responses([[self.pr()], self.pr(head_ref="different")])
        _, receipt = self.invoke("--current-pr")
        self.assertEqual(receipt["reason"], "current-pr-changed-during-selection")

    def test_core_pass_with_stale_post_run_pr_is_incomplete(self) -> None:
        self.responses([self.pr()])
        self.invoke("--pr", "7")
        path, digest = self.fx.response(self.latest())
        record = self.pr()
        self.responses([record, record, self.pr(head="2" * 40)])
        result, receipt = self.invoke("--pr", "7", "--head", self.fx.head, "--action", "check", "--execute-trusted",
                                      "--review", path, "--review-sha256", digest)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["core_exit"], 0)
        self.assertEqual(receipt["context_status"], "incomplete")
        self.assertEqual(self.latest()["overall"], "pass")

    def test_metadata_never_authorizes_new_trusted_head(self) -> None:
        self.responses([self.pr()])
        result, receipt = self.invoke("--pr", "7", "--execute-trusted")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["reason"], "explicit-expected-head-required-for-trusted-pr-execution")
        self.assertFalse((self.config / "calls.jsonl").exists())

    def test_head_side_adapter_config_and_pin_do_not_choose_code(self) -> None:
        self.fx.write(".quality/config.json", '{"repository":"example/other"}')
        self.fx.write(".quality/lock.json", "{}")
        marker = self.fx.root / "head-adapter-marker"
        self.fx.write("quality_context.py", "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        self.fx.head = self.fx.commit()
        _, receipt = self.invoke(explicit=True)
        self.assertEqual(receipt["context_status"], "complete")
        self.assertEqual(self.latest()["context"]["artifact_sha256"], self.fx.digest)
        self.assertFalse(marker.exists())

    def test_target_side_trusted_paths_are_refused(self) -> None:
        self.responses([self.pr()])
        executable = self.fx.repo / "gh"
        executable.symlink_to(self.gh)
        result, receipt = self.invoke("--pr", "7", "--github-cli", str(executable))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["reason"], "approved-path-must-be-outside-target")
        self.assertFalse((self.config / "calls.jsonl").exists())

    def test_success_and_core_failure_keep_separate_context_status(self) -> None:
        self.responses([self.pr()])
        self.invoke("--pr", "7")
        path, digest = self.fx.response(self.latest())
        result, receipt = self.invoke("--pr", "7", "--head", self.fx.head, "--action", "check", "--execute-trusted",
                                      "--review", path, "--review-sha256", digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(receipt["core_exit"], 0)
        self.fx.write("check.py", "raise SystemExit(7)\n")
        self.fx.head = self.fx.commit()
        record = self.pr()
        self.responses([record, record, record], fail_at=3)
        result, receipt = self.invoke("--pr", "7", "--head", self.fx.head, "--action", "check", "--execute-trusted")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(receipt["core_exit"], 1)
        self.assertEqual(receipt["context_status"], "incomplete")

    def test_missing_eligibility_and_wrong_explicit_repository_incomplete(self) -> None:
        result, receipt = self.invoke("--identity", "example/other", explicit=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt["reason"], "accepted-repository-identity-mismatch")
        _, receipt = self.invoke(explicit=True, personal=False)
        self.assertEqual(receipt["reason"], "explicit-personal-eligibility-and-identity-required")

    def test_bundle_has_complete_shared_skill_resources(self) -> None:
        for name in ("quality", "cmd-quality"):
            skill = self.directory / "skills" / name / "SKILL.md"
            self.assertTrue(skill.is_file())
            self.assertTrue((skill.parent / "../../workflow.md").resolve().is_file())
        compatibility = json.loads((self.directory / "compatibility.json").read_text())
        self.assertEqual(compatibility["adapter_protocol"], 1)
        self.assertFalse(compatibility["installed_or_registered"])

    def test_partial_frontend_copy_is_incomplete_without_importing_other_code(self) -> None:
        directory = self.fx.root / "partial-bundle" / "bin"
        directory.mkdir(parents=True)
        script = directory / "quality_context.py"
        script.write_bytes(self.frontend.read_bytes())
        (directory / "quality.py").write_text("raise RuntimeError('must not import legacy shim')\n")
        result = subprocess.run([sys.executable, "-I", "-S", str(script), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("incomplete adapter resource closure", result.stderr)
        self.assertNotIn("RuntimeError", result.stderr)

    def test_metadata_stream_overflow_stops_owned_helper(self) -> None:
        self.responses([self.pr()], helper_at=1, overflow_at=1, wait_at=1)
        result, receipt = self.invoke("--pr", "7")
        self.assertEqual(receipt["reason"], "metadata-output-limit-use-explicit-ids")
        self.assertIsNone(receipt["core_exit"])
        self.assertLess(len(result.stdout), 10000)
        self.assert_helper_stopped()

    def test_metadata_timeout_stops_owned_helper(self) -> None:
        self.responses([self.pr()], helper_at=1, wait_at=1)
        _, receipt = self.invoke("--pr", "7", "--metadata-timeout", "1")
        self.assertEqual(receipt["reason"], "metadata-timeout-use-explicit-ids")
        self.assert_helper_stopped()

    def test_frontend_cancellation_stops_metadata_and_keeps_core_failure(self) -> None:
        for fail in (False, True):
            with self.subTest(core_failed=fail):
                extra = []
                if fail:
                    self.fx.write("check.py", "raise SystemExit(7)\n")
                    self.fx.head = self.fx.commit()
                    extra = ["--head", self.fx.head, "--action", "check", "--execute-trusted"]
                number = 3 if fail else 1
                self.responses([self.pr()], helper_at=number, wait_at=number)
                with subprocess.Popen(self.command("--pr", "7", *extra), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                    deadline = time.monotonic() + 10
                    while not (self.config / "metadata-ready").exists():
                        if process.poll() is not None or time.monotonic() >= deadline:
                            process.kill()
                            self.fail("metadata fixture did not reach cancellation point")
                        time.sleep(0.01)
                    process.terminate()
                    stdout, stderr = process.communicate(timeout=10)
                    self.assertEqual(process.returncode, 1 if fail else 2, stderr)
                receipt = json.loads([line[8:] for line in stdout.splitlines() if line.startswith("context ")][-1])
                self.assertEqual(receipt["context_status"], "incomplete")
                self.assertEqual(receipt["core_exit"], 1 if fail else None)
                if fail:
                    self.assertEqual(receipt["target"]["head"], self.fx.head)
                self.assert_helper_stopped()
