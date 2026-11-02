"""Pinned schema2 import-only CLI. A report never claims importer execution."""
from __future__ import annotations

import argparse
from pathlib import Path
import os
import signal
import sys
import subprocess

from quality_trust import Cancellation, write_output, EXTERNAL_VERSION, MAX_ARTIFACT, Git, Invalid, artifact, canonical, regular_bytes
from quality.evidence import target_lock
from quality.external_clock import read
from quality.external_model import metadata, subject
from quality.external_store import ImportStorageFailure, ImportOutcome, create, gap, checkpoint, receive, state_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "import"))
    for name in ("repo", "state"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("base", "head", "identity", "artifact-sha256", "source"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--trusted-head")
    parser.add_argument("--plan")
    for prefix, actor in (("evidence", "producer"), ("observations", "observer")):
        parser.add_argument("--" + prefix, type=Path)
        parser.add_argument("--" + prefix + "-sha256")
        parser.add_argument("--approved-" + actor)
    args = parser.parse_args()
    cancellation = Cancellation()
    with cancellation.handlers():
        return import_main(args, cancellation)


def emit(state: dict, root: Path, cancellation: Cancellation) -> None:
    data = canonical({"protocol_version": 2, "plan_id": state["plan_id"], "challenge": state["challenge"],
        "context_sha256": state["context_sha256"], "record": str(root / state["plan_id"] / "record.json"), "report": state["report"]})
    write_output(data, cancellation, known_failure=state["report"]["overall"] == "fail",
                 allow_cancelled=state["report"]["overall"] == "incomplete")


def import_main(args: argparse.Namespace, cancellation: Cancellation) -> int:
    outcome = ImportOutcome()
    delivering = False
    root = args.state
    try:
        if not sys.flags.isolated or not sys.flags.no_site or os.name != "posix" or sys.version_info < (3, 11):
            raise Invalid("unsupported-runtime")
        package = Path(sys.argv[0]).resolve(strict=True)
        artifact(regular_bytes(package, MAX_ARTIFACT), args.artifact_sha256, args.source,
                 version=EXTERNAL_VERSION, schema_version=2, entrypoint="quality/external_cli.py")
        if args.trusted_head is not None and args.trusted_head != args.head:
            raise Invalid("trusted-designation-must-name-exact-head")
        if args.command == "doctor" and (args.plan or any((args.evidence, args.evidence_sha256, args.approved_producer,
                                                         args.observations, args.observations_sha256, args.approved_observer))):
            raise Invalid("doctor-cannot-import")
        if args.command == "import" and not args.plan:
            raise Invalid("import-requires-plan")
        repo = args.repo.resolve(strict=True)
        root = state_root(args.state, [repo, package.parent])
        git = Git(repo)
        clock = read()
        context, config, error = None, None, None
        try:
            context, config = subject(git, args.base, args.head, args.identity, args.artifact_sha256,
                                      args.source, args.trusted_head is not None, clock)
        except (Invalid, OSError, ValueError, subprocess.SubprocessError):
            if args.command == "doctor":
                raise
            error = "current-subject-unavailable"
        with target_lock(root, repo):
            if cancellation.requested:
                raise KeyboardInterrupt
            if args.command == "doctor":
                assert context is not None and config is not None
                state = create(root, context, config, clock)
                if metadata(git, config) != context["metadata"]:
                    gap(state, "source-moved-during-plan")
                    checkpoint(root / state["plan_id"] / "record.json", state, read())
            else:
                request = {"repository": args.identity, "base": args.base, "head": args.head,
                           "artifact_sha256": args.artifact_sha256, "toolkit_source": args.source}
                state = receive(root, args.plan, git, context, config, clock,
                    [repo, package.parent, root], evidence=args.evidence,
                    evidence_sha256=args.evidence_sha256, producer=args.approved_producer,
                    observations=args.observations, observations_sha256=args.observations_sha256,
                    observer=args.approved_observer, context_error=error, outcome=outcome,
                    request=request, cancellation=cancellation)
        if cancellation.requested and outcome.state is not None:
            state = outcome.recover("import-interrupted", persist=False) or state
        delivering = True
        emit(state, root, cancellation)
        code = {"pass": 0, "fail": 1, "incomplete": 2}[state["report"]["overall"]]
        return 1 if code == 1 else 2 if cancellation.requested else code
    except (ImportStorageFailure, Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        if outcome.state is not None:
            try:
                state = outcome.recover("report-output-unavailable" if delivering else "import-finalization-unavailable", persist=False)
                if state is not None and not delivering:
                    delivering = True
                    emit(state, root, cancellation)
            except (ImportStorageFailure, Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
                pass
            code = 1 if outcome.failure is not None else 2
            try:
                message = "fail: known bound failure; final report delivery/persistence unconfirmed\n" if code == 1 else "incomplete: final report delivery/persistence unconfirmed\n"
                write_output(message.encode(), cancellation, fd=2, seconds=0.1, known_failure=True)
            except (OSError, KeyboardInterrupt):
                pass
            return code
        try:
            write_output(b"incomplete: external-import-unavailable (inspect the last atomic plan record)\n", cancellation, fd=2, seconds=0.1, known_failure=True)
        except (OSError, KeyboardInterrupt):
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
