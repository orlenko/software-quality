"""Bounded trusted-local command execution; explicitly not containment."""
from __future__ import annotations

import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
from typing import Any

from quality_trust import Cancellation, Invalid, OwnedProcess, runtime_python


class CommandInterrupted(KeyboardInterrupt):
    def __init__(self, code: int | None) -> None:
        self.code = code


def stop(process: OwnedProcess) -> bool:
    if not isinstance(process, OwnedProcess):
        return False
    try:
        return process.close()
    except (Invalid, OSError, KeyboardInterrupt):
        return False


def execute(check: dict[str, Any], snapshot: Path, state: Path, log: Path,
            cancellation: Cancellation | None = None, *, subject: Path) -> tuple[str, str, int, str, str]:
    cancellation = cancellation or Cancellation()
    with cancellation.handlers():
        return _execute(check, snapshot, state, log, cancellation, subject)


def _execute(check: dict[str, Any], snapshot: Path, state: Path, log: Path,
             cancellation: Cancellation, subject: Path) -> tuple[str, str, int, str, str]:
    process = OwnedProcess(cancellation, protected_roots=[subject, snapshot])
    try:
        return _execute_body(check, snapshot, state, log, cancellation, process)
    except KeyboardInterrupt:
        stop(process)
        raise CommandInterrupted(process.code) from None
    except (Invalid, OSError, ValueError):
        stop(process)
        code = process.code
        if code is not None and code >= 0:
            return ("pass" if code == 0 else "fail", "command-exited-zero" if code == 0 else "command-failed",
                    min(code, 255), "incomplete", "owned-output-or-finalization-unavailable")
        return "incomplete", "owned-output-or-finalization-unavailable", -1, "incomplete", "owned-group-cleanup-unverified"


def _execute_body(check: dict[str, Any], snapshot: Path, state: Path, log: Path,
                  cancellation: Cancellation, process: OwnedProcess) -> tuple[str, str, int, str, str]:
    state.mkdir(mode=0o700)
    for name in ("home", "tmp", "cache", "config", "data"):
        (state / name).mkdir(mode=0o700)
    env = {"PATH": str(Path(runtime_python(process.protected_roots)).parent) + ":" + os.defpath,
           "HOME": str(state / "home"), "TMPDIR": str(state / "tmp"),
           "TMP": str(state / "tmp"), "TEMP": str(state / "tmp"),
           "XDG_CACHE_HOME": str(state / "cache"), "XDG_CONFIG_HOME": str(state / "config"),
           "XDG_DATA_HOME": str(state / "data"), "QUALITY_STATE_ROOT": str(state),
           "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    stopped = False
    cleanup_complete = False
    def stop_owned() -> bool:
        nonlocal stopped, cleanup_complete
        if process is not None and not stopped:
            cleanup_complete = stop(process)
            stopped = True
        return cleanup_complete

    try:
        with log.open("xb") as output, selectors.DefaultSelector() as selector:
            process.start(check["argv"], cwd=snapshot, env=env,
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            assert process.stdout is not None
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdout, selectors.EVENT_READ)
            deadline = time.monotonic() + check["timeout_seconds"]
            size = 0
            def limited(reason: str) -> tuple[str, str, int, str, str]:
                observed = process.observe()
                stop_owned()
                # The final owned wait may reveal a racing natural exit; retain it.
                if process.code is not None and process.code >= 0:
                    observed = process.code
                if observed is not None and observed >= 0:
                    status = "pass" if observed == 0 else "fail"
                    outcome = "command-exited-zero" if observed == 0 else "command-failed"
                    return status, outcome, min(observed, 255), "incomplete", reason
                return "incomplete", reason, -1, "incomplete", reason

            while True:
                if cancellation.requested:
                    raise KeyboardInterrupt
                if time.monotonic() >= deadline:
                    return limited("command-timeout")
                events = selector.select(min(0.1, max(0, deadline - time.monotonic())))
                for key, _ in events:
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                    else:
                        remaining = check["max_log_bytes"] - size
                        output.write(chunk[:remaining])
                        size += len(chunk)
                        if size > check["max_log_bytes"]:
                            return limited("command-log-limit")
                if process.observe() is not None and not selector.get_map():
                    code = process.code
                    # Descendants must not outlive the owned check, even if they close stdout.
                    clean = stop_owned()
                    output = ("pass", "bounded-output-complete") if clean else ("incomplete", "owned-group-cleanup-unverified")
                    if code < 0:
                        return ("incomplete", "command-signal", -1) + output
                    return (("pass", "command-exited-zero", 0) if code == 0 else ("fail", "command-failed", min(code, 255))) + output
    except KeyboardInterrupt:
        observed = process.code
        stop_owned()
        if process is not None and process.code is not None and process.code >= 0:
            observed = process.code
        raise CommandInterrupted(observed) from None
    except (Invalid, OSError, ValueError):
        stop_owned()
        observed = process.code
        if observed is not None and observed >= 0:
            return ("pass" if observed == 0 else "fail", "command-exited-zero" if observed == 0 else "command-failed",
                    min(observed, 255), "incomplete", "owned-execution-observation-unavailable")
        return "incomplete", "owned-execution-observation-unavailable", -1, "incomplete", "owned-group-cleanup-unverified"
    finally:
        if process is not None:
            stop_owned()
            if process.stdout is not None:
                process.stdout.close()
