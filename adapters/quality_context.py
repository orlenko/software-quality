"""Optional personal-repository context; delegate policy and pinning to the launcher."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
import signal
import selectors
import subprocess
import sys
import time
from typing import Any

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use an approved Python interpreter with -I -S")
HERE = Path(__file__).resolve().parent
# Resolve only the complete approved source/bundle layout. In source mode the
# legacy adapters/quality.py must not shadow the owned quality package.
REQUIRED_RESOURCES = ("quality_trust.py", "quality/__init__.py", "quality/process.py")
if all((HERE / name).is_file() for name in REQUIRED_RESOURCES):
    RESOURCE_ROOT = HERE
elif HERE.name == "adapters" and all((HERE.parent / name).is_file() for name in REQUIRED_RESOURCES):
    RESOURCE_ROOT = HERE.parent
else:
    print("incomplete adapter resource closure", file=sys.stderr)
    raise SystemExit(2)
sys.path.insert(0, str(RESOURCE_ROOT))
from quality_trust import Cancellation, OwnedProcess, write_output, Git, Invalid, MAX_JSON, OID, SAFE_PATH, canonical, parse_json, within, outside_path, raw_absolute, subject_root
from quality.process import stop

IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")
PROJECTION = "{number:.number,state:.state,base_repository:.base.repo.full_name,base:.base.sha,head_repository:.head.repo.full_name,head:.head.sha,head_ref:.head.ref}"


@dataclass(frozen=True)
class PullRequest:
    number: int
    state: str
    base_repository: str
    base: str
    head_repository: str
    head: str
    head_ref: str

    @staticmethod
    def read(value: Any, identity: str) -> PullRequest:
        keys = set(PullRequest.__dataclass_fields__)
        if type(value) is not dict or set(value) != keys:
            raise Invalid("invalid-pr-metadata")
        if type(value["number"]) is not int or not 0 < value["number"] < 2**31:
            raise Invalid("invalid-pr-number")
        if any(type(value[key]) is not str for key in keys - {"number"}):
            raise Invalid("invalid-pr-field")
        if (value["base_repository"] != identity or not IDENTITY.fullmatch(value["head_repository"])
                or value["state"] != "open" or not OID.fullmatch(value["base"])
                or not OID.fullmatch(value["head"]) or not 0 < len(value["head_ref"]) <= 255
                or any(ord(char) < 32 for char in value["head_ref"])):
            raise Invalid("pr-repository-state-or-identity-mismatch")
        return PullRequest(**value)


def outside_target(value: Path, repo: Path) -> Path:
    try:
        return outside_path(value, [repo], strict=True)
    except Invalid as exc:
        if str(exc) == "path-traverses-protected-root":
            raise Invalid("approved-path-must-be-outside-target") from None
        raise


def approved_path(value: Path, repo: Path, *, directory: bool = False) -> Path:
    resolved = outside_target(value, repo)
    if directory:
        if not resolved.is_dir():
            raise Invalid("approved-directory-required")
    elif not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise Invalid("approved-executable-required")
    return resolved


def metadata(args: Any, route: str, fields: list[str] | None = None) -> Any:
    gh = approved_path(args.github_cli, args.repo)
    config = approved_path(args.github_config, args.repo, directory=True)
    projection = "map(" + PROJECTION + ")" if fields is not None else PROJECTION
    command = [str(gh), "api", "--hostname", "github.com", "--method", "GET", route, "--jq", projection]
    for field in fields or []:
        command.extend(["-f", field])
    env = {"PATH": SAFE_PATH, "HOME": str(config), "GH_CONFIG_DIR": str(config),
           "GH_HOST": "github.com", "GH_PROMPT_DISABLED": "1", "GH_PAGER": "cat", "LC_ALL": "C",
           "GH_NO_UPDATE_NOTIFIER": "1", "GH_NO_EXTENSION_UPDATE_NOTIFIER": "1",
           "GH_TELEMETRY": "false", "DO_NOT_TRACK": "1"}
    # Bound bytes during execution, retain no raw files, and own the helper group.
    process = OwnedProcess(args.cancellation, protected_roots=[args.repo])
    stopped = False
    cleaned = False
    def cleanup() -> bool:
        nonlocal stopped, cleaned
        if not stopped:
            cleaned = stop(process)
            stopped = True
        return cleaned

    data = bytearray()
    try:
        process.start(command, cwd=HERE, env=env, stdin=subprocess.DEVNULL,
                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert process.stdout is not None
        with selectors.DefaultSelector() as selector:
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdout, selectors.EVENT_READ)
            deadline = time.monotonic() + args.metadata_timeout
            while True:
                if args.cancellation.requested:
                    raise KeyboardInterrupt
                if time.monotonic() >= deadline:
                    raise Invalid("metadata-timeout-use-explicit-ids")
                for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                    elif len(data) + len(chunk) > MAX_JSON:
                        raise Invalid("metadata-output-limit-use-explicit-ids")
                    else:
                        data.extend(chunk)
                if process.observe() is not None and not selector.get_map():
                    break
        if not cleanup():
            raise Invalid("metadata-helper-cleanup-unverified")
    finally:
        cleanup()
        if process.stdout is not None:
            process.stdout.close()
    if process.code:
        raise Invalid("metadata-route-unavailable-use-explicit-ids")
    return parse_json(bytes(data))


def local_branch(git: Git) -> tuple[str, str]:
    ref = git.run("symbolic-ref", "--quiet", "HEAD").decode().removesuffix("\n")
    if not ref.startswith("refs/heads/"):
        raise Invalid("attached-branch-required-use-explicit-ids")
    return ref, git.commit(git.run("rev-parse", "HEAD").decode().strip())


def fetch_pr(args: Any, number: int) -> PullRequest:
    result = PullRequest.read(metadata(args, f"repos/{args.identity}/pulls/{number}"), args.identity)
    if result.number != number or result.base != args.base:
        raise Invalid("pr-number-or-accepted-base-mismatch")
    return result


def core_arguments(args: Any, head: str) -> list[str]:
    command = [str(args.python), "-I", "-S", str(args.launcher), "--adapter-protocol", "1", args.action,
               "--repo", str(args.repo), "--identity", args.identity, "--base", args.base, "--head", head,
               "--cache", str(args.cache), "--state", str(args.state)]
    if args.execute_trusted:
        command.append("--execute-trusted")
    if args.review is not None:
        command.extend(["--review", str(args.review)])
    if args.review_sha256 is not None:
        command.extend(["--review-sha256", args.review_sha256])
    return command


def launch(command: list[str], cancellation: Cancellation, *, protected_roots: list[Path],
           cwd: Path | None = None) -> tuple[int, bool]:
    owned = OwnedProcess(cancellation, protected_roots=protected_roots)
    try:
        owned.start(command, cwd=cwd if cwd is not None else HERE, env={"PATH": SAFE_PATH, "LC_ALL": "C"})
        code = owned.wait()
    except (Invalid, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt):
        stop(owned)
        return (owned.code if owned.code in (0, 1, 2) else 2), True
    finally:
        cleaned = stop(owned)
    return (code if code in (0, 1, 2) else 2), cancellation.requested or not cleaned


def frontend_exit(core_exit: int | None, context_complete: bool) -> int:
    if core_exit == 1:
        return 1
    return 0 if core_exit == 0 and context_complete else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--personal", action="store_true", help="owner attests personal eligibility for this repository")
    parser.add_argument("--base", required=True, help="full owner-approved accepted base; never inferred as approval")
    parser.add_argument("--head", help="full explicit head; additionally required for trusted execution in PR mode")
    context = parser.add_mutually_exclusive_group()
    context.add_argument("--pr", type=int)
    context.add_argument("--current-pr", action="store_true")
    parser.add_argument("--github-cli", type=Path)
    parser.add_argument("--github-config", type=Path, help="explicit owner-approved outside-target authentication directory")
    parser.add_argument("--allow-github-metadata", action="store_true")
    parser.add_argument("--metadata-timeout", type=int, choices=range(1, 16), default=15,
                        help="maximum seconds per metadata request (1-15)")
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--action", choices=("doctor", "check"), default="doctor")
    parser.add_argument("--execute-trusted", action="store_true")
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-sha256")
    args = parser.parse_args()
    args.cancellation = Cancellation()
    with args.cancellation.handlers():
        return frontend_main(args)


def frontend_main(args: argparse.Namespace) -> int:
    receipt: dict[str, Any] = {"adapter_protocol": 1, "adapter_version": "0.1.2", "target": None,
        "core_exit": None, "context_status": "incomplete", "pr_freshness": "unverified", "reason": "not-started"}
    try:
        if not args.personal or not IDENTITY.fullmatch(args.identity):
            raise Invalid("explicit-personal-eligibility-and-identity-required")
        args.repo = subject_root(args.repo)
        outside_path(Path(__file__), [args.repo], strict=True)
        args.python = approved_path(args.python, args.repo)
        # Launcher is a Python source file, not necessarily executable.
        launcher = outside_target(args.launcher, args.repo)
        if not launcher.is_file():
            raise Invalid("launcher-must-be-approved-outside-target")
        args.launcher = launcher
        tool_roots = [RESOURCE_ROOT, args.launcher.parent]
        args.cache = outside_path(args.cache, [args.repo, *tool_roots])
        args.state = outside_path(args.state, [args.repo, *tool_roots, args.cache])
        if args.review is not None:
            # The authoritative reader validates data after retaining check facts.
            args.review = raw_absolute(args.review)
        git = Git(args.repo)
        args.base = git.commit(args.base)
        config = parse_json(git.blob(args.base, ".quality/config.json"))
        if type(config) is not dict or config.get("repository") != args.identity:
            raise Invalid("accepted-repository-identity-mismatch")
        use_pr = args.pr is not None or args.current_pr
        selected: PullRequest | None = None
        branch: tuple[str, str] | None = None
        if use_pr:
            if not args.allow_github_metadata or args.github_cli is None or args.github_config is None:
                raise Invalid("approved-metadata-route-required-or-use-explicit-ids")
            if args.execute_trusted and args.head is None:
                raise Invalid("explicit-expected-head-required-for-trusted-pr-execution")
            if args.current_pr:
                branch = local_branch(git)
                short_ref = branch[0].removeprefix("refs/heads/")
                owner = args.identity.split("/", 1)[0]
                candidates = metadata(args, f"repos/{args.identity}/pulls", ["state=open", "head=" + owner + ":" + short_ref, "per_page=100", "page=1"])
                if type(candidates) is not list or len(candidates) != 1:
                    raise Invalid("ambiguous-missing-or-truncated-current-pr")
                candidate = PullRequest.read(candidates[0], args.identity)
                if candidate.head_ref != short_ref or candidate.head_repository != args.identity:
                    raise Invalid("current-fork-or-branch-mismatch-use-explicit-context")
                number = candidate.number
            else:
                number = args.pr
                if number is None or number < 1 or number >= 2**31:
                    raise Invalid("invalid-pr-number")
            selected = fetch_pr(args, number)
            if args.current_pr and selected != candidate:
                raise Invalid("current-pr-changed-during-selection")
            head = git.commit(selected.head)
            if args.head is not None and git.commit(args.head) != head:
                raise Invalid("explicit-expected-head-mismatch")
            if branch is not None and branch[1] != head:
                raise Invalid("current-local-head-differs-use-explicit-context")
            receipt["target"] = {"repository": args.identity, "base": args.base, "head": head,
                                 "pr": asdict(selected), "local_ref": branch[0] if branch else None,
                                 "local_head": branch[1] if branch else None}
            if fetch_pr(args, number) != selected:
                raise Invalid("pr-moved-before-launch")
            if branch is not None and local_branch(git) != branch:
                raise Invalid("local-branch-moved-before-launch")
        else:
            if args.head is None:
                raise Invalid("explicit-head-or-authorized-pr-context-required")
            head = git.commit(args.head)
        receipt["target"] = {"repository": args.identity, "base": args.base, "head": head,
                             "pr": asdict(selected) if selected else None,
                             "local_ref": branch[0] if branch else None, "local_head": branch[1] if branch else None}
        code, interrupted = launch(core_arguments(args, head), args.cancellation, protected_roots=[args.repo])
        receipt["core_exit"] = code
        if interrupted:
            raise Invalid("frontend-interrupted")
        if selected is not None:
            if fetch_pr(args, selected.number) != selected:
                raise Invalid("pr-moved-after-launch")
            if branch is not None and local_branch(git) != branch:
                raise Invalid("local-branch-moved-after-launch")
        receipt.update(context_status="complete", pr_freshness="stable-observed" if selected else "not-requested", reason="immutable-context-observed")
    except Invalid as exc:
        receipt["reason"] = str(exc)
    except KeyboardInterrupt:
        receipt["reason"] = "frontend-interrupted"
    except (OSError, ValueError, subprocess.SubprocessError):
        receipt["reason"] = "context-prerequisite-unavailable-use-explicit-ids"
    code = frontend_exit(receipt["core_exit"], receipt["context_status"] == "complete")
    if args.cancellation.requested and code != 1:
        receipt.update(context_status="incomplete", reason="frontend-interrupted")
        code = 2
    try:
        write_output(b"context " + canonical(receipt), args.cancellation, known_failure=code == 1, allow_cancelled=code == 2)
    except (OSError, KeyboardInterrupt):
        try:
            write_output(b"incomplete: context delivery unavailable or partial\n", args.cancellation, fd=2, seconds=0.1, known_failure=True)
        except (OSError, KeyboardInterrupt):
            pass
        return 1 if code == 1 else 2
    return 1 if code == 1 else 2 if args.cancellation.requested else code


if __name__ == "__main__":
    raise SystemExit(main())
