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
from quality_trust import (MAX_ARTIFACT, Git, Invalid, OID, artifact, lock_value,
                           regular_bytes, within)


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
    try:
        if os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("unsupported-runtime")
        cache = args.cache.resolve()
        if args.command == "install":
            data = regular_bytes(args.artifact, MAX_ARTIFACT)
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
            print("installed " + args.sha256)
            return 0
        repo = args.repo.resolve(strict=True)
        if within(Path(__file__), repo) or within(cache, repo) or within(args.state, repo):
            raise Invalid("trusted-paths-must-be-outside-target")
        if within(args.state, cache) or within(cache, args.state):
            raise Invalid("cache-and-state-must-be-separate")
        git = Git(repo)
        base, head = git.commit(args.base), git.commit(args.head)
        lock = lock_value(git.blob(base, ".quality/lock.json"))
        package = cache / (lock["artifact_sha256"] + ".pyz")
        artifact(regular_bytes(package, MAX_ARTIFACT), lock["artifact_sha256"], lock["source"])
        command = [sys.executable, "-I", "-S", str(package), args.command,
                   "--repo", str(repo), "--base", base, "--head", head,
                   "--identity", args.identity, "--state", str(args.state.resolve()),
                   "--artifact-sha256", lock["artifact_sha256"], "--source", lock["source"]]
        if args.execute_trusted:
            command.append("--execute-trusted")
        if args.review:
            command.extend(["--review", str(args.review.resolve())])
        if args.review_sha256:
            command.extend(["--review-sha256", args.review_sha256])
        with subprocess.Popen(command, env={"PATH": os.defpath, "LC_ALL": "C"}) as process:
            def forward(signum: int, frame: object) -> None:
                try:
                    process.send_signal(signum)
                except ProcessLookupError:
                    pass
            previous = signal.signal(signal.SIGTERM, forward)
            try:
                try:
                    code = process.wait()
                except KeyboardInterrupt:
                    forward(signal.SIGINT, None)
                    code = process.wait()
            finally:
                signal.signal(signal.SIGTERM, previous)
        if code not in (0, 1, 2):
            print("incomplete: runner-terminated (inspect the initial run report)", file=sys.stderr)
            return 2
        return code
    except (Invalid, OSError, ValueError, subprocess.SubprocessError):
        print("incomplete: trusted-launch-failed (check pins, paths and prerequisites)", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
