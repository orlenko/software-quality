"""One-gate schema2 subject and externally attested fact validation. No execution."""
from __future__ import annotations

from typing import Any
from quality_trust import EXTERNAL_VERSION, POLICY, Git, Invalid, canonical, lock_value, parse_json, sha
from quality.evidence import stage, verdict
from quality.external_clock import CONTINUITY_MS, MODEL, PRECISION_MS, Reading
from quality.schema import checked


def registry(value: Any) -> dict[str, Any]:
    checked("external-config", value)
    gate = value["gate"]
    for key in ("required_controls", "allowed_effects", "refs"):
        if len(set(gate[key])) != len(gate[key]):
            raise Invalid("duplicate-registry-item")
    if (gate["producer_id"] == gate["observer_id"]
            or not {"deadline", "cleanup"} <= set(gate["required_controls"])
            or (gate["trust_rule"] == "always-contained" and "containment" not in gate["required_controls"])):
        raise Invalid("invalid-control-registry")
    for ref in gate["refs"]:
        if ".." in ref or "//" in ref or ref.endswith(("/", ".", ".lock")):
            raise Invalid("unsupported-registry-ref")
    ids = [row["id"] for row in value["unsupported_obligations"]]
    if len(ids) != len(set(ids)):
        raise Invalid("duplicate-obligation")
    return value


def metadata(git: Git, config: dict[str, Any]) -> dict[str, Any]:
    return {**git.state(), "index_sha256": sha(git.run("ls-files", "--stage", "-z")),
            "refs": [{"name": ref, "commit": git.run("rev-parse", "--verify", ref + "^{commit}").decode().strip()}
                     for ref in sorted(config["gate"]["refs"])]}


def subject(git: Git, base: str, head: str, identity: str, digest: str,
            source: str, trusted: bool, clock: Reading) -> tuple[dict[str, Any], dict[str, Any]]:
    git.commit(base)
    git.commit(head)
    config_data = git.blob(base, ".quality/config.json")
    lock_data = git.blob(base, ".quality/lock.json")
    config = registry(parse_json(config_data))
    pin = lock_value(lock_data, version=EXTERNAL_VERSION, schema_version=2)
    if (config["repository"] != identity or pin["artifact_sha256"] != digest or pin["source"] != source):
        raise Invalid("subject-pin-or-repository-mismatch")
    if trusted and config["gate"]["trust_rule"] != "owner-designation-permitted":
        raise Invalid("owner-designation-not-permitted")
    observed = metadata(git, config)
    if observed["head"] != head or observed["status_sha256"] != sha(b""):
        raise Invalid("known-clean-head-required")
    context = {"repository": identity, "base": base, "head": head,
               "base_tree": git.tree(base), "head_tree": git.tree(head),
               "config_sha256": sha(config_data), "lock_sha256": sha(lock_data),
               "artifact_sha256": digest, "toolkit_source": source, "policy_version": POLICY,
               "schema_version": 2, "metadata": observed,
               "clock": {"model": MODEL, "boot_sha256": clock.boot_sha256},
               "owner_trusted_head": trusted}
    return context, config


def continuity(state: dict[str, Any], clock: Reading) -> bool:
    wall_delta = clock.wall_ms - state["issued_wall_ms"]
    mono_delta = clock.mono_ms - state["issued_mono_ms"]
    return (clock.boot_sha256 == state["context"]["clock"]["boot_sha256"]
            and wall_delta >= 0 and mono_delta >= 0
            and abs(wall_delta - mono_delta) <= CONTINUITY_MS)


