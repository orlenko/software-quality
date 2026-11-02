"""Plan, execute authorized stages and atomically persist local evidence."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import sys
from typing import Any
import uuid

from quality_trust import (write_output, Cancellation, MAX_JSON, Git, Invalid, POLICY, canonical, lock_value,
                           parse_json, regular_bytes, sha, snapshot_stable, within)
from quality.process import CommandInterrupted, execute
from quality.schema import checked
from quality.evidence import now, stage, verdict, save, target_lock

EMPTY_STATUS = sha(b"")


def review_stages(args: Any, config: dict[str, Any], context: dict[str, Any],
                  report: dict[str, Any], repo: Path, tool_root: Path) -> list[dict[str, Any]]:
    routes = config["reviewer"]["routes"]
    def missing(reason: str) -> list[dict[str, Any]]:
        return [stage("review:" + route["id"], reason=reason) for route in routes]

    if args.review is None or args.review_sha256 is None:
        return missing("review-response-and-approved-digest-required")
    try:
        path = args.review
        if within(path, repo) or within(path, tool_root):
            raise Invalid("review-must-be-outside-target-and-tool")
        data = regular_bytes(path, MAX_JSON)
        if sha(data) != args.review_sha256:
            raise Invalid("review-digest-mismatch")
        response = checked("review", parse_json(data))
        if response["context"] != context:
            raise Invalid("review-context-mismatch")
        report["review"]["response_sha256"] = sha(data)
        results: list[dict[str, Any]] = []
        known = {route["id"] for route in routes}
        unknown = any(type(record) is not dict or type(record.get("route_id")) is not str or record.get("route_id") not in known
                      for record in response["reviews"])
        for route in routes:
            records = [record for record in response["reviews"]
                       if type(record) is dict and record.get("route_id") == route["id"]]
            valid: list[dict[str, Any]] = []
            invalid = False
            for record in records:
                try:
                    checked("review-record", record)
                    if record["reviewer_id"] != route["reviewer_id"] or record["boundary"] != route["boundary"]:
                        raise Invalid("review-identity-or-boundary-mismatch")
                    ids: set[str] = set()
                    for finding in record["findings"]:
                        if finding["id"] in ids or (finding["disposition"] == "resolved" and not finding["resolution"].strip()):
                            raise Invalid("review-finding-invalid")
                        ids.add(finding["id"])
                    valid.append(record)
                    report["review"]["records"].append(record)
                except Invalid:
                    invalid = True
            blocker = any(f["severity"] == "blocker" and f["disposition"] == "open"
                          for record in valid for f in record["findings"])
            if blocker:
                results.append(stage("review:" + route["id"], "fail", "open-validated-blocker"))
            elif invalid or len(records) != 1 or len(valid) != 1:
                results.append(stage("review:" + route["id"], reason="review-route-missing-invalid-or-duplicate"))
            else:
                results.append(stage("review:" + route["id"], "pass", "accepted-external-independent-attestation"))
        if unknown:
            results.append(stage("review-unexpected", reason="unknown-or-unroutable-review-record"))
        return results
    except Invalid as exc:
        return missing(str(exc))
    except (OSError, ValueError):
        return missing("review-unreadable")


def run(args: Any, artifact_sha: str, source: str, experimental: bool) -> tuple[dict[str, Any], Path]:
    repo = args.repo.resolve(strict=True)
    state = args.state.resolve()
    tool = Path(sys.argv[0]).resolve()
    tool_root = Path(__file__).resolve().parents[1] if experimental else tool.parent
    if (within(state, repo) or within(state, tool_root) or within(repo, state)
            or within(repo, tool_root)):
        raise Invalid("target-tool-state-paths-must-be-separate")
    git = Git(repo)
    base, head = git.commit(args.base), git.commit(args.head)
    config_data = git.blob(base, ".quality/config.json")
    lock_data = git.blob(base, ".quality/lock.json")
    config = checked("config", parse_json(config_data))
    lock = checked("lock", lock_value(lock_data))
    if config["repository"] != args.identity:
        raise Invalid("repository-identity-mismatch")
    if lock["artifact_sha256"] != artifact_sha or lock["source"] != source:
        raise Invalid("accepted-pin-mismatch")
    checks = config["execution"]["checks"]
    if len({check["id"] for check in checks}) != len(checks):
        raise Invalid("duplicate-check-id")
    routes = config["reviewer"]["routes"]
    if len({route["id"] for route in routes}) != len(routes):
        raise Invalid("duplicate-review-route")
    if config["reviewer"]["require_distinct_identities"] and len({route["reviewer_id"] for route in routes}) != len(routes):
        raise Invalid("distinct-reviewer-identities-required")
    for ref in config["references"].values():
        if ref.startswith("/") or ".." in PurePosixPath(ref).parts or "\\" in ref:
            raise Invalid("reference-path-invalid")
        git.blob(base, ref)
    context = {"repository": config["repository"], "base": base, "head": head,
               "base_tree": git.tree(base), "head_tree": git.tree(head),
               "config_sha256": sha(config_data), "lock_sha256": sha(lock_data),
               "artifact_sha256": artifact_sha, "toolkit_source": source,
               "policy_version": POLICY, "schema_version": 1}
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with target_lock(state, repo):
        run_id = uuid.uuid4().hex
        directory = state / run_id
        directory.mkdir(mode=0o700)
        before = git.state()
        paths = git.run("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base, head)
        changed_paths = [item.decode("utf-8") for item in paths.split(b"\0") if item]
        report: dict[str, Any] = {"schema_version": 1, "run_id": run_id, "mode": args.command,
            "started_at": now(), "finished_at": "", "context": context,
            "tool_mode": "experimental" if experimental else "artifact", "effective_plan": config,
            "source_before": before, "source_after": before, "changed_paths": changed_paths,
            "stages": [stage("inspection", "pass", "immutable-target-resolved"),
                       stage("artifact", "incomplete" if experimental else "pass",
                             "experimental-source" if experimental else "accepted-artifact-verified"),
                       *[stage(prefix + check["id"]) for check in checks for prefix in ("check:", "snapshot:", "output:")],
                       *[stage("review:" + route["id"]) for route in routes], stage("source")],
            "review": {"response_sha256": "", "evidence_kind": "external-attestation", "records": []},
            "overall": "incomplete"}
        report_path = directory / "report.json"
        save(report_path, report)
        args._validated_report, args._report_path = report, report_path
        # Surface the effective effects and response context before any target execution.
        write_output(canonical({"run_id": run_id, "context": context, "effective_plan": config,
                               "execution_requested": args.execute_trusted}),
                     getattr(args, "cancellation", Cancellation()))
        try:
            execute_allowed = (args.command == "check" and args.execute_trusted
                               and config["execution"]["trusted_local"]
                               and config["execution"]["isolation"] == "owner-approved-wrapper")
            reason = "doctor-does-not-execute" if args.command == "doctor" else "trusted-local-authorization-or-isolation-missing"
            for number, check in enumerate(checks):
                index = 2 + number * 3
                if not execute_allowed:
                    report["stages"][index] = stage("check:" + check["id"], reason=reason)
                else:
                    snapshot = directory / ("snapshot-" + check["id"])
                    snapshot.mkdir(mode=0o700)
                    log_name = check["id"] + ".log"
                    try:
                        expected = git.export(head, snapshot)
                        if not snapshot_stable(snapshot, expected):
                            raise Invalid("snapshot-changed-before-check")
                        status, outcome, code, output_status, output_reason = execute(check, snapshot, directory / ("state-" + check["id"]), directory / log_name, getattr(args, "cancellation", None))
                        report["stages"][index] = stage("check:" + check["id"], status, outcome, code, log_name)
                        stable = snapshot_stable(snapshot, expected)
                        report["stages"][index + 1] = stage("snapshot:" + check["id"], "pass" if stable else "incomplete",
                                                            "tracked-snapshot-unchanged" if stable else "tracked-snapshot-mutated")
                        report["stages"][index + 2] = stage("output:" + check["id"], output_status, output_reason)
                    except CommandInterrupted as exc:
                        code = exc.code
                        status = "incomplete" if code is None or code < 0 else "pass" if code == 0 else "fail"
                        report["stages"][index] = stage("check:" + check["id"], status,
                                                       "command-failed" if status == "fail" else "run-interrupted",
                                                       min(code, 255) if code is not None and code >= 0 else -1, log_name)
                        report["stages"][index + 2] = stage("output:" + check["id"], reason="run-interrupted")
                        raise KeyboardInterrupt from exc
                    except (Invalid, UnicodeError) as exc:
                        report["stages"][index] = stage("check:" + check["id"], reason=str(exc) if isinstance(exc, Invalid) else "snapshot-encoding-unsupported")
                    except OSError:
                        report["stages"][index] = stage("check:" + check["id"], reason="snapshot-or-command-unavailable")
                report["overall"] = verdict(report["stages"])
                save(report_path, report)
            review_index = 2 + 3 * len(checks)
            report["stages"][review_index:-1] = review_stages(args, config, context, report, repo, tool_root)
        except KeyboardInterrupt:
            # A failing completed stage remains failure; unfinished stages stay incomplete.
            report["stages"][-1] = stage("source", reason="run-interrupted")
        finally:
            # Handled interruption during a later record cannot discard a blocker
            # already independently validated against this immutable context.
            for record in report["review"]["records"]:
                if any(f["severity"] == "blocker" and f["disposition"] == "open" for f in record["findings"]):
                    for index, item in enumerate(report["stages"]):
                        if item["id"] == "review:" + record["route_id"]:
                            report["stages"][index] = stage(item["id"], "fail", "open-validated-blocker")
            try:
                after = git.state()
                report["source_after"] = after
                clean = before == after and before["status_sha256"] == EMPTY_STATUS
                if report["stages"][-1]["reason"] != "run-interrupted":
                    report["stages"][-1] = stage("source", "pass" if clean else "incomplete",
                                                 "clean-stable-checkout" if clean else "dirty-or-moving-checkout")
            except (Invalid, OSError):
                report["stages"][-1] = stage("source", reason="final-source-identity-unavailable")
            report["finished_at"] = now()
            report["overall"] = verdict(report["stages"])
            save(report_path, report)
        return report, report_path
