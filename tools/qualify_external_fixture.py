"""One owned fixture only. Static review and exact-source owner approval precede use."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any

SOURCE = "70a054bcbc77605d1d4f7c5a2fdc2af30c33705a"
ZIP_SHA = "958a5261f752e523eec74a75ffa3719b1536f966a67db3a482d5e5bd6e9b1cd4"
BOOT_SHA = "e70106e7c7d6027f4b9901eb8e7559ea40e00ef994fa49bf532d7c05ee5b876f"
TRUST_SHA = "8799e4706394735e3dc2dc700fa05c09fe05ab5455cf5b1c0b3f2d7b15487a63"
CASES = ("pass", "fail", "timeout", "interrupt")
STAGES = ["parse", "sum", "compare"]
BUDGET = 3
GRACE = 1
BOOT: str | None = None


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def read_json(path: Path) -> Any:
    data = path.read_bytes()
    if len(data) > 65536:
        raise ValueError("fixture-data-too-large")
    return json.loads(data)


def write(path: Path, value: Any) -> None:
    data = encoded(value)
    temporary = path.with_name(path.name + ".partial")
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Atomic publication without replacing old evidence.
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def environment(case: Path) -> dict[str, str]:
    return {"PATH": os.defpath, "HOME": str(case / "temp"), "TMPDIR": str(case / "temp"), "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
            "__CF_USER_TEXT_ENCODING": "0x" + format(os.getuid(), "X") + ":0x0:0x0"}


def runtime(case: Path, *, observed: bool = False) -> dict[str, Any]:
    return {"interpreter_sha256": digest(Path(sys.executable).read_bytes()), "version": sys.version,
            "isolated": sys.flags.isolated, "no_site": sys.flags.no_site, "environment": dict(os.environ) if observed else environment(case)}


def command(argv: list[str], case: Path, codes: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(argv, env=environment(case), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    if result.returncode not in codes or max(len(result.stdout), len(result.stderr)) > 65536:
        raise ValueError("fixture-helper-failed")
    return result


def pin(root: Path) -> dict[str, Any]:
    if (root.is_symlink() or root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077
            or not root.name.startswith("software-quality-real-fixture-")):
        raise ValueError("owned-private-fixture-root-required")
    if Path(__file__).resolve() != root / "harness" / "qualify_external_fixture.py":
        raise ValueError("approved-copy-entry-required")
    profile = read_json(root / "harness" / "profile.json")
    if (digest((root / "harness" / "qualify_external_fixture.py").read_bytes()) != profile["harness_sha256"]
            or digest((root / "harness" / "gate.py").read_bytes()) != profile["gate_sha256"]
            or digest((root / "frozen" / "candidate.pyz").read_bytes()) != ZIP_SHA
            or digest((root / "frozen" / "quality_external_launch.py").read_bytes()) != BOOT_SHA
            or digest((root / "frozen" / "quality_trust.py").read_bytes()) != TRUST_SHA):
        raise ValueError("fixture-approved-bytes-mismatch")
    return profile


def bootstrap(root: Path, case: Path, verb: str, extra: list[str] | None = None) -> list[str]:
    args = [sys.executable, "-I", "-S", str(root / "frozen" / "quality_external_launch.py"),
            "--adapter-protocol", "2", verb]
    if verb == "install":
        return args + ["--artifact", str(root / "frozen" / "candidate.pyz"), "--sha256", ZIP_SHA,
                       "--source", SOURCE, "--cache", str(case / "cache")]
    identities = read_json(case / "identities.json")
    return args + ["--repo", str(root / "subject"), "--base", identities["head"], "--head", identities["head"],
                   "--trusted-head", identities["head"], "--identity", "example/real-executed-fixture",
                   "--cache", str(case / "cache"), "--state", str(case / "state")] + (extra or [])


def prepare(root: Path, profile: dict[str, Any]) -> None:
    target = root / "subject"
    target.mkdir(mode=0o700)
    for name in CASES:
        case = root / name
        case.mkdir(mode=0o700)
        for child in ("temp", "producer", "controller"):
            (case / child).mkdir(mode=0o700)
        def git(*args: str) -> str:
            return command(["/usr/bin/git", "-c", "core.hooksPath=" + os.devnull, "-C", str(target), *args], case).stdout.decode().strip()
        if name == "pass":
            git("init", "-b", "main")
            git("config", "user.name", "Invented Fixture")
            git("config", "user.email", "fixture@example.invalid")
        (target / "gate.py").write_bytes((root / "harness" / "gate.py").read_bytes())
        (target / "input.json").write_bytes(encoded({"values": [2, 4, 6], "expected": 13 if name == "fail" else 12,
                                                     "block_seconds": 10 if name in ("timeout", "interrupt") else 0}))
        (target / ".quality").mkdir(mode=0o700, exist_ok=True)
        fingerprint = digest(encoded(runtime(case)))
        config = {"schema_version": 2, "repository": "example/real-executed-fixture", "gate": {
            "id": "sum", "producer_id": "owned-fixture-producer", "observer_id": "owned-fixture-controller",
            "canonical_sha256": profile["gate_sha256"], "coverage_sha256": digest(encoded(STAGES)),
            "environment_sha256": fingerprint,
            "mechanism": {"id": "serialized-inputs", "sha256": digest(encoded(profile["consumption"]))},
            "observer": {"profile_sha256": digest(encoded(profile)), "mechanism_sha256": digest(encoded(profile["supervision"]))},
            "trust_rule": "owner-designation-permitted", "required_controls": ["deadline", "cleanup"],
            "allowed_effects": ["read-source", "read-git-metadata", "disposable-files"], "refs": ["refs/heads/main"],
            "budget_seconds": BUDGET, "import_window_seconds": 60}, "unsupported_obligations": []}
        (target / ".quality/config.json").write_bytes(encoded(config))
        (target / ".quality/lock.json").write_bytes(encoded({"schema_version": 2, "publisher": "orlenko/software-quality",
            "source": SOURCE, "artifact_sha256": ZIP_SHA, "version": "0.2.0", "policy_version": "0.1"}))
        git("add", ".")
        git("commit", "-m", "Newly authored invented fixture")
        write(case / "identities.json", {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
                                          "runtime_sha256": fingerprint})
        command(bootstrap(root, case, "install"), case)
    print("prepared-one-owned-subject-four-commits", flush=True)


def issued(root: Path, case: Path) -> dict[str, Any]:
    result = command(bootstrap(root, case, "doctor"), case, (2,))
    output = json.loads(result.stdout)
    write(case / "doctor.json", output)
    # This is the actual issued state, not a reconstructed challenge/context.
    handoff = read_json(Path(output["record"]))
    write(case / "handoff.json", handoff)
    return handoff


def clock() -> Any:
    global BOOT
    from quality.external_clock import read, Reading
    if BOOT is None:
        BOOT = read().boot_sha256
    # A live process cannot survive a host reboot; do not launch boot helpers
    # in the finite-deadline polling/signal path. Timestamps are fresh OS reads.
    return Reading(time.time_ns() // 1000000, time.monotonic_ns() // 1000000, BOOT)


def gate(root: Path, case: Path, profile: dict[str, Any]) -> int:
    raw = sys.stdin.buffer.read(32769)
    if len(raw) > 32768:
        raise ValueError("oversized-captured-frame")
    frame = json.loads(raw)
    code = base64.b64decode(frame["source"], validate=True)
    data = base64.b64decode(frame["input"], validate=True)
    if digest(code) != profile["gate_sha256"] or len(data) > 2048:
        raise ValueError("unapproved-gate-bytes")
    namespace: dict[str, Any] = {}
    origin = "git:" + frame["head"] + ":gate.py"
    exec(compile(code, origin, "exec"), namespace)
    actual_runtime = runtime(case, observed=True)
    intake = {"actual_runtime": actual_runtime, "source_sha256": digest(code), "input_sha256": digest(data), "frame_sha256": digest(raw),
              "origin": namespace["check"].__code__.co_filename, "head": frame["head"], "tree": frame["tree"],
              "runtime_sha256": digest(encoded(actual_runtime)), "pid": os.getpid(), "pgid": os.getpgrp()}
    def parsed() -> None:
        reading = clock()
        write(case / "producer" / "intake.json", {**intake, "stage": "parse", "wall_ms": reading.wall_ms, "mono_ms": reading.mono_ms})
        print(encoded({"intake": intake, "stages": ["parse"]}).decode(), end="", flush=True)
    code, stages = namespace["check"](data, parsed, json, time)
    print(encoded({"completed": stages, "exit_code": code}).decode(), end="", flush=True)
    return code


def producer(root: Path, case: Path, profile: dict[str, Any]) -> int:
    from quality_trust import Git, canonical, sha
    from quality.external_model import subject
    handoff = read_json(case / "handoff.json")
    ids = read_json(case / "identities.json")
    interrupted = False
    def cancellation(signum: int, frame: object) -> None:
        nonlocal interrupted
        interrupted = True
    signal.signal(signal.SIGTERM, cancellation)
    signal.signal(signal.SIGINT, cancellation)
    start = clock()
    if start.mono_ms <= handoff["issued_mono_ms"] or start.wall_ms <= handoff["issued_wall_ms"]:
        raise ValueError("not-after-issuance")
    git = Git(root / "subject")
    before, registry = subject(git, ids["head"], ids["head"], "example/real-executed-fixture", ZIP_SHA, SOURCE, True, start)
    source = git.blob(ids["head"], "gate.py")
    data = git.blob(ids["head"], "input.json")
    packet = encoded({"source": base64.b64encode(source).decode(), "input": base64.b64encode(data).decode(),
                      "head": ids["head"], "tree": git.tree(ids["head"])})
    write(case / "producer" / "start.json", {"pid": os.getpid(), "pgid": os.getpgrp(), "wall_ms": start.wall_ms, "mono_ms": start.mono_ms})
    if interrupted:
        write(case / "producer" / "wait.json", {"gate_started": False, "gate_pid": 0,
            "gate_reaped": False, "signal_received": True, "completed_stages": []})
        return 0
    events: list[dict[str, Any]] = []
    with (case / "producer" / "stdout.log").open("xb") as output_log, (case / "producer" / "stderr.log").open("xb") as error_log:
        child = subprocess.Popen([sys.executable, "-I", "-S", str(root / "harness" / "qualify_external_fixture.py"),
            "gate", "--root", str(root), "--case", case.name], env=environment(case),
            stdin=subprocess.PIPE, stdout=output_log, stderr=error_log)
        try:
            assert child.stdin is not None
            child.stdin.write(packet)
            child.stdin.close()
            while not exited_unreaped(child) and not interrupted:
                time.sleep(0.005)
        finally:
            try:
                if child.stdin is not None and not child.stdin.closed:
                    child.stdin.close()
            finally:
                gate_code = settle(child, events, group=False)
    output = (case / "producer" / "stdout.log").read_bytes()
    errors = (case / "producer" / "stderr.log").read_bytes()
    if len(output) + len(errors) > 65536:
        raise ValueError("gate-output-too-large")
    intake = read_json(case / "producer" / "intake.json") if (case / "producer" / "intake.json").exists() else None
    lines = [json.loads(line) for line in output.splitlines()]
    completion = next((item for item in lines if "completed" in item), None)
    after, _ = subject(git, ids["head"], ids["head"], "example/real-executed-fixture", ZIP_SHA, SOURCE, True, clock())
    finish = clock()
    valid = bool(intake and intake["source_sha256"] == digest(source) and intake["input_sha256"] == digest(data)
                 and intake["frame_sha256"] == digest(packet) and intake["origin"] == "git:" + ids["head"] + ":gate.py"
                 and intake["tree"] == git.tree(ids["head"]) and intake["runtime_sha256"] == ids["runtime_sha256"])
    completed = bool(completion and completion["completed"] == STAGES and completion["exit_code"] == gate_code and gate_code in (0, 7))
    outcome = "completed" if completed else "terminated" if gate_code < 0 else "wrapper-error"
    gate_config = registry["gate"]
    record = {"gate_id": "sum", "producer_id": "owned-fixture-producer", "invocation_id": handoff["plan_id"],
        "canonical_sha256": digest(source), "phase": "known-commit", "features": [],
        "coverage": {"kind": "whole" if completed else "partial", "sha256": digest(encoded(completion["completed"] if completed else ["parse"] if intake else []))},
        "consumed": {"mechanism_id": "serialized-inputs", "mechanism_sha256": gate_config["mechanism"]["sha256"],
            "established": valid, "before_context_sha256": sha(canonical(before)), "after_context_sha256": sha(canonical(after)),
            "origin_tree": intake["tree"] if intake else "0"*40, "environment_sha256": intake["runtime_sha256"] if intake else "0"*64,
            "provenance": "trusted-local"}, "outcome": {"kind": outcome, "exit_code": gate_code if completed else -1},
        "timing": {"clock": {"model": "same-host-boot-ms-v1", "boot_sha256": start.boot_sha256},
            "started_ms": start.wall_ms, "finished_ms": finish.wall_ms, "started_mono_ms": start.mono_ms,
            "finished_mono_ms": finish.mono_ms, "elapsed_ms": finish.mono_ms-start.mono_ms},
        "effects": ["read-source", "read-git-metadata", "disposable-files"], "output_complete": not errors,
        "note": "Measured owned fixture; logical compiled Git origin; no OS containment/independence claim."}
    write(case / "producer" / "receipt.json", {"schema_version": 2, "protocol": "external-checks-v1", "plan_id": handoff["plan_id"],
        "challenge": handoff["challenge"], "context_sha256": handoff["context_sha256"], "records": [record]})
    write(case / "producer" / "wait.json", {"gate_started": True, "gate_pid": child.pid, "gate_returncode": gate_code, "gate_reaped": True, "events": events,
        "signal_received": interrupted, "completed_stages": completion["completed"] if completed else ["parse"] if intake else []})
    return 0


def exited_unreaped(child: subprocess.Popen[Any]) -> bool:
    return os.waitid(os.P_PID, child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None


def settle(child: subprocess.Popen[Any], events: list[dict[str, Any]], *, group: bool, grace: int = GRACE) -> int:
    """Final signaling while PID is reserved; reap exactly after that capability ends."""
    def send(sig: int) -> None:
        reading = clock()
        try:
            (os.killpg if group else os.kill)(child.pid, sig)
            sent = True
        except ProcessLookupError:
            sent = False
        events.append({"signal": sig, "sent": sent, "wall_ms": reading.wall_ms, "mono_ms": reading.mono_ms})
    # waitid(WNOWAIT) confirms ownership without Popen's implicit reaping.
    try:
        exited = exited_unreaped(child)
        if not exited:
            send(signal.SIGTERM)
            until = time.monotonic() + grace
            while not exited_unreaped(child) and time.monotonic() < until:
                time.sleep(0.005)
        if not exited_unreaped(child):
            send(signal.SIGKILL)
    finally:
        # Even a signaling/observation exception must attempt the owned child's wait.
        code = child.wait(timeout=grace)
    return code


def controller(root: Path, case: Path, profile: dict[str, Any]) -> int:
    handoff = read_json(case / "handoff.json")
    cancel = False
    def cancellation(signum: int, frame: object) -> None:
        nonlocal cancel
        cancel = True
    signal.signal(signal.SIGINT, cancellation)
    signal.signal(signal.SIGTERM, cancellation)
    began = clock()
    deadline_wall, deadline_mono = began.wall_ms + BUDGET*1000, began.mono_ms + BUDGET*1000
    events: list[dict[str, Any]] = []
    child: subprocess.Popen[Any] | None = None
    reason = "completed"
    ownership_verified = False
    checks: list[dict[str, int]] = []
    write(case / "controller" / "armed.json", {"wall_ms": began.wall_ms, "mono_ms": began.mono_ms,
        "deadline_wall_ms": deadline_wall, "deadline_mono_ms": deadline_mono})
    with (case / "controller" / "producer.log").open("xb") as log:
        try:
            if cancel:
                raise ValueError("cancelled-before-producer-launch")
            child = subprocess.Popen([sys.executable, "-I", "-S", str(root / "harness" / "qualify_external_fixture.py"),
                "producer", "--root", str(root), "--case", case.name], env=environment(case), stdin=subprocess.DEVNULL,
                stdout=log, stderr=log, start_new_session=True)
            write(case / "controller" / "owned.json", {"controller_pid": os.getpid(), "producer_pid": child.pid, "producer_pgid": child.pid})
            ownership_verified = os.getpgid(child.pid) == child.pid
            if not ownership_verified:
                raise ValueError("wrong-owned-producer-group")
            ready = False
            while not exited_unreaped(child):
                observed = clock()
                checks.append({"wall_ms": observed.wall_ms, "mono_ms": observed.mono_ms})
                if not ready and (case / "producer" / "intake.json").exists():
                    intake = read_json(case / "producer" / "intake.json")
                    if intake["stage"] != "parse" or intake["pgid"] != child.pid:
                        raise ValueError("wrong-observed-intake")
                    write(case / "controller" / "ready.json", {"controller_pid": os.getpid(), "gate_pid": intake["pid"]})
                    ready = True
                if cancel or observed.mono_ms >= deadline_mono:
                    reason = "interrupted" if cancel else "deadline"
                    break
                time.sleep(0.005)
        finally:
            if child is not None:
                producer_code = settle(child, events, group=True)
    cleaned = clock()
    group_empty = False
    try:
        os.killpg(child.pid, 0)  # Observation only after releasing leader ownership.
    except ProcessLookupError:
        group_empty = True
    waited = read_json(case / "producer" / "wait.json") if (case / "producer" / "wait.json").exists() else None
    cleanup = bool(group_empty and producer_code == 0 and waited
                   and (waited["gate_reaped"] or waited.get("gate_started") is False))
    armed = bool(ownership_verified and began.mono_ms < deadline_mono and checks)
    action_observed = reason == "completed" or any(item["sent"] and item["signal"] == signal.SIGTERM for item in events)
    deadline_observed = armed and action_observed
    # Observe both clocks beyond the declared precision margin, never restamp.
    through = clock()
    while through.wall_ms < cleaned.wall_ms+1 or through.mono_ms < cleaned.mono_ms+1:
        time.sleep(0.001)
        through = clock()
    write(case / "controller" / "raw.json", {"reason": reason, "events": events, "producer_code": producer_code,
        "group_empty": group_empty, "cleanup_complete": cleanup, "gate_wait": waited,
        "owned_pgid_verified": ownership_verified, "deadline_armed": armed,
        "deadline_wall_ms": deadline_wall, "deadline_mono_ms": deadline_mono, "checks": checks,
        "began": began.__dict__, "cleaned": cleaned.__dict__, "through": through.__dict__})
    write(case / "controller" / "receipt.json", {"schema_version": 2, "protocol": "external-controls-v1",
        "plan_id": handoff["plan_id"], "challenge": handoff["challenge"], "context_sha256": handoff["context_sha256"],
        "gate_id": "sum", "invocation_id": handoff["plan_id"], "observer_id": "owned-fixture-controller",
        "profile_sha256": digest(encoded(profile)), "mechanism_sha256": digest(encoded(profile["supervision"])),
        "source_route": "independent-controller", "basis": "controller-observation", "clock": handoff["context"]["clock"],
        "observed_from_ms": began.wall_ms, "observed_from_mono_ms": began.mono_ms,
        "observed_through_ms": through.wall_ms, "observed_through_mono_ms": through.mono_ms,
        "cleanup_at_ms": cleaned.wall_ms, "cleanup_at_mono_ms": cleaned.mono_ms,
        "deadline_at_ms": deadline_wall, "deadline_at_mono_ms": deadline_mono,
        "cleanup_state": "complete" if cleanup else "unknown",
        "observations": [{"kind": "deadline", "state": "enforced" if deadline_observed else "unknown", "measurement_ref": "controller/raw.json: real finite monotonic deadline and signal loop"},
                         {"kind": "cleanup", "state": "enforced" if cleanup else "unknown", "measurement_ref": "controller/raw.json: owned wait results and empty group"}]})
    return 0 if cleanup else 2


def run_case(root: Path, case: Path, profile: dict[str, Any]) -> int:
    ids = read_json(case / "identities.json")
    command(["/usr/bin/git", "-c", "core.hooksPath=" + os.devnull, "-C", str(root / "subject"),
             "reset", "--hard", ids["head"]], case)
    issued(root, case)
    cancelled = False
    def cancellation(signum: int, frame: object) -> None:
        nonlocal cancelled
        cancelled = True
    signal.signal(signal.SIGTERM, cancellation)
    signal.signal(signal.SIGINT, cancellation)
    sent = False
    events: list[dict[str, Any]] = []
    with (case / "driver.log").open("xb") as log:
        if cancelled:
            raise ValueError("cancelled-before-controller-launch")
        child = subprocess.Popen([sys.executable, "-I", "-S", str(root / "harness" / "qualify_external_fixture.py"),
            "controller", "--root", str(root), "--case", case.name], env=environment(case),
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        try:
            until = time.monotonic() + BUDGET + 2*GRACE + 4
            while not exited_unreaped(child) and time.monotonic() < until and not cancelled:
                if case.name == "interrupt" and not sent and (case / "controller" / "ready.json").exists():
                    ready = read_json(case / "controller" / "ready.json")
                    if ready["controller_pid"] != child.pid:
                        raise ValueError("wrong-owned-controller")
                    if exited_unreaped(child):
                        break
                    when = clock()
                    os.kill(child.pid, signal.SIGINT)
                    write(case / "interrupt.json", {"controller_pid": child.pid, "signal": signal.SIGINT,
                        "wall_ms": when.wall_ms, "mono_ms": when.mono_ms})
                    sent = True
                time.sleep(0.005)
        finally:
            code = settle(child, events, group=False, grace=2*GRACE+1)
    raw_path = case / "controller" / "raw.json"
    observed_cleanup = raw_path.exists() and read_json(raw_path)["cleanup_complete"] is True
    write(case / "driver.json", {"controller_pid": child.pid, "controller_reaped": True, "returncode": code,
        "actual_sigint_sent": sent, "ready_observed": (case / "controller" / "ready.json").exists(),
        "root_cancelled": cancelled, "events": events, "controller_cleanup_observed": observed_cleanup})
    if cancelled:
        raise ValueError("root-cancelled-qualification-incomplete")
    if not observed_cleanup or (case.name == "interrupt" and (not sent or read_json(raw_path)["reason"] != "interrupted")):
        raise ValueError("fixture-cleanup-or-interruption-unverified")
    print(encoded({"case": case.name, "controller_returncode": code, "actual_sigint_sent": sent}).decode(), end="", flush=True)
    return code


def main() -> int:
    if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix":
        raise ValueError("isolated-posix-runtime-required")
    if not all(hasattr(os, name) for name in ("waitid", "WNOWAIT", "WEXITED", "WNOHANG", "P_PID")):
        raise ValueError("non-reaping-owned-child-observation-unavailable")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("prepare", "run", "controller", "producer", "gate"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--case", choices=CASES)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    profile = pin(root)
    sys.path.insert(0, str(root / "frozen" / "candidate.pyz"))
    if args.role == "prepare":
        prepare(root, profile)
        return 0
    if args.case is None:
        raise ValueError("fixture-case-required")
    return {"run": run_case, "controller": controller, "producer": producer, "gate": gate}[args.role](root, root / args.case, profile)


if __name__ == "__main__":
    raise SystemExit(main())
