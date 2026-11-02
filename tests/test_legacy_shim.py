"""Advertised explicit shim: owned benign work through source and actual bundle."""
from __future__ import annotations

from pathlib import Path
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest

import tests
from tests.support import Fixture, ROOT
from quality_trust import parse_json


class LegacyShimTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fx = Fixture(Path(self.temp.name))
        self.shim = tests.ADAPTER_ROOT / "bin/quality.py" if tests.ADAPTER_ROOT else ROOT / "adapters/quality.py"

    def command(self, *extra: str) -> list[str]:
        return [sys.executable,"-I","-S",str(self.shim),"--launcher",str(ROOT/"quality_launch.py"),
                "--python",sys.executable,*self.fx.command("check",*extra)]

    def process_state(self, pid: int) -> str:
        result = subprocess.run(["ps","-o","stat=","-p",str(pid)],env={"PATH":os.defpath,"LC_ALL":"C"},
                                capture_output=True,text=True,timeout=5)
        self.assertIn(result.returncode,(0,1),result.stderr)
        return result.stdout.strip()

    def test_normal_delegation_and_pin_override_refusal(self) -> None:
        result = subprocess.run(self.command(),capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertIn(self.fx.digest,result.stdout)
        report=parse_json(max(self.fx.state.glob("*/report.json"),key=lambda p:p.stat().st_mtime_ns).read_bytes())
        response,digest=self.fx.response(report)
        result = subprocess.run(self.command("--execute-trusted","--review",str(response),"--review-sha256",digest),
                                capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.fx.write("check.py","raise SystemExit(7)\n");self.fx.head=self.fx.commit()
        result = subprocess.run(self.command("--execute-trusted"),capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,1,result.stderr)
        for extra in (("--artifact",str(self.fx.package)),("--adapter-protocol","2")):
            result = subprocess.run(self.command(*extra),capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,2,result.stderr)

    def test_direct_path_interruption_is_incomplete(self) -> None:
        driver=self.fx.root/"invented-path-interruption.py"
        driver.write_text("""import runpy,sys
from unittest.mock import patch
module=runpy.run_path(sys.argv[1],run_name='owned_shim_test')
sys.argv=sys.argv[1:]
with patch('pathlib.Path.cwd',side_effect=KeyboardInterrupt) as interrupted:
    code=module['main']()
    interrupted.assert_called()
    raise SystemExit(code)
""")
        result=subprocess.run([sys.executable,"-I","-S",str(driver),str(self.shim),"--launcher",str(ROOT/"quality_launch.py"),
                               "--python",sys.executable,"doctor","--repo",str(self.fx.repo)],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertNotIn("Traceback",result.stderr)
        self.assertFalse(self.fx.state.exists())

    def test_relative_approved_paths_preserve_caller_context(self) -> None:
        caller=self.fx.root/"invoking";caller.mkdir()
        (caller/"approved-python").symlink_to(sys.executable)
        (caller/"approved-launcher.py").symlink_to(ROOT/"quality_launch.py")
        arguments=self.fx.command("doctor")
        for flag in ("--repo","--cache","--state"):
            index=arguments.index(flag)+1
            arguments[index]=os.path.relpath(arguments[index],caller)
        command=[sys.executable,"-I","-S",str(self.shim),"--launcher","./approved-launcher.py",
                 "--python","./approved-python",*arguments]
        result=subprocess.run(command,cwd=caller,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertIn(self.fx.digest,result.stdout)
        self.assertTrue(list(self.fx.state.glob("*/report.json")))
        command[command.index("--python")+1]="unavailable-interpreter"
        result=subprocess.run(command,cwd=caller,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertNotIn("Traceback",result.stderr)

    def test_missing_adjacent_resources_refuse_without_import_traceback(self) -> None:
        partial=self.fx.root/"partial";partial.mkdir();shim=partial/"quality.py";shim.write_bytes(self.shim.read_bytes())
        for frontend in (False,True):
            if frontend:
                source=self.shim.with_name("quality_context.py")
                (partial/"quality_context.py").write_bytes(source.read_bytes())
            result=subprocess.run([sys.executable,"-I","-S",str(shim),"--help"],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn("incomplete adapter resource closure",result.stderr)
            self.assertNotIn("Traceback",result.stderr)

    def test_real_signal_current_invocation_handoff_and_owned_cleanup(self) -> None:
        for code in (None,7):
            for signum in (signal.SIGTERM,signal.SIGINT):
                with self.subTest(natural=code,signum=signum):
                    case_root=Path(self.temp.name)/("case-"+str(code)+"-"+str(int(signum)))
                    case_root.mkdir()
                    self.fx=Fixture(case_root)
                    self.fx.write("check.py", "import os,subprocess,sys,time\nfrom pathlib import Path\n"
                        "root=Path(os.environ['QUALITY_STATE_ROOT'])\n"
                        "child=subprocess.Popen([sys.executable,'-I','-S','-c','import time;time.sleep(8)'])\n"
                        "(root/'descendant').write_text(str(child.pid))\n"
                        "(root/'leader').write_text(str(os.getpid()))\n"+
                        ("raise SystemExit(7)\n" if code else "time.sleep(8)\n"))
                    self.fx.head=self.fx.commit()
                    with subprocess.Popen(self.command("--execute-trusted"),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as process:
                        deadline=time.monotonic()+10
                        directory=None
                        while time.monotonic()<deadline and process.poll() is None:
                            choices=list(self.fx.state.glob("*/state-unit/leader"))
                            if choices:
                                candidate=max(choices,key=lambda p:p.stat().st_mtime_ns).parent
                                leader_text=(candidate/"leader").read_text()
                                child_text=(candidate/"descendant").read_text()
                                if leader_text and child_text:
                                    leader,descendant=int(leader_text),int(child_text)
                                    # A natural nonzero leader must be terminal before cancellation.
                                    if code is None or self.process_state(leader).startswith("Z"):
                                        directory=candidate
                                        break
                            time.sleep(.005)
                        self.assertIsNotNone(directory,"owned shim fixture did not reach signal point")
                        process.send_signal(signum)
                        stdout,stderr=process.communicate(timeout=15)
                        self.assertEqual(process.returncode,1 if code else 2,stderr)
                    report=parse_json((directory.parent/"report.json").read_bytes())
                    self.assertEqual(report["overall"],"fail" if code else "incomplete")
                    self.assertTrue(any(row["reason"]=="run-interrupted" for row in report["stages"]),stdout+stderr)
                    for pid in (leader,descendant):
                        state=self.process_state(pid)
                        self.assertTrue(not state or state.startswith("Z"),"owned fixture still active")
