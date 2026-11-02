"""Safe identity regressions: fake OS identities never designate real processes."""
from __future__ import annotations

from contextlib import ExitStack
import errno
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from quality_trust import Cancellation, Invalid, OwnedProcess
from quality.process import stop

FAKE_PID = 71337001


def exited(code: int = 7) -> SimpleNamespace:
    return SimpleNamespace(si_pid=FAKE_PID, si_code=os.CLD_EXITED, si_status=code)


class IdentityTests(unittest.TestCase):
    def fake(self, waitid: object, killpg: object) -> tuple[ExitStack, OwnedProcess, SimpleNamespace]:
        stack = ExitStack()
        self.addCleanup(stack.close)
        cancel = Cancellation()
        stack.enter_context(cancel.handlers())
        stack.enter_context(patch.object(OwnedProcess, "_capability_verified", True))
        process = SimpleNamespace(pid=FAKE_PID, returncode=None, stdout=None)
        stack.enter_context(patch("quality_trust.subprocess.Popen", return_value=process))
        stack.enter_context(patch("quality_trust.os.waitid", side_effect=waitid))
        stack.enter_context(patch("quality_trust.os.killpg", side_effect=killpg))
        owned = OwnedProcess(cancel, protected_roots=[])
        owned.start(["invented-never-executed"])
        return stack, owned, process

    def test_status_does_not_reap_and_signal_precedes_real_wait(self) -> None:
        events = []
        def waitid(kind, pid, flags):
            events.append(("observe" if flags & os.WNOWAIT else "reap", pid))
            return exited()
        def killpg(pid, sig):
            events.append(("signal", sig))
            if sig == 0:
                raise ProcessLookupError
        _, owned, process = self.fake(waitid, killpg)
        self.assertEqual(owned.observe(), 7)
        self.assertIsNone(process.returncode)
        self.assertTrue(owned.close())
        self.assertEqual(process.returncode, 7)
        self.assertLess(events.index(("signal", signal.SIGKILL)), events.index(("reap", FAKE_PID)))
        before = list(events)
        with self.assertRaises(Invalid):
            owned.send(signal.SIGTERM)
        self.assertEqual(events, before)
        self.assertTrue(owned.close())

    def test_reaped_or_reused_identity_never_authorizes_signal(self) -> None:
        for release in ("returncode", "echild"):
            with self.subTest(release=release), ExitStack() as scope:
                calls = []
                def waitid(kind, pid, flags):
                    raise ChildProcessError(errno.ECHILD, "fake released identity")
                def killpg(pid, sig):
                    calls.append((pid, sig))
                    return None  # A reused numeric group exists; it is unrelated.
                _, owned, process = self.fake(waitid, killpg)
                if release == "returncode":
                    process.returncode = 0
                self.assertFalse(stop(owned))
                self.assertEqual(calls, [])
                with self.assertRaises(Invalid):
                    owned.send(signal.SIGKILL)
                self.assertEqual(calls, [])

    def test_interrupted_reaping_ends_all_signal_authority(self) -> None:
        calls = []
        def waitid(kind, pid, flags):
            if not flags & os.WNOWAIT:
                raise KeyboardInterrupt
            return exited()
        _, owned, _ = self.fake(waitid, lambda pid, sig: calls.append(sig))
        with self.assertRaises(KeyboardInterrupt):
            owned.close()
        self.assertEqual(owned.code, 7)
        self.assertEqual(calls, [signal.SIGKILL])
        self.assertFalse(owned.close())
        with self.assertRaises(Invalid):
            owned.send(signal.SIGINT)
        self.assertEqual(calls, [signal.SIGKILL])

    def test_eperm_is_separate_from_owned_wait_and_absence(self) -> None:
        for absent in (True, False):
            with self.subTest(absent=absent):
                calls = []
                def killpg(pid, sig):
                    calls.append(sig)
                    if sig:
                        raise PermissionError
                    if absent:
                        raise ProcessLookupError
                _, owned, _ = self.fake(lambda *args: exited(0), killpg)
                # Advance only the observation deadline; no real process exists.
                ticks = iter(range(100))
                with patch("quality_trust.time.monotonic", side_effect=lambda: next(ticks)):
                    self.assertEqual(owned.close(), absent)
                self.assertTrue(owned.signal_unavailable)
                self.assertTrue(owned.reaped)
                self.assertEqual(calls.count(signal.SIGKILL), 1)
                self.assertTrue(all(sig == 0 for sig in calls[1:]))

    def test_missing_capability_and_autoreaping_policy_refuse_spawn(self) -> None:
        cancel = Cancellation()
        with cancel.handlers(), patch("quality_trust.subprocess.Popen") as popen:
            with patch("quality_trust.os.waitid", None):
                with self.assertRaises(Invalid):
                    OwnedProcess(cancel, protected_roots=[]).start(["never-executed"])
            with patch("quality_trust.signal.getsignal", return_value=signal.SIG_IGN):
                with self.assertRaises(Invalid):
                    OwnedProcess(cancel, protected_roots=[]).start(["never-executed"])
            popen.assert_not_called()

    def test_failed_probe_never_starts_target_or_signals(self) -> None:
        cancel = Cancellation()
        process = SimpleNamespace(pid=FAKE_PID, returncode=None, stdout=None)
        with cancel.handlers(), patch.object(OwnedProcess, "_capability_verified", False), \
             patch("quality_trust.subprocess.Popen", return_value=process) as popen, \
             patch("quality_trust.os.waitid", side_effect=OSError(errno.EINVAL, "fake unsupported")), \
             patch("quality_trust.os.waitpid", return_value=(FAKE_PID, 0)), patch("quality_trust.os.killpg") as kill:
            with self.assertRaises(Invalid):
                OwnedProcess(cancel, protected_roots=[]).start(["target-never-executed"])
            self.assertEqual(popen.call_count, 1)
            self.assertEqual(popen.call_args.args[0][-2:], ["-c", "pass"])
            kill.assert_not_called()

    def test_cancellation_handler_records_without_signaling(self) -> None:
        cancel = Cancellation()
        with patch("quality_trust.os.killpg") as kill, cancel.handlers():
            cancel.request(signal.SIGTERM)
            self.assertTrue(cancel.requested)
            kill.assert_not_called()


