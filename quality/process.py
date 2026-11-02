"""Bounded trusted-local command execution; explicitly not containment."""
from __future__ import annotations

import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
from typing import Any


class CommandInterrupted(KeyboardInterrupt):
    def __init__(self, code: int | None) -> None:
        self.code = code


def stop(process: subprocess.Popen[bytes]) -> bool:
    complete = True
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        complete = False
        try:
            process.kill()
        except OSError:
            pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        complete = False
    return complete


def execute(check: dict[str, Any], snapshot: Path, state: Path, log: Path) -> tuple[str, str, int, str, str]:
    state.mkdir(mode=0o700)
    for name in ("home", "tmp", "cache", "config", "data"):
        (state / name).mkdir(mode=0o700)
    env = {"PATH": str(Path(sys.executable).parent) + ":" + os.defpath,
           "HOME": str(state / "home"), "TMPDIR": str(state / "tmp"),
           "TMP": str(state / "tmp"), "TEMP": str(state / "tmp"),
           "XDG_CACHE_HOME": str(state / "cache"), "XDG_CONFIG_HOME": str(state / "config"),
           "XDG_DATA_HOME": str(state / "data"), "QUALITY_STATE_ROOT": str(state),
           "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    process: subprocess.Popen[bytes] | None = None
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
            process = subprocess.Popen(check["argv"], cwd=snapshot, env=env,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            assert process.stdout is not None
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdout, selectors.EVENT_READ)
            deadline = time.monotonic() + check["timeout_seconds"]
            size = 0
            def limited(reason: str) -> tuple[str, str, int, str, str]:
                observed = process.poll()
                stop_owned()
                # wait() may reveal an exit racing with poll(). Never discard it.
                if process.returncode is not None and process.returncode >= 0:
                    observed = process.returncode
                if observed is not None and observed >= 0:
                    status = "pass" if observed == 0 else "fail"
                    outcome = "command-exited-zero" if observed == 0 else "command-failed"
                    return status, outcome, min(observed, 255), "incomplete", reason
                return "incomplete", reason, -1, "incomplete", reason

            while True:
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
                if process.poll() is not None and not selector.get_map():
                    code = process.returncode
                    # Descendants must not outlive the owned check, even if they close stdout.
                    clean = stop_owned()
                    output = ("pass", "bounded-output-complete") if clean else ("incomplete", "owned-group-cleanup-unverified")
                    if code < 0:
                        return ("incomplete", "command-signal", -1) + output
                    return (("pass", "command-exited-zero", 0) if code == 0 else ("fail", "command-failed", min(code, 255))) + output
    except KeyboardInterrupt:
        observed = process.poll() if process is not None else None
        stop_owned()
        if process is not None and process.returncode is not None and process.returncode >= 0:
            observed = process.returncode
        raise CommandInterrupted(observed) from None
    finally:
        if process is not None:
            stop_owned()
            if process.stdout is not None:
                process.stdout.close()
