"""Owner-local authoritative import route. Reads data; never starts a target gate."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import secrets
import subprocess
from typing import Any, Callable
import uuid

from quality_trust import DIGEST, EXTERNAL_VERSION, MAX_JSON, Git, Invalid, canonical, parse_json, regular_bytes, sha, outside_path
from quality.evidence import save, sync_directory, target_lock
from quality.external_clock import Reading, read as read_clock
from quality.external_model import bound, continuity, metadata, natural_failure, observer_bound, registry, report
from quality.schema import checked


def overlaps(a: Path, b: Path) -> bool:
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


def outside(path: Path, roots: list[Path]) -> Path:
    resolved = outside_path(path, roots)
    if path.is_symlink():
        raise Invalid("symlink-input-refused")
    return resolved


def state_root(path: Path, roots: list[Path]) -> Path:
    root = outside(path, roots)
    if any(overlaps(root, item.resolve()) for item in roots):
        raise Invalid("state-roots-must-be-separate")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not root.is_dir() or root.stat().st_mode & 0o077:
        raise Invalid("private-state-root-required")
    return root


def gap(state: dict[str, Any], reason: str, permanent: bool = False) -> None:
    items = state["integrity_gaps" if permanent else "request_gaps"]
    if reason not in items:
        if len(items) >= 16:
            raise Invalid("too-many-route-gaps")
        items.append(reason)


def checkpoint(path: Path, state: dict[str, Any], clock: Reading) -> None:
    state["report"] = report(state, clock)
    state["state_sha256"] = sha(canonical({key: value for key, value in state.items() if key != "state_sha256"}))
    save(path, state, "external-state")


def create(root: Path, context: dict[str, Any], config: dict[str, Any], clock: Reading, issuance_clock: Callable[[], Reading] = read_clock) -> dict[str, Any]:
    # The initial clock identifies inspection boot; issuance follows durability.
    identifier = uuid.uuid4().hex
    directory = root / identifier
    directory.mkdir(mode=0o700)
    sync_directory(root)
    state: dict[str, Any] = {"schema_version": 2, "engine_version": EXTERNAL_VERSION,
        "plan_id": identifier, "challenge": secrets.token_hex(32), "context": context,
        "context_sha256": sha(canonical(context)), "registry": config,
        "issued": False, "issued_wall_ms": clock.wall_ms, "issued_mono_ms": clock.mono_ms,
        "original": [], "failure": [], "observer": [], "integrity_gaps": [], "request_gaps": [],
        "report": {}, "state_sha256": "0" * 64}
    # First make the challenge durable in a non-importable record. Issuance is
    # sampled only after that write, so a pre-durability invocation cannot bind.
    path = directory / "record.json"
    checkpoint(path, state, clock)
    issued = issuance_clock()
    if issued.boot_sha256 != clock.boot_sha256:
        raise Invalid("boot-changed-before-issuance")
    state["issued_wall_ms"], state["issued_mono_ms"] = issued.wall_ms, issued.mono_ms
    state["issued"] = True
    checkpoint(path, state, issued)
    return state


def load(root: Path, identifier: str) -> tuple[Path, dict[str, Any]]:
    if len(identifier) != 32 or any(char not in "0123456789abcdef" for char in identifier):
        raise Invalid("invalid-plan-id")
    directory = root / identifier
    if directory.is_symlink() or not directory.is_dir() or directory.stat().st_mode & 0o077:
        raise Invalid("private-plan-directory-required")
    path = directory / "record.json"
    value = checked("external-state", parse_json(regular_bytes(path, MAX_JSON)))
    expected = sha(canonical({key: item for key, item in value.items() if key != "state_sha256"}))
    if (not value["issued"] or value["plan_id"] != identifier or value["state_sha256"] != expected
            or sha(canonical(value["context"])) != value["context_sha256"]):
        raise Invalid("corrupt-plan-record")
    registry(value["registry"])
    for slot in ("original", "failure"):
        for entry in value[slot]:
            if sha(canonical(entry["record"])) != entry["record_sha256"] or not bound(value, entry["record"], entry["accepted_at_ms"], entry["accepted_at_mono_ms"]):
                raise Invalid("corrupt-accepted-record")
    if value["failure"] and not natural_failure(value["failure"][0]["record"]):
        raise Invalid("corrupt-failure-slot")
    if value["observer"] and not observer_bound(value, value["observer"][0]["document"], value["observer"][0]["accepted_at_ms"], value["observer"][0]["accepted_at_mono_ms"]):
        raise Invalid("corrupt-observer-slot")
    return path, value


def approved(path: Path | None, digest: str | None, actor: str | None, expected: str,
             roots: list[Path]) -> tuple[bytes, str]:
    if path is None or digest is None or actor != expected or not DIGEST.fullmatch(digest):
        raise Invalid("missing-independent-input-approval")
    data = regular_bytes(outside(path, roots), MAX_JSON)
    if sha(data) != digest:
        raise Invalid("approved-input-digest-mismatch")
    return data, digest


def frame(state: dict[str, Any], envelope: dict[str, Any]) -> bool:
    return (envelope["plan_id"] == state["plan_id"] and envelope["challenge"] == state["challenge"]
            and envelope["context_sha256"] == state["context_sha256"])


def import_records(path: Path, state: dict[str, Any], data: bytes, digest: str, clock: Reading) -> None:
    envelope = checked("external-envelope", parse_json(data))
    if not frame(state, envelope):
        raise Invalid("wrong-envelope-context-or-challenge")
    seen: set[str] = set()
    for raw in envelope["records"]:
        try:
            record = checked("external-record", raw)
        except Invalid:
            gap(state, "malformed-extra-record", True)
            checkpoint(path, state, clock)
            continue
        fingerprint = sha(canonical(record))
        if fingerprint in seen:
            gap(state, "duplicate-producer-record", True)
        seen.add(fingerprint)
        if not bound(state, record, clock.wall_ms, clock.mono_ms):
            gap(state, "unbound-or-unsupported-record", True)
            checkpoint(path, state, clock)
            continue
        entry = {"receipt_sha256": digest, "record_sha256": sha(canonical(record)), "record": deepcopy(record), "accepted_at_ms": clock.wall_ms, "accepted_at_mono_ms": clock.mono_ms}
        if not state["original"]:
            state["original"] = [entry]
        elif any(state["original"][0][key] != entry[key] for key in ("receipt_sha256", "record_sha256")):
            gap(state, "conflicting-producer-evidence", True)
        if natural_failure(record) and not state["failure"]:
            state["failure"] = [entry]
        # This durable checkpoint precedes every later record/control parse.
        checkpoint(path, state, clock)
    if not envelope["records"]:
        gap(state, "empty-producer-envelope")


def import_observer(path: Path, state: dict[str, Any], data: bytes, digest: str, clock: Reading) -> None:
    document = checked("external-observer", parse_json(data))
    if not observer_bound(state, document, clock.wall_ms, clock.mono_ms):
        raise Invalid("unbound-controller-observation")
    entry = {"receipt_sha256": digest, "document": document, "accepted_at_ms": clock.wall_ms, "accepted_at_mono_ms": clock.mono_ms}
    if not state["observer"]:
        state["observer"] = [entry]
    elif state["observer"][0]["receipt_sha256"] != digest:
        gap(state, "conflicting-controller-evidence", True)
    checkpoint(path, state, clock)


def receive(root: Path, identifier: str, git: Git, context: dict[str, Any] | None,
            config: dict[str, Any] | None, clock: Reading, roots: list[Path], *,
            evidence: Path | None = None, evidence_sha256: str | None = None, producer: str | None = None,
            observations: Path | None = None, observations_sha256: str | None = None, observer: str | None = None,
            context_error: str | None = None, final_clock: Callable[[], Reading] = read_clock) -> dict[str, Any]:
    # Plan lock also serializes the same route used from two physical clones.
    with target_lock(root, root / identifier):
        path, state = load(root, identifier)
        state["request_gaps"] = []
        if context_error or context != state["context"] or config != state["registry"]:
            gap(state, "current-subject-mismatch")
        if not continuity(state, clock):
            gap(state, "unsupported-clock-continuity")
        can_admit = not state["request_gaps"]
        try:
            if can_admit:
                try:
                    data, digest = approved(evidence, evidence_sha256, producer, state["registry"]["gate"]["producer_id"], roots)
                    import_records(path, state, data, digest, clock)
                except (Invalid, OSError, ValueError):
                    gap(state, "producer-input-unavailable-or-invalid")
                if observations is not None or observations_sha256 is not None or observer is not None:
                    try:
                        data, digest = approved(observations, observations_sha256, observer, state["registry"]["gate"]["observer_id"], roots)
                        import_observer(path, state, data, digest, clock)
                    except (Invalid, OSError, ValueError):
                        gap(state, "controller-input-unavailable-or-invalid")
            if metadata(git, state["registry"]) != state["context"]["metadata"]:
                gap(state, "source-moved-during-import")
        except KeyboardInterrupt:
            gap(state, "import-interrupted")
            checkpoint(path, state, clock)
            return state
        except (Invalid, OSError, ValueError, subprocess.SubprocessError):
            gap(state, "source-observation-unavailable")
        try:
            observed_clock = final_clock()
        except (Invalid, OSError, ValueError, subprocess.SubprocessError):
            gap(state, "final-clock-unavailable")
            observed_clock = clock
        checkpoint(path, state, observed_clock)
        return state