class OwnedChildrenTests(unittest.TestCase):
    def test_benign_natural_status_and_clean_group(self) -> None:
        for code in (0, 7):
            with self.subTest(code=code):
                cancel = Cancellation()
                owned = OwnedProcess(cancel, protected_roots=[])
                with cancel.handlers():
                    try:
                        owned.start([sys.executable, "-I", "-S", "-c", "raise SystemExit("+str(code)+")"],
                                    env={"PATH": os.defpath, "HOME": "/nonexistent", "LC_ALL": "C"},
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        self.assertEqual(owned.wait(), code)
                    finally:
                        owned.close()
                self.assertTrue(owned.reaped)
                self.assertTrue(owned.cleanup_complete)

    def test_owned_descendant_cleanup_after_leader_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child"
            code = "import subprocess,sys;from pathlib import Path;p=subprocess.Popen([sys.executable,'-I','-S','-c','import time;time.sleep(2)']);Path(sys.argv[1]).write_text(str(p.pid))"
            cancel = Cancellation()
            owned = OwnedProcess(cancel, protected_roots=[])
            with cancel.handlers():
                try:
                    owned.start([sys.executable, "-I", "-S", "-c", code, str(marker)], env={"PATH": os.defpath, "HOME": directory, "LC_ALL": "C"},
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    deadline = time.monotonic()+3
                    while owned.observe() is None and time.monotonic()<deadline:
                        time.sleep(0.005)
                    self.assertEqual(owned.code, 0)
                    complete = owned.close()
                finally:
                    owned.close()
            self.assertTrue(owned.reaped)
            # Empty-group evidence is platform-dependent; never manufacture it.
            if complete:
                with self.assertRaises(ProcessLookupError):
                    os.killpg(owned.pid, 0)
            else:
                self.assertFalse(owned.cleanup_complete)


class CallerBoundaryTests(unittest.TestCase):
    def test_pipe_close_fault_preserves_natural_nonzero(self):
        from quality.process import execute, CommandInterrupted
        for error in (OSError("invented pipe close"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                rfd, wfd = os.pipe()
                os.close(wfd)
                self.addCleanup(os.close, rfd)
                class BrokenClose:
                    def fileno(self): return rfd
                    def close(self): raise error
                process = SimpleNamespace(pid=FAKE_PID, returncode=None, stdout=BrokenClose())
                def killpg(pid, sig):
                    if sig == 0: raise ProcessLookupError
                with patch.object(OwnedProcess,"_capability_verified",True), patch("quality_trust.subprocess.Popen",return_value=process), \
                     patch("quality_trust.os.waitid",side_effect=lambda *args:exited(7)), patch("quality_trust.os.killpg",side_effect=killpg):
                    call=lambda:execute({"argv":["never-executed"],"timeout_seconds":1,"max_log_bytes":100},Path(directory),Path(directory)/"state",Path(directory)/"log",subject=Path(directory))
                    if isinstance(error,KeyboardInterrupt):
                        with self.assertRaises(CommandInterrupted) as observed: call()
                        self.assertEqual(observed.exception.code,7)
                    else:
                        result=call()
                        self.assertEqual(result[0],"fail")
                        self.assertEqual(result[2],7)
                        self.assertEqual(result[3],"incomplete")

    def test_adapter_final_format_and_write_interrupt_retains_core_failure(self):
        import adapters.quality_context as frontend
        for code in (0,1):
            for boundary in ("canonical","write_output"):
                with self.subTest(code=code,boundary=boundary),tempfile.TemporaryDirectory() as directory:
                    root=Path(directory);repo=root/"subject";repo.mkdir()
                    args=SimpleNamespace(personal=True,identity="example/demo",repo=repo,python=Path(sys.executable),
                        launcher=Path(frontend.__file__).resolve().parents[1]/"quality_launch.py",cache=root/"cache",state=root/"state",
                        base="1"*40,head="1"*40,pr=None,current_pr=False,execute_trusted=False,review=None,review_sha256=None,
                        action="doctor",cancellation=Cancellation())
                    fake_git=SimpleNamespace(commit=lambda value:value,blob=lambda *args:b'{"repository":"example/demo"}')
                    with args.cancellation.handlers(),patch.object(frontend,"Git",return_value=fake_git), \
                         patch.object(frontend,"launch",return_value=(code,False)),patch.object(frontend,boundary,side_effect=KeyboardInterrupt):
                        self.assertEqual(frontend.frontend_main(args),1 if code==1 else 2)

    def test_bootstrap_install_output_cancellation_is_incomplete(self):
        import quality_launch,quality_external_launch
        for module in (quality_launch,quality_external_launch):
            with self.subTest(module=module.__name__),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);archive=root/"invented.pyz";archive.write_bytes(b"not executed")
                args=SimpleNamespace(command="install",cache=root/"cache",artifact=archive,sha256="a"*64,source="1"*40)
                cancel=Cancellation()
                def interrupted_output(*args,**kwargs):cancel.request(signal.SIGTERM)
                verifier="artifact" if module is quality_launch else "verify"
                with cancel.handlers(),patch.object(module,verifier),patch.object(module,"write_output",side_effect=interrupted_output):
                    self.assertEqual(module.launch_main(args,cancel),2)

    def test_bootstrap_cancellation_during_reap_cannot_signal_released_id(self):
        import quality_launch,quality_external_launch
        from quality_trust import VERSION,EXTERNAL_VERSION,canonical
        for module in (quality_launch,quality_external_launch):
            with self.subTest(module=module.__name__),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);repo=root/"subject";repo.mkdir();cache=root/"cache";cache.mkdir();(cache/("a"*64+".pyz")).write_bytes(b"not executed")
                args=SimpleNamespace(command="doctor",cache=cache,repo=repo,state=root/"state",base="1"*40,head="1"*40,
                    identity="example/demo",trusted_head=None,plan=None,evidence=None,evidence_sha256=None,approved_producer=None,
                    observations=None,observations_sha256=None,approved_observer=None,execute_trusted=False,review=None,review_sha256=None)
                version=VERSION if module is quality_launch else EXTERNAL_VERSION
                pin={"schema_version":1 if module is quality_launch else 2,"publisher":"orlenko/software-quality",
                     "version":version,"policy_version":"0.1","source":"1"*40,"artifact_sha256":"a"*64}
                fake_git=SimpleNamespace(commit=lambda value:value,blob=lambda *args:canonical(pin))
                process=SimpleNamespace(pid=FAKE_PID,returncode=None,stdout=None)
                cancel=Cancellation();events=[]
                def waitid(kind,pid,flags):
                    if not flags&os.WNOWAIT:
                        cancel.request(signal.SIGTERM)
                        events.append("reap")
                    return exited(1)
                def killpg(pid,sig):
                    if sig==0:raise ProcessLookupError
                    self.assertNotIn("reap",events)
                    events.append(sig)
                verifier="artifact" if module is quality_launch else "verify"
                with cancel.handlers(),patch.object(module,"Git",return_value=fake_git),patch.object(module,verifier), \
                     patch.object(OwnedProcess,"_capability_verified",True),patch("quality_trust.subprocess.Popen",return_value=process), \
                     patch("quality_trust.os.waitid",side_effect=waitid),patch("quality_trust.os.killpg",side_effect=killpg):
                    self.assertEqual(module.launch_main(args,cancel),1)
                self.assertEqual(events,[signal.SIGKILL,"reap"])

    def test_full_owned_output_pipe_is_bounded_and_cancelled(self):
        from quality_trust import OutputUnavailable,write_output
        rfd,wfd=os.pipe()
        try:
            os.set_blocking(wfd,False)
            while True:
                try:os.write(wfd,b"x"*4096)
                except BlockingIOError:break
            cancel=Cancellation();start=time.monotonic()
            with self.assertRaises(OutputUnavailable):write_output(b"result",cancel,fd=wfd,seconds=.02)
            self.assertLess(time.monotonic()-start,1)
            cancel.request(signal.SIGTERM)
            with self.assertRaises(OutputUnavailable):write_output(b"result",cancel,fd=wfd)
        finally:
            os.close(wfd);os.close(rfd)

    def test_legacy_recovery_diagnostic_interrupt_retains_known_failure(self):
        from quality import cli
        from quality.evidence import stage
        for known in (False, True):
            args = SimpleNamespace(cancellation=Cancellation(), experimental_source=True)
            def unavailable(*unused):
                if known:
                    args._validated_report = {"stages": [stage("invented", "fail", "invented-known-failure")]}
                raise OSError("invented ordinary finalization error")
            with args.cancellation.handlers(), patch.object(cli,"run",side_effect=unavailable), \
                 patch.object(cli,"write_output",side_effect=KeyboardInterrupt):
                args.artifact_sha256="a"*64;args.source="1"*40
                self.assertEqual(cli.run_main(args),1 if known else 2)