def bound(state: dict[str, Any], record: dict[str, Any], at_ms: int, at_mono_ms: int) -> bool:
    """Attributable subject/result binding; coverage/controls are separate axes."""
    gate = state["registry"]["gate"]
    consumed, timing = record["consumed"], record["timing"]
    return (record["gate_id"] == gate["id"] and record["producer_id"] == gate["producer_id"]
            and record["canonical_sha256"] == gate["canonical_sha256"]
            and record["phase"] == "known-commit" and not record["features"]
            and consumed["established"]
            and consumed["mechanism_id"] == gate["mechanism"]["id"]
            and consumed["mechanism_sha256"] == gate["mechanism"]["sha256"]
            and consumed["before_context_sha256"] == state["context_sha256"]
            and consumed["after_context_sha256"] == state["context_sha256"]
            and consumed["origin_tree"] == state["context"]["head_tree"]
            and consumed["environment_sha256"] == gate["environment_sha256"]
            and timing["clock"] == state["context"]["clock"]
            and state["issued_wall_ms"] + PRECISION_MS <= timing["started_ms"] <= timing["finished_ms"] <= at_ms
            and state["issued_mono_ms"] + PRECISION_MS <= timing["started_mono_ms"] <= timing["finished_mono_ms"] <= at_mono_ms
            and abs((timing["started_ms"] - state["issued_wall_ms"]) - (timing["started_mono_ms"] - state["issued_mono_ms"])) <= CONTINUITY_MS
            and abs((timing["finished_ms"] - state["issued_wall_ms"]) - (timing["finished_mono_ms"] - state["issued_mono_ms"])) <= CONTINUITY_MS)


def natural_failure(record: dict[str, Any]) -> bool:
    return record["outcome"]["kind"] == "completed" and record["outcome"]["exit_code"] > 0


def observer_bound(state: dict[str, Any], document: dict[str, Any], at_ms: int, at_mono_ms: int) -> bool:
    if not state["original"]:
        return False
    record = state["original"][0]["record"]
    gate = state["registry"]["gate"]
    timing = record["timing"]
    return (document["plan_id"] == state["plan_id"] and document["challenge"] == state["challenge"]
            and document["context_sha256"] == state["context_sha256"]
            and document["gate_id"] == gate["id"] and document["invocation_id"] == record["invocation_id"]
            and document["observer_id"] == gate["observer_id"]
            and document["profile_sha256"] == gate["observer"]["profile_sha256"]
            and document["mechanism_sha256"] == gate["observer"]["mechanism_sha256"]
            and document["source_route"] == "independent-controller"
            and document["basis"] == "controller-observation" and document["clock"] == state["context"]["clock"]
            and document["observed_from_ms"] <= timing["started_ms"] - PRECISION_MS
            and timing["finished_ms"] <= document["cleanup_at_ms"]
            and document["cleanup_at_ms"] + PRECISION_MS <= document["observed_through_ms"] <= at_ms
            and document["observed_from_ms"] >= state["issued_wall_ms"] - PRECISION_MS
            and state["issued_mono_ms"] - PRECISION_MS <= document["observed_from_mono_ms"] <= timing["started_mono_ms"] - PRECISION_MS
            and timing["finished_mono_ms"] <= document["cleanup_at_mono_ms"]
            and document["cleanup_at_mono_ms"] + PRECISION_MS <= document["observed_through_mono_ms"] <= at_mono_ms
            and all(abs((document[prefix + "_ms"] - state["issued_wall_ms"])
                        - (document[prefix + "_mono_ms"] - state["issued_mono_ms"])) <= CONTINUITY_MS
                    for prefix in ("observed_from", "observed_through", "cleanup_at", "deadline_at")))


