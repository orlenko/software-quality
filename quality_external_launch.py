"""Trusted outside-target protocol2 bootstrap; offline explicit imports only."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S quality_external_launch.py")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from quality_trust import EXTERNAL_VERSION, MAX_ARTIFACT, Git, Invalid, artifact, lock_value, regular_bytes, within, outside_path


def verify(data: bytes, digest: str, source: str) -> None:
    artifact(data, digest, source, version=EXTERNAL_VERSION, schema_version=2, entrypoint="quality/external_cli.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-protocol", type=int, choices=(2,), default=2)
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("install")
    install.add_argument("--artifact", type=Path, required=True)
    install.add_argument("--sha256", required=True)
    install.add_argument("--source", required=True)
    install.add_argument("--cache", type=Path, required=True)
    for name in ("doctor", "import"):
        child = commands.add_parser(name)
        for field in ("repo", "cache", "state"):
            child.add_argument("--" + field, type=Path, required=True)
        for field in ("base", "head", "identity"):
            child.add_argument("--" + field, required=True)
        child.add_argument("--trusted-head")
        child.add_argument("--plan")
        for prefix, actor in (("evidence", "producer"), ("observations", "observer")):
            child.add_argument("--" + prefix, type=Path)
            child.add_argument("--" + prefix + "-sha256")
            child.add_argument("--approved-" + actor)
    args = parser.parse_args()
    try:
        if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("unsupported-runtime")
        cache = args.cache.resolve()
        if args.cache.is_symlink():
            raise Invalid("symlink-cache-refused")
        if args.command == "install":
            data = regular_bytes(args.artifact, MAX_ARTIFACT)
            verify(data, args.sha256, args.source)
            cache.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = cache / (args.sha256 + ".pyz")
            if target.exists() or target.is_symlink():
                verify(regular_bytes(target, MAX_ARTIFACT), args.sha256, args.source)
            else:
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            print("installed " + args.sha256)
            return 0
        repo = args.repo.resolve(strict=True)
        tool = Path(__file__).resolve().parent
        outside_path(Path(__file__), [repo])
        outside_path(args.cache, [repo])
        outside_path(args.state, [repo, tool, cache])
        state = args.state.resolve()
        if any(within(path, repo) for path in (tool, cache, state)):
            raise Invalid("trusted-roots-must-be-outside-target")
        if within(state, cache) or within(cache, state) or within(state, tool) or within(tool, state):
            raise Invalid("trusted-roots-must-be-separate")
        git = Git(repo)
        base, head = git.commit(args.base), git.commit(args.head)
        pin = lock_value(git.blob(base, ".quality/lock.json"), version=EXTERNAL_VERSION, schema_version=2)
        package = cache / (pin["artifact_sha256"] + ".pyz")
        verify(regular_bytes(package, MAX_ARTIFACT), pin["artifact_sha256"], pin["source"])
        command = [sys.executable, "-I", "-S", str(package), args.command, "--repo", str(repo),
                   "--base", base, "--head", head, "--identity", args.identity, "--state", str(args.state),
                   "--artifact-sha256", pin["artifact_sha256"], "--source", pin["source"]]
        for field in ("trusted_head", "plan", "evidence", "evidence_sha256", "approved_producer",
                      "observations", "observations_sha256", "approved_observer"):
            value = getattr(args, field)
            if value is not None:
                # Retain lexical paths: the core checks both lexical and resolved roots.
                command.extend(["--" + field.replace("_", "-"), str(value)])
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
        return code if code in (0, 1, 2) else 2
    except (Invalid, OSError, ValueError, subprocess.SubprocessError):
        print("incomplete: protocol2-launch-unavailable (check approved pins and prerequisites)", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
