"""Pinned schema2 import-only CLI. A report never claims importer execution."""
from __future__ import annotations

import argparse
from pathlib import Path
import os
import signal
import sys
import subprocess

from quality_trust import EXTERNAL_VERSION, MAX_ARTIFACT, Git, Invalid, artifact, canonical, regular_bytes
from quality.evidence import target_lock
from quality.external_clock import read
from quality.external_model import metadata, subject
from quality.external_store import create, gap, checkpoint, receive, state_root


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
        def interrupted(signum: int, frame: object) -> None:
            raise KeyboardInterrupt
        previous = signal.signal(signal.SIGTERM, interrupted)
        try:
            with target_lock(root, repo):
                if args.command == "doctor":
                    assert context is not None and config is not None
                    state = create(root, context, config, clock)
                    if metadata(git, config) != context["metadata"]:
                        gap(state, "source-moved-during-plan")
                        checkpoint(root / state["plan_id"] / "record.json", state, read())
                else:
                    state = receive(root, args.plan, git, context, config, clock,
                                    [repo, package.parent, root], evidence=args.evidence,
                                    evidence_sha256=args.evidence_sha256, producer=args.approved_producer,
                                    observations=args.observations, observations_sha256=args.observations_sha256,
                                    observer=args.approved_observer, context_error=error)
        finally:
            signal.signal(signal.SIGTERM, previous)
        print(canonical({"protocol_version": 2, "plan_id": state["plan_id"], "challenge": state["challenge"],
                         "context_sha256": state["context_sha256"],
                         "record": str(root / state["plan_id"] / "record.json"), "report": state["report"]}).decode(), end="")
        return {"pass": 0, "fail": 1, "incomplete": 2}[state["report"]["overall"]]
    except (Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        print("incomplete: external-import-unavailable (inspect the last atomic plan record)", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
