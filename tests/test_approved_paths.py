"""Owned inert path boundaries; no real metadata client or authentication."""
from __future__ import annotations

from pathlib import Path
import os
import signal
import tempfile
import unittest
from unittest.mock import patch

from quality_trust import Cancellation, Git, Invalid, OwnedProcess, outside_path, raw_absolute, selector_context


class WalkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "subject"
        self.repo.mkdir()
        self.a, self.b = self.root / "outside-a", self.root / "outside-b"
        for directory in (self.a, self.b):
            (directory / "subdir").mkdir(parents=True)
            for parent in (directory, directory / "subdir"):
                (parent / "tool.py").write_text("# Newly authored inert path fixture; not executed.\n")
        self.hop = self.repo / "traversal"
        self.hop.symlink_to(self.a / "subdir", target_is_directory=True)
        self.alias = self.root / "outside-alias"
        self.alias.symlink_to(self.hop, target_is_directory=True)

    def test_unchanged_literal_parent_and_no_parent_chains_are_refused(self) -> None:
        for parent in (False, True):
            value = self.alias / ".." / "tool.py" if parent else self.alias / "tool.py"
            for destination in (self.a, self.b):
                with self.subTest(parent=parent,destination=destination.name):
                    self.hop.unlink();self.hop.symlink_to(destination / "subdir", target_is_directory=True)
                    with self.assertRaises(Invalid):
                        outside_path(value, [self.repo], strict=True)

    def test_symlink_target_parent_cannot_erase_protected_hop(self) -> None:
        link = self.root / "target-parent"
        link.symlink_to("subject/../outside-a/tool.py")
        with self.assertRaises(Invalid):outside_path(link,[self.repo],strict=True)
        with self.assertRaises(Invalid):outside_path(self.repo,[self.repo],strict=True)

    def test_safe_alias_parent_and_canonical_result(self) -> None:
        safe = self.root / "safe-var-alias"
        safe.symlink_to(self.a / "subdir",target_is_directory=True)
        self.assertEqual(outside_path(safe/"tool.py",[self.repo],strict=True),self.a/"subdir/tool.py")
        self.assertEqual(outside_path(safe/".."/"tool.py",[self.repo],strict=True),self.a/"tool.py")
        self.assertEqual(outside_path(safe/"tool.py",[self.repo],strict=True,final_symlink=False),self.a/"subdir/tool.py")
        # Finite revisits are not cycles; only expansion/work limits bound them.
        self.assertEqual(outside_path(safe/".."/".."/"safe-var-alias"/"tool.py",[self.repo],strict=True),self.a/"subdir/tool.py")

    def test_relative_context_and_protected_start(self) -> None:
        caller = self.root / "caller";caller.mkdir()
        previous=Path.cwd()
        try:
            os.chdir(caller)
            raw=Path("../outside-a/tool.py")
            self.assertIn("..",raw_absolute(raw).parts)
            self.assertEqual(outside_path(raw,[self.repo],strict=True),self.a/"tool.py")
            os.chdir(self.repo)
            with self.assertRaises(Invalid):outside_path(raw,[self.repo],strict=True)
            self.assertEqual(outside_path(self.a/"tool.py",[self.repo],strict=True),self.a/"tool.py")
        finally:os.chdir(previous)

    def test_terminal_symlink_policy_survives_canonicalization(self) -> None:
        link=self.root/"final-tool";link.symlink_to(self.a/"tool.py")
        self.assertEqual(outside_path(link,[self.repo],strict=True),self.a/"tool.py")
        with self.assertRaises(Invalid):outside_path(link,[self.repo],strict=True,final_symlink=False)
        directory=self.root/"final-directory";directory.symlink_to(self.a,target_is_directory=True)
        self.assertEqual(outside_path(directory,[self.repo],strict=True),self.a)
        with self.assertRaises(Invalid):outside_path(directory,[self.repo],final_symlink=False)

    def test_creation_tails_strict_reads_and_non_directory_parents(self) -> None:
        missing=self.root/"new"/"nested"/"state"
        self.assertEqual(outside_path(missing,[self.repo]),missing)
        with self.assertRaises(Invalid):outside_path(missing,[self.repo],strict=True)
        with self.assertRaises(Invalid):outside_path(self.root/"new"/".."/"state",[self.repo])
        with self.assertRaises(Invalid):outside_path(self.a/"tool.py"/"..",[self.repo])

    def test_cycles_expansion_and_work_budget_refuse(self) -> None:
        cycle=self.root/"cycle";cycle.symlink_to("cycle")
        with self.assertRaises(Invalid):outside_path(cycle,[self.repo])
        for number in range(41):
            (self.root/("link"+str(number))).symlink_to("link"+str(number+1) if number<40 else "outside-a/tool.py")
        with self.assertRaises(Invalid):outside_path(self.root/"link0",[self.repo],strict=True)
        with self.assertRaises(Invalid):outside_path(self.root.joinpath(*(["tail"]*4200)),[self.repo])
        safe=self.root/"readlink-error";safe.symlink_to(self.a/"tool.py")
        with patch("quality_trust.os.readlink",side_effect=PermissionError):
            with self.assertRaises(Invalid):outside_path(safe,[self.repo],strict=True)

    def test_defaults_refuse_before_probe_git_or_clock_execution(self) -> None:
        unsafe=self.alias/"tool.py"
        cancel=Cancellation()
        with cancel.handlers(),patch.object(OwnedProcess,"_capability_verified",True),patch("quality_trust.sys.executable",str(unsafe)),patch("quality_trust.subprocess.Popen") as spawn:
            with self.assertRaises(Invalid):OwnedProcess(cancel,protected_roots=[self.repo]).start(["never-executed"])
            spawn.assert_not_called()
        with patch("quality_trust.shutil.which",return_value=str(unsafe)),patch("quality_trust.subprocess.run") as run:
            with self.assertRaises(Invalid):Git(self.repo)
            run.assert_not_called()
        from quality import external_clock
        real_path=Path
        with patch.object(external_clock.sys,"platform","darwin"),patch.object(external_clock,"Path",side_effect=lambda value:unsafe if value=="/usr/sbin/sysctl" else real_path(value)),patch.object(external_clock.subprocess,"run") as run:
            with self.assertRaises(Invalid):external_clock.read(protected_roots=[self.repo])
            run.assert_not_called()


class SelectorContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.repo=Path(self.temp.name).resolve()

    def test_explicit_subject_is_canonical_and_rewritten(self) -> None:
        for flags in (["--repo",str(self.repo)],["--repo="+str(self.repo)]):
            original=["doctor",*flags,"--identity","example/invented"]
            subject,forwarded=selector_context(original)
            self.assertEqual(subject,self.repo)
            self.assertEqual(original,["doctor",*flags,"--identity","example/invented"])
            self.assertIn(str(self.repo),forwarded if len(flags)==2 else [forwarded[1].split("=",1)[1]])

    def test_duplicates_abbreviations_delimiters_and_missing_values_refuse(self) -> None:
        good=["doctor","--repo",str(self.repo)]
        invalid=[good+["--repo="+str(self.repo)],good+["--repo",str(self.repo)],good+["--rep="+str(self.repo)],
                 good+["--r",str(self.repo)],good+["--re="+str(self.repo)],good+["--"],
                 ["doctor","--repo"],["doctor","--repo="],["doctor","--repo","--identity"],
                 ["doctor","--rep",str(self.repo)],["doctor"],["doctor","--repo=-option"]]
        for arguments in invalid:
            with self.subTest(arguments=arguments):
                with self.assertRaises(Invalid):selector_context(arguments)

    def test_subjectless_install_is_explicit_and_bounded(self) -> None:
        for arguments in (["install"],["--adapter-protocol","2","install"],["--adapter-protocol=2","install"]):
            self.assertEqual(selector_context(arguments,subjectless_install=True),(None,arguments))
            with self.assertRaises(Invalid):selector_context(arguments)
        for arguments in (["doctor"],["--adapter","2","install"],["--adapter-protocol","--repo","install"]):
            with self.assertRaises(Invalid):selector_context(arguments,subjectless_install=True)


class RootIdentityTests(unittest.TestCase):
    def test_equivalent_existing_root_identity_is_protected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();subject=root/"subject";subject.mkdir();alias=root/"equivalent-root";alias.mkdir()
            outside=root/"outside";outside.mkdir();(outside/"item").write_text("inert")
            (alias/"traversal").symlink_to(outside,target_is_directory=True)
            actual=Path.lstat;identity=subject.lstat()
            def equivalent(path):
                return identity if path==alias else actual(path)
            with patch.object(Path,"lstat",equivalent):
                with self.assertRaises(Invalid):outside_path(alias/"traversal/item",[subject],strict=True)
            # Distinct owned outside roots remain supported without an identity alias.
            self.assertEqual(outside_path(alias/"traversal/item",[subject],strict=True),outside/"item")

    def test_real_platform_root_alias_cannot_hide_subject_hop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();subject=root/"subject";subject.mkdir()
            alternate=Path('/System/Volumes/Data')/subject.relative_to('/')
            if not alternate.exists() or not os.path.samefile(subject,alternate):
                self.skipTest('no stable alternate root namespace available on this platform')
            outside=root/"outside";(outside/"subdir").mkdir(parents=True)
            (outside/"item").write_text("inert");(outside/"subdir/item").write_text("inert")
            (subject/"traversal").symlink_to(outside/"subdir",target_is_directory=True)
            alias=root/"outside-alias";alias.symlink_to(alternate/"traversal",target_is_directory=True)
            for value in (alias/"item",alias/".."/"item"):
                with self.assertRaises(Invalid):outside_path(value,[subject],strict=True)

    def test_filesystem_root_identity_is_checked_before_named_components(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();subject=root/"root-alias";subject.mkdir()
            item=root/"item";item.write_text("inert")
            actual=Path.lstat;filesystem_root=Path('/').lstat()
            def equivalent(path):
                return filesystem_root if path==subject else actual(path)
            with patch.object(Path,"lstat",equivalent):
                with self.assertRaises(Invalid):outside_path(item,[subject],strict=True)
            self.assertEqual(outside_path(item,[subject],strict=True),item)
