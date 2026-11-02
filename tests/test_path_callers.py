"""Marker-only owned helpers; hidden-path refusal before helper or auth use."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

import tests
from tests.support import Fixture, ROOT


class PathCallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.fx=Fixture(self.root)
        self.adapter=tests.ADAPTER_ROOT/"bin" if tests.ADAPTER_ROOT else ROOT/"adapters"
        self.frontend=self.adapter/"quality_context.py";self.shim=self.adapter/"quality.py"
        self.marker=self.root/"marker.json"
        self.a,self.b=self.root/"outside-a",self.root/"outside-b"
        self.hop=self.fx.repo/"traversal"
        for directory in (self.a,self.b):
            (directory/"subdir").mkdir(parents=True)
            for parent in (directory,directory/"subdir"):
                (parent/"auth").mkdir()
                body=parent/"helper.py"
                body.write_text("import json,os,sys\nfrom pathlib import Path\nPath("+repr(str(self.marker))+").write_text(json.dumps({'argv':sys.argv[1:],'auth':os.environ.get('GH_CONFIG_DIR'),'entry':os.environ.get('QUALITY_INVENTED_ENTRY')}))\nraise SystemExit(9)\n")
                wrapper=parent/"helper"
                wrapper.write_text("#!/bin/sh\nQUALITY_INVENTED_ENTRY=\"$0\"\nexport QUALITY_INVENTED_ENTRY\nexec "+shlex.quote(str(Path(sys.executable).resolve()))+" -I -S "+shlex.quote(str(body))+" \"$@\"\n")
                wrapper.chmod(0o700)
        self.hop.symlink_to(self.a/"subdir",target_is_directory=True)
        self.alias=self.root/"outside-alias";self.alias.symlink_to(self.hop,target_is_directory=True)
        self.safe_auth=self.root/"empty-invented-auth";self.safe_auth.mkdir()

    def frontend_command(self, *, metadata: bool=False) -> list[str]:
        command=[sys.executable,"-I","-S",str(self.frontend),"--launcher",str(ROOT/"quality_launch.py"),
                 "--python",sys.executable,"--repo",str(self.fx.repo),"--identity","example/demo","--personal",
                 "--base",self.fx.base,"--head",self.fx.head,"--cache",str(self.fx.cache),"--state",str(self.fx.state)]
        if metadata:command += ["--pr","7","--allow-github-metadata","--github-cli",str(self.a/"helper"),"--github-config",str(self.safe_auth)]
        return command

    def value(self, name: str, parent: bool) -> Path:
        return self.alias/".."/name if parent else self.alias/name

    def retarget(self, destination: Path) -> None:
        self.hop.unlink();self.hop.symlink_to(destination/"subdir",target_is_directory=True)
        self.fx.head=self.fx.commit()

    def run_refusal(self, command: list[str]) -> None:
        self.marker.unlink(missing_ok=True)
        result=subprocess.run(command,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,2,result.stderr+result.stdout)
        self.assertFalse(self.marker.exists(),"unsafe selected helper or auth route was used")
        self.assertFalse(self.fx.state.exists(),"unsafe selector reached core invocation")

    def test_frontend_every_tool_and_auth_role_refuses_both_hidden_forms(self) -> None:
        for role,name in (("--python","helper"),("--launcher","helper.py"),("--github-cli","helper"),("--github-config","auth")):
            for parent in (False,True):
                literal=str(self.value(name,parent))
                for destination in (self.a,self.b):
                    with self.subTest(role=role,parent=parent,destination=destination.name):
                        self.retarget(destination)
                        command=self.frontend_command(metadata=role.startswith("--github"))
                        command[command.index(role)+1]=literal
                        self.run_refusal(command)

    def test_simple_shim_preserves_raw_evidence_for_both_selectors(self) -> None:
        for role,name in (("--python","helper"),("--launcher","helper.py")):
            for parent in (False,True):
                literal=str(self.value(name,parent))
                for destination in (self.a,self.b):
                    with self.subTest(role=role,parent=parent,destination=destination.name):
                        self.retarget(destination)
                        command=[sys.executable,"-I","-S",str(self.shim),"--launcher",str(ROOT/"quality_launch.py"),
                                 "--python",sys.executable,*self.fx.command("doctor")]
                        command[command.index(role)+1]=literal
                        self.run_refusal(command)

    def test_shim_ambiguous_repo_forms_refuse_before_marker_interpreter(self) -> None:
        for extra in (["--rep="+str(self.root)],["--repo="+str(self.root)],["--re",str(self.root)],["--"],["--repo"]):
            with self.subTest(extra=extra):
                command=[sys.executable,"-I","-S",str(self.shim),"--launcher",str(ROOT/"quality_launch.py"),
                         "--python",str(self.a/"helper"),*self.fx.command("doctor"),*extra]
                self.run_refusal(command)

    def test_safe_aliases_consume_canonical_client_and_auth_directory(self) -> None:
        client=self.root/"safe-client-alias";client.symlink_to(self.a/"helper")
        auth=self.root/"safe-auth-alias";auth.symlink_to(self.safe_auth,target_is_directory=True)
        command=self.frontend_command(metadata=True)
        command[command.index("--github-cli")+1]=str(client)
        command[command.index("--github-config")+1]=str(auth)
        result=subprocess.run(command,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertTrue(self.marker.exists(),"approved marker client did not execute")
        receipt=json.loads(self.marker.read_text())
        self.assertEqual(receipt["auth"],str(self.safe_auth))
        self.assertEqual(receipt["entry"],str(self.a/"helper"))
        self.assertEqual(receipt["argv"][:4],["api","--hostname","github.com","--method"])

    def test_safe_relative_frontend_selectors_keep_caller_context(self) -> None:
        caller=self.root/"invoking";caller.mkdir()
        (caller/"approved-python").symlink_to(Path(sys.executable).resolve())
        (caller/"approved-launcher.py").symlink_to(ROOT/"quality_launch.py")
        command=self.frontend_command()
        command[command.index("--python")+1]="./approved-python"
        command[command.index("--launcher")+1]="./approved-launcher.py"
        for flag in ("--repo","--cache","--state"):
            index=command.index(flag)+1;command[index]=os.path.relpath(command[index],caller)
        result=subprocess.run(command,cwd=caller,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,2,result.stderr+result.stdout)
        receipt=json.loads([line[8:] for line in result.stdout.splitlines() if line.startswith("context ")][-1])
        self.assertEqual(receipt["context_status"],"complete")
        self.assertEqual(receipt["core_exit"],2)
        self.assertFalse(self.marker.exists())

    def test_frontend_preserves_separate_launcher_toolkit_protection(self) -> None:
        toolkit=self.root/"approved-launcher-toolkit";toolkit.mkdir()
        for name in ("quality_launch.py","quality_trust.py"):
            (toolkit/name).write_bytes((ROOT/name).read_bytes())
        hop=toolkit/"traversal";hop.symlink_to(self.a/"subdir",target_is_directory=True)
        alias=self.root/"launcher-root-alias";alias.symlink_to(hop,target_is_directory=True)
        candidate_cache=self.a/"subdir/cache";candidate_cache.mkdir()
        (candidate_cache/(self.fx.digest+".pyz")).write_bytes(self.fx.package.read_bytes())
        for role,suffix in (("--cache","cache"),("--state","state")):
            with self.subTest(role=role):
                command=self.frontend_command()
                command[command.index("--launcher")+1]=str(toolkit/"quality_launch.py")
                command[command.index(role)+1]=str(alias/suffix)
                self.run_refusal(command)
                self.assertFalse((self.a/"subdir/state").exists())


class CorePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.fx=Fixture(self.root)
        self.outside=self.root/"outside";self.outside.mkdir();(self.outside/"subdir").mkdir()
        self.hop=self.fx.repo/"traversal";self.hop.symlink_to(self.outside/"subdir",target_is_directory=True)
        self.alias=self.root/"outside-alias";self.alias.symlink_to(self.hop,target_is_directory=True)

    def direct(self, *extra: str, package: Path | None=None) -> list[str]:
        arguments=self.fx.command("doctor",*extra)
        index=arguments.index("--cache");del arguments[index:index+2]
        return [sys.executable,"-I","-S",str(package or self.fx.cache/(self.fx.digest+".pyz")),*arguments,
                "--artifact-sha256",self.fx.digest,"--source",self.fx.source]

    def test_bootstrap_and_actual_core_refuse_hidden_state_before_record(self) -> None:
        for parent in (False,True):
            value=self.alias/".."/"state" if parent else self.alias/"state"
            for direct in (False,True):
                with self.subTest(parent=parent,direct=direct):
                    result=subprocess.run(self.direct("--state",str(value)),capture_output=True,text=True,timeout=15) if direct else self.fx.launch(*self.fx.command("doctor","--state",str(value)))
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertFalse((self.outside/"state").exists())
                    self.assertFalse((self.outside/"subdir/state").exists())
                    self.assertFalse(self.fx.state.exists())

    def test_bootstrap_refuses_hidden_cache_and_current_archive_entry_hop(self) -> None:
        for parent in (False,True):
            directory=self.outside if parent else self.outside/"subdir"
            cache=directory/"cache";cache.mkdir()
            (cache/(self.fx.digest+".pyz")).write_bytes(self.fx.package.read_bytes())
            value=self.alias/".."/"cache" if parent else self.alias/"cache"
            result=self.fx.launch(*self.fx.command("doctor","--cache",str(value)))
            self.assertEqual(result.returncode,2,result.stderr)
            archive=directory/"approved.pyz";archive.write_bytes(self.fx.package.read_bytes())
            entry=self.alias/".."/"approved.pyz" if parent else self.alias/"approved.pyz"
            result=subprocess.run(self.direct(package=entry),capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertFalse(self.fx.state.exists())

    def test_install_and_cached_archive_terminal_links_remain_refused(self) -> None:
        link=self.root/"archive-link.pyz";link.symlink_to(self.fx.package)
        cache=self.root/"install-cache"
        result=self.fx.launch("install","--artifact",str(link),"--sha256",self.fx.digest,"--source",self.fx.source,"--cache",str(cache))
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(cache.exists())
        cached=self.fx.cache/(self.fx.digest+".pyz")
        saved=self.root/"saved.pyz";cached.rename(saved);cached.symlink_to(saved)
        result=self.fx.launch(*self.fx.command("doctor"))
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(self.fx.state.exists())

    def test_unsafe_review_stays_incomplete_without_erasing_known_failure(self) -> None:
        self.hop.unlink()  # Keep the snapshot free of unsupported tracked links.
        self.fx.write("check.py","raise SystemExit(7)\n");self.fx.head=self.fx.commit()
        self.hop.symlink_to(self.outside/"subdir",target_is_directory=True)
        _,initial=self.fx.check(mode="doctor")
        response,digest=self.fx.response(initial)
        for parent in (False,True):
            directory=self.outside if parent else self.outside/"subdir"
            (directory/"review.json").write_bytes(Path(response).read_bytes())
            value=self.alias/".."/"review.json" if parent else self.alias/"review.json"
            result,report=self.fx.check("--execute-trusted","--review",str(value),"--review-sha256",digest)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertEqual(report["overall"],"fail")
            check=next(row for row in report["stages"] if row["id"]=="check:unit")
            self.assertEqual(check["status"],"fail")
            review=next(row for row in report["stages"] if row["id"].startswith("review:"))
            self.assertEqual(review["status"],"incomplete")
            self.assertEqual(review["reason"],"path-traverses-protected-root")


class ExternalShimPathTests(unittest.TestCase):
    def test_raw_entry_is_checked_before_derived_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();subject=root/"subject";subject.mkdir();marker=root/"marker"
            toolkits=[root/"approved-a",root/"approved-b"]
            for toolkit in toolkits:
                (toolkit/"adapters").mkdir(parents=True)
                (toolkit/"adapters/quality_external.py").write_bytes((ROOT/"adapters/quality_external.py").read_bytes())
                (toolkit/"quality_trust.py").write_bytes((ROOT/"quality_trust.py").read_bytes())
                (toolkit/"quality_external_launch.py").write_text("from pathlib import Path\nPath("+repr(str(marker))+").touch()\nraise SystemExit(9)\n")
            hop=subject/"traversal";hop.symlink_to(toolkits[0]/"adapters",target_is_directory=True)
            alias=root/"outside-alias";alias.symlink_to(hop,target_is_directory=True)
            for parent in (False,True):
                entry=alias/".."/"adapters/quality_external.py" if parent else alias/"quality_external.py"
                for toolkit in toolkits:
                    hop.unlink();hop.symlink_to(toolkit/"adapters",target_is_directory=True)
                    result=subprocess.run([sys.executable,"-I","-S",str(entry),"doctor","--repo",str(subject)],capture_output=True,text=True,timeout=10)
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertFalse(marker.exists(),"unsafe derived bootstrap executed")
            safe=toolkits[0]/"adapters/quality_external.py"
            result=subprocess.run([sys.executable,"-I","-S",str(safe),"doctor","--repo="+str(subject)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,9,result.stderr)
            self.assertTrue(marker.exists(),"safe owned bootstrap control did not run")


class DefaultArchivePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.fx=Fixture(self.root)
        self.marker=self.root/"marker"
        outside=self.root/"outside";(outside/"subdir").mkdir(parents=True)
        body=outside/"subdir/helper.py";body.write_text("from pathlib import Path\nPath("+repr(str(self.marker))+").touch()\nraise SystemExit(9)\n")
        helper=outside/"subdir/helper";helper.write_text("#!/bin/sh\nexec "+shlex.quote(str(Path(sys.executable).resolve()))+" -I -S "+shlex.quote(str(body))+" \"$@\"\n");helper.chmod(0o700)
        hop=self.fx.repo/"traversal";hop.symlink_to(outside/"subdir",target_is_directory=True)
        alias=self.root/"alias";alias.symlink_to(hop,target_is_directory=True)
        self.unsafe=alias/"helper"

    def test_actual_core_default_python_and_git_refuse_before_helper_use(self) -> None:
        package=self.fx.cache/(self.fx.digest+".pyz")
        arguments=self.fx.command("doctor");index=arguments.index("--cache");del arguments[index:index+2]
        argv=[str(package),*arguments,"--artifact-sha256",self.fx.digest,"--source",self.fx.source]
        for role in ("python","git"):
            with self.subTest(role=role):
                driver=self.root/("default-"+role+".py")
                driver.write_text("""import sys
from unittest.mock import patch
package,unsafe,role=sys.argv[1:4]
sys.path.insert(0,package)
from quality.cli import main
import quality_trust as trust
sys.argv=[package,*sys.argv[4:]]
expected_repo=sys.argv[sys.argv.index('--repo')+1]
observed=[]
actual=trust.outside_path
def inspected(path,roots,**kwargs):
    if str(path)==unsafe:observed.append([str(root) for root in roots])
    return actual(path,roots,**kwargs)
with patch.object(trust,'outside_path',side_effect=inspected):
    with patch('sys.executable',unsafe) if role=='python' else patch('quality_trust.shutil.which',return_value=unsafe):
        try: code=main()
        except SystemExit as exc: code=exc.code
    assert observed and all(expected_repo in roots for roots in observed),'unsafe default selector was not checked against subject'
    raise SystemExit(code)
""")
                result=subprocess.run([sys.executable,"-I","-S",str(driver),str(package),str(self.unsafe),role,*argv[1:]],capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertFalse(self.marker.exists(),"unsafe default helper executed")
                self.assertFalse(self.fx.state.exists())
