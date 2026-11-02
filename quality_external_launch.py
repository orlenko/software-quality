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

from quality_trust import Cancellation, OwnedProcess, write_output, diagnostic, EXTERNAL_VERSION, MAX_ARTIFACT, Git, Invalid, artifact, lock_value, regular_bytes, within, outside_path, runtime_python, raw_absolute, subject_root


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
    cancellation = Cancellation()
    with cancellation.handlers():
        return launch_main(args, cancellation)


def launch_main(args: argparse.Namespace, cancellation: Cancellation) -> int:
    owned: OwnedProcess | None = None
    try:
        if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("unsupported-runtime")
        repo = subject_root(args.repo) if args.command != "install" else None
        roots = [repo] if repo is not None else []
        tool = outside_path(Path(__file__), roots, strict=True).parent
        interpreter = runtime_python(roots)
        cache = outside_path(args.cache, [*roots, tool], final_symlink=False)
        if within(tool, cache) or (repo is not None and within(repo, cache)):
            raise Invalid("cache-roots-must-be-separate")
        if args.command == "install":
            path = outside_path(args.artifact, [], strict=True, final_symlink=False)
            data = regular_bytes(path, MAX_ARTIFACT)
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
            if cancellation.requested:
                raise KeyboardInterrupt
            write_output(("installed " + args.sha256 + "\n").encode(), cancellation)
            return 2 if cancellation.requested else 0
        assert repo is not None
        state = outside_path(args.state, [repo, tool, cache], final_symlink=False)
        if any(within(path, repo) for path in (tool, cache, state)):
            raise Invalid("trusted-roots-must-be-outside-target")
        if within(state, cache) or within(cache, state) or within(state, tool) or within(tool, state):
            raise Invalid("trusted-roots-must-be-separate")
        git = Git(repo)
        base, head = git.commit(args.base), git.commit(args.head)
        pin = lock_value(git.blob(base, ".quality/lock.json"), version=EXTERNAL_VERSION, schema_version=2)
        package = outside_path(cache / (pin["artifact_sha256"] + ".pyz"), [repo], strict=True, final_symlink=False)
        verify(regular_bytes(package, MAX_ARTIFACT), pin["artifact_sha256"], pin["source"])
        command = [interpreter, "-I", "-S", str(package), args.command, "--repo", str(repo),
                   "--base", base, "--head", head, "--identity", args.identity, "--state", str(state),
                   "--artifact-sha256", pin["artifact_sha256"], "--source", pin["source"]]
        for field in ("trusted_head", "plan", "evidence", "evidence_sha256", "approved_producer",
                      "observations", "observations_sha256", "approved_observer"):
            value = getattr(args, field)
            if value is not None:
                # Retain lexical paths: the core checks both lexical and resolved roots.
                if field in ("evidence", "observations"):
                    value = raw_absolute(value)
                command.extend(["--" + field.replace("_", "-"), str(value)])
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
        return code if code in (0, 1, 2) else 2
    except (Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        if owned is not None and owned.code == 1:
            return 1
        diagnostic("incomplete: protocol2-launch-unavailable (check approved pins and prerequisites)", cancellation)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
