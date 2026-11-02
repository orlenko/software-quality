from __future__ import annotations

import io
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
import zipfile

from quality_trust import Git, Invalid, artifact, canonical, parse_json, sha
from tests.support import Fixture


class TrustTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name))

    def test_duplicate_keys_and_nonfinite_json_rejected(self) -> None:
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}'):
            with self.subTest(data=data), self.assertRaises(Invalid):
                parse_json(data)

    def test_fsmonitor_and_inherited_git_environment_never_execute(self) -> None:
        marker = self.fx.root / "unexpected"
        monitor = self.fx.root / "monitor.sh"
        monitor.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\n")
        monitor.chmod(0o700)
        self.fx.git("config", "core.fsmonitor", str(monitor))
        result, report = self.fx.check(extra_env={"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.fsmonitor",
                                                 "GIT_CONFIG_VALUE_0": str(monitor)})
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())
        self.assertEqual(report["stages"][0]["status"], "pass")

    def test_replacement_refs_cannot_change_resolved_tree(self) -> None:
        before = self.fx.head
        before_tree = self.fx.git("rev-parse", before + "^{tree}")
        self.fx.write("check.py", "raise SystemExit(1)\n")
        after = self.fx.commit()
        self.fx.git("replace", before, after)
        self.assertEqual(Git(self.fx.repo).tree(before), before_tree)

    def test_status_never_executes_configured_clean_or_process_filter(self) -> None:
        marker = self.fx.root / "filter-marker"
        script = self.fx.root / "filter.sh"
        script.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\ncat\n")
        script.chmod(0o700)
        self.fx.write(".gitattributes", "check.py filter=example\n")
        self.fx.head = self.fx.commit()
        for kind in ("clean", "process"):
            with self.subTest(kind=kind):
                self.fx.git("config", "filter.example." + kind, str(script))
                self.fx.write("check.py", "print('changed filter input')\n")
                self.fx.check()
                self.assertFalse(marker.exists())
        included = self.fx.root / "included.gitconfig"
        included.write_text('[filter "included"]\n\tclean = ' + str(script) + '\n\tprocess = ' + str(script) + '\n\trequired = true\n')
        self.fx.git("config", "include.path", str(included))
        self.fx.write(".gitattributes", "check.py filter=included\n")
        self.fx.check()
        self.assertFalse(marker.exists())

    def test_status_does_not_recurse_into_submodule_filters(self) -> None:
        child = self.fx.root / "child"
        child.mkdir()
        env = {"PATH": os.defpath, "HOME": str(self.fx.root), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        def git(*args: str) -> None:
            subprocess.run(["git", "-C", str(child), *args], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        git("init", "-q")
        git("config", "user.name", "Example Maintainer")
        git("config", "user.email", "maintainer@example.invalid")
        (child / "file.txt").write_text("invented")
        (child / ".gitattributes").write_text("file.txt filter=child\n")
        git("add", ".")
        git("commit", "-qm", "Invented child")
        self.fx.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(child), "child")
        self.fx.head = self.fx.commit()
        marker = self.fx.root / "child-filter-marker"
        script = self.fx.root / "child-filter.sh"
        script.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\ncat\n")
        script.chmod(0o700)
        subprocess.run(["git", "-C", str(self.fx.repo / "child"), "config", "filter.child.clean", str(script)], env=env, check=True)
        (self.fx.repo / "child/file.txt").write_text("changed")
        self.fx.check()
        self.assertFalse(marker.exists())

    def test_export_ignores_archive_attributes_and_refuses_symlinks(self) -> None:
        self.fx.write(".gitattributes", "check.py export-ignore\ninstructions.md export-subst\n")
        self.fx.head = self.fx.commit()
        snapshot = self.fx.root / "export"
        snapshot.mkdir()
        Git(self.fx.repo).export(self.fx.head, snapshot)
        self.assertEqual((snapshot / "check.py").read_text(), "print('invented check')\n")
        (self.fx.repo / "escape").symlink_to("../../outside")
        self.fx.head = self.fx.commit()
        second = self.fx.root / "second"
        second.mkdir()
        with self.assertRaisesRegex(Invalid, "snapshot-entry-unsupported"):
            Git(self.fx.repo).export(self.fx.head, second)

    def test_artifact_modified_digest_and_source_refused(self) -> None:
        data = self.fx.package.read_bytes()
        with self.assertRaises(Invalid):
            artifact(data + b"x", self.fx.digest, self.fx.source)
        with self.assertRaises(Invalid):
            artifact(data, self.fx.digest, "2" * 40)
        cached = self.fx.cache / (self.fx.digest + ".pyz")
        cached.chmod(0o600)
        cached.write_bytes(data + b"x")
        result = self.fx.launch(*self.fx.command())
        self.assertEqual(result.returncode, 2)
        self.assertFalse(list(self.fx.state.glob("*/report.json")))

    def test_archive_path_traversal_and_duplicate_members_refused(self) -> None:
        for member in ("../escape", "/absolute", "a\\escape", "quality/../../escape"):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, "w") as archive:
                archive.writestr(member, b"x")
            data = stream.getvalue()
            with self.subTest(member=member), self.assertRaises(Invalid):
                artifact(data, sha(data), self.fx.source)

    def test_python_startup_injection_ignored(self) -> None:
        injected = self.fx.root / "injected"
        injected.mkdir()
        marker = self.fx.root / "startup-marker"
        (injected / "sitecustomize.py").write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        result, _ = self.fx.check(extra_env={"PYTHONPATH": str(injected), "PYTHONHOME": str(injected)})
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())

    def test_cached_symlink_and_nonfull_target_ids_refused(self) -> None:
        cached = self.fx.cache / (self.fx.digest + ".pyz")
        cached.unlink()
        cached.symlink_to(self.fx.package)
        self.assertEqual(self.fx.launch(*self.fx.command()).returncode, 2)
        self.fx.base = "HEAD"
        self.assertEqual(self.fx.launch(*self.fx.command()).returncode, 2)
