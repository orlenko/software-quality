"""Trusted local launcher. Approve this file and quality_trust.py out of band."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import signal

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("invoke with a trusted Python 3.11+ interpreter and -I -S")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_trust import (Cancellation, OwnedProcess, write_output, diagnostic, MAX_ARTIFACT, Git, Invalid, OID, artifact, lock_value,
                           regular_bytes, within, outside_path, runtime_python, raw_absolute, subject_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-protocol", type=int, choices=(1,), default=1)
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("install", help="explicit offline cache installation")
    install.add_argument("--artifact", type=Path, required=True)
    install.add_argument("--sha256", required=True)
    install.add_argument("--source", required=True)
    install.add_argument("--cache", type=Path, required=True)
    for name in ("check", "doctor"):
        child = commands.add_parser(name)
        child.add_argument("--repo", type=Path, required=True)
        child.add_argument("--base", required=True)
        child.add_argument("--head", required=True)
        child.add_argument("--identity", required=True)
        child.add_argument("--cache", type=Path, required=True)
        child.add_argument("--state", type=Path, required=True)
        child.add_argument("--execute-trusted", action="store_true")
        child.add_argument("--review", type=Path)
        child.add_argument("--review-sha256")
    args = parser.parse_args()
    cancellation = Cancellation()
    with cancellation.handlers():
        return launch_main(args, cancellation)


def launch_main(args: argparse.Namespace, cancellation: Cancellation) -> int:
    owned: OwnedProcess | None = None
    try:
        if os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("unsupported-runtime")
        repo = subject_root(args.repo) if args.command != "install" else None
        roots = [repo] if repo is not None else []
        tool = outside_path(Path(__file__), roots, strict=True).parent
        interpreter = runtime_python(roots)
        cache = outside_path(args.cache, [*roots, tool])
        if within(tool, cache) or (repo is not None and within(repo, cache)):
            raise Invalid("cache-roots-must-be-separate")
        if args.command == "install":
            path = outside_path(args.artifact, [], strict=True, final_symlink=False)
            data = regular_bytes(path, MAX_ARTIFACT)
            artifact(data, args.sha256, args.source)
            cache.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = cache / (args.sha256 + ".pyz")
            if target.exists() or target.is_symlink():
                artifact(regular_bytes(target, MAX_ARTIFACT), args.sha256, args.source)
            else:
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            if cancellation.requested:
                raise KeyboardInterrupt
            write_output(("installed " + args.sha256 + "\n").encode(), cancellation)
            return 2 if cancellation.requested else 0
        assert repo is not None
        state = outside_path(args.state, [repo, tool, cache])
        if any(within(root, state) for root in (repo, tool, cache)):
            raise Invalid("state-roots-must-be-separate")
        git = Git(repo)
        base, head = git.commit(args.base), git.commit(args.head)
        lock = lock_value(git.blob(base, ".quality/lock.json"))
        package = outside_path(cache / (lock["artifact_sha256"] + ".pyz"), [repo], strict=True, final_symlink=False)
        artifact(regular_bytes(package, MAX_ARTIFACT), lock["artifact_sha256"], lock["source"])
        command = [interpreter, "-I", "-S", str(package), args.command,
                   "--repo", str(repo), "--base", base, "--head", head,
                   "--identity", args.identity, "--state", str(state),
                   "--artifact-sha256", lock["artifact_sha256"], "--source", lock["source"]]
        if args.execute_trusted:
            command.append("--execute-trusted")
        if args.review:
            command.extend(["--review", str(raw_absolute(args.review))])
        if args.review_sha256:
            command.extend(["--review-sha256", args.review_sha256])
        owned = OwnedProcess(cancellation, protected_roots=[repo])
        try:
            owned.start(command, env={"PATH": os.defpath, "LC_ALL": "C"})
            code = owned.wait()
        finally:
            cleaned = owned.close()
        if code == 1:
            return 1
        if cancellation.requested or not cleaned:
            diagnostic("incomplete: owned-launch-cancelled-or-cleanup-unverified", cancellation)
            return 2
        if code not in (0, 1, 2):
            diagnostic("incomplete: runner-terminated (inspect the initial run report)", cancellation)
            return 2
        return code
    except (Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        if owned is not None and owned.code == 1:
            return 1
        diagnostic("incomplete: trusted-launch-failed (check pins, paths and prerequisites)", cancellation)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