def report(state: dict[str, Any], clock: Reading) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    def row(name: str, ok: bool, reason: str, basis: str = "external-attestation", code: int = -1,
            failure: bool = False) -> None:
        rows.append({**stage(name, "fail" if failure else "pass" if ok else "incomplete", reason, code),
                     "evidence_basis": basis})
    row("plan-issuance", state["issued"], "durable-challenge-before-issuance", "importer-observation")
    row("context", not state["request_gaps"], "current-context-and-request" if not state["request_gaps"] else ",".join(state["request_gaps"]), "importer-observation")
    row("clock", continuity(state, clock), "same-host-boot-continuity", "importer-observation")
    row("integrity", not state["integrity_gaps"], "local-route-integrity" if not state["integrity_gaps"] else ",".join(state["integrity_gaps"]), "importer-observation")
    gate = state["registry"]["gate"]
    row("producer-approval", bool(state["original"]), "independently-approved-input-route", "operator-approval")
    if state["original"]:
        record = state["original"][0]["record"]
        timing, outcome = record["timing"], record["outcome"]
        row("consumed-subject", True, "accepted-mechanism-context-origin-environment")
        row("natural-result", outcome["kind"] == "completed" and outcome["exit_code"] == 0,
            "externally-attested-" + outcome["kind"], code=outcome["exit_code"], failure=natural_failure(record))
        row("coverage", record["coverage"] == {"kind": "whole", "sha256": gate["coverage_sha256"]}, "whole-canonical-coverage")
        row("effects", len(record["effects"]) == len(set(record["effects"])) and set(record["effects"]) <= set(gate["allowed_effects"]), "effects-within-registry")
        row("output", record["output_complete"], "output-complete")
        duration = timing["finished_ms"] - timing["started_ms"]
        mono_duration = timing["finished_mono_ms"] - timing["started_mono_ms"]
        row("budget", max(duration, mono_duration, timing["elapsed_ms"]) <= gate["budget_seconds"] * 1000
            and abs(duration - mono_duration) <= CONTINUITY_MS
            and abs(mono_duration - timing["elapsed_ms"]) <= PRECISION_MS, "budget-and-elapsed-validation-only")
        row("freshness", 0 <= clock.wall_ms - timing["finished_ms"] <= gate["import_window_seconds"] * 1000
            and 0 <= clock.mono_ms - timing["finished_mono_ms"] <= gate["import_window_seconds"] * 1000, "original-completion-window")
        controls = set(gate["required_controls"])
        if not state["context"]["owner_trusted_head"] or record["consumed"]["provenance"] != "trusted-local":
            controls.add("containment")
        observations = state["observer"][0]["document"]["observations"] if state["observer"] else []
        kinds = [item["kind"] for item in observations]
        if state["observer"]:
            document = state["observer"][0]["document"]
            row("deadline-observation", timing["started_ms"] < document["deadline_at_ms"] <= timing["started_ms"] + gate["budget_seconds"] * 1000
                and timing["started_mono_ms"] < document["deadline_at_mono_ms"] <= timing["started_mono_ms"] + gate["budget_seconds"] * 1000
                and timing["finished_ms"] <= document["deadline_at_ms"] + PRECISION_MS
                and timing["finished_mono_ms"] <= document["deadline_at_mono_ms"] + PRECISION_MS,
                "observed-deadline-within-approved-budget", "external-controller-observation")
            row("cleanup-observation", document["cleanup_state"] == "complete", "observed-cleanup-complete", "external-controller-observation")
        row("observer-approval", bool(state["observer"]), "independently-approved-controller-route", "operator-approval")
        row("observation-uniqueness", len(kinds) == len(set(kinds)), "unique-control-observations", "external-controller-observation")
        for kind in sorted(controls):
            witnesses = [item for item in observations if item["kind"] == kind]
            row("control:" + kind, len(witnesses) == 1 and witnesses[0]["state"] == "enforced",
                "accepted-controller-observation-required", "external-controller-observation")
    else:
        row("canonical-gate", False, "no-bound-supported-receipt")
    if state["failure"]:
        row("retained-natural-failure", False, "validated-same-context-natural-failure",
            code=state["failure"][0]["record"]["outcome"]["exit_code"], failure=True)
    for obligation in state["registry"]["unsupported_obligations"]:
        row("unsupported:" + obligation["id"], False, "required-obligation-unsupported", "unsupported")
    value = {"schema_version": 2, "engine_version": EXTERNAL_VERSION, "policy_version": POLICY,
             "plan_id": state["plan_id"], "context": state["context"], "evidence_kind": "external-attestation",
             "observed_at_ms": clock.wall_ms, "stages": rows, "overall": verdict(rows),
             "original_receipt_sha256": state["original"][0]["receipt_sha256"] if state["original"] else "",
             "failure_receipt_sha256": state["failure"][0]["receipt_sha256"] if state["failure"] else "",
             "observer_receipt_sha256": state["observer"][0]["receipt_sha256"] if state["observer"] else ""}
    return checked("external-report", value)
