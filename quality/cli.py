"""Explicit immutable-target CLI. No PR/provider discovery or target launchers."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys

from quality_trust import MAX_ARTIFACT, Invalid, artifact, regular_bytes, sha
from quality.runner import run


def interrupted(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "doctor"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--execute-trusted", action="store_true")
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-sha256")
    parser.add_argument("--experimental-source", action="store_true")
    args = parser.parse_args()
    try:
        if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("isolated-posix-python-3.11-required")
        if not args.experimental_source:
            artifact(regular_bytes(Path(sys.argv[0]), MAX_ARTIFACT), args.artifact_sha256, args.source)
        signal.signal(signal.SIGTERM, interrupted)
        report, path = run(args, args.artifact_sha256, args.source, args.experimental_source)
        print("report " + str(path))
        print(report["overall"])
        return {"pass": 0, "fail": 1, "incomplete": 2}[report["overall"]]
    except Invalid as exc:
        print("incomplete: " + str(exc), file=sys.stderr)
        return 2
    except (OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        print("incomplete: input-or-runtime-unavailable", file=sys.stderr)
        return 2
