"""Explicit immutable-target CLI. No PR/provider discovery or target launchers."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys

from quality_trust import Cancellation, write_output, MAX_ARTIFACT, Invalid, artifact, regular_bytes, sha
from quality.runner import run


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
    args.cancellation = Cancellation()
    with args.cancellation.handlers():
        return run_main(args)


def run_main(args: argparse.Namespace) -> int:
    try:
        if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("isolated-posix-python-3.11-required")
        if not args.experimental_source:
            artifact(regular_bytes(Path(sys.argv[0]), MAX_ARTIFACT), args.artifact_sha256, args.source)
        report, path = run(args, args.artifact_sha256, args.source, args.experimental_source)
        if args.cancellation.requested and report["overall"] != "fail":
            from quality.evidence import stage, save
            report["stages"].append(stage("cancellation", reason="handled-cancellation"))
            report["overall"] = "incomplete"
            save(path, report)
        code = {"pass": 0, "fail": 1, "incomplete": 2}[report["overall"]]
        write_output(("report " + str(path) + "\n" + report["overall"] + "\n").encode(), args.cancellation,
                     known_failure=code == 1)
        return 1 if code == 1 else 2 if args.cancellation.requested else code
    except (Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        from quality.evidence import verdict
        report = getattr(args, "_validated_report", None)
        known = report is not None and verdict(report["stages"]) == "fail"
        message = b"fail: validated result retained; report persistence/delivery unconfirmed\n" if known else b"incomplete: input/runtime or report delivery unavailable\n"
        if not known and isinstance(exc, Invalid):
            message = ("incomplete: " + str(exc) + "\n").encode()
        try:
            write_output(message, args.cancellation, fd=2, seconds=0.1, known_failure=True)
        except (OSError, KeyboardInterrupt):
            pass
        return 1 if known else 2
