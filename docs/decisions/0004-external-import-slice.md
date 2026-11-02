# Known-target external gate import slice

Status: proposed implementation reconciliation, 2026-11-02. Authority is the
bounded import-only assignment; accepted repository/policy rules are those at
`c6b311f`. This narrows [decision 0003](0003-pilot-compatibility.md), rather than
implementing its whole proposed platform. Independent critique is pending below.

The user needs truthful evidence from existing canonical gates that a Git-free
snapshot runner cannot represent. The smallest alternative remains the current
inspection-only/incomplete candidate. This increment will validate one whole-gate
attestation for a known immutable target; it will never execute that gate, provision
a producer, launch a reviewer, contact a service or claim consumer adoption.

## Narrow architecture and versions

Keep the previous engine/adapter source branches and artifact bytes intact. Add
explicit engine/package `0.2.0`, config/report schema `2`, launcher/adapter protocol
`2`, with a separate external CLI/bootstrap entry. The existing v1 entry points
and default shared primitive contracts remain available; neither silently accepts
v2 fields. New source/package identities require separate owner approval. Preserve
policy `0.1` text and obligations unchanged.

Use Python 3.11+ stdlib/POSIX and owned Git, strict JSON/schema, locking and atomic
evidence primitives. Extract shared evidence helpers from the v1 orchestrator so
the new package need not ship a target-execution route. Generalize only explicit
artifact/lock identity parameters, retaining v1 defaults. A deterministic new ZIP
contains only the external CLI/model/store, shared validation/inspection/storage,
schema2 and unchanged policy/license. Its trusted outside-target bootstrap verifies
the accepted-base lock and bytes before execution. A protocol2 shim only delegates.

The schema2 registry has exactly one required whole gate: producer identity,
canonical source/coverage/environment digests, accepted consumed-input mechanism,
effects, required observer controls, selected Git refs, budget and import window.
Other required privacy/review/product/index obligations are explicit unsupported
rows, each producing incomplete; they cannot disappear in a generic green gate.
Registry completeness is an owner mapping obligation, not inferred from prose.

The first supported subject is a single already-known committed first-party tree.
HEAD, clean checkout, staged-entry digest and selected refs are sampled for plan/
import freshness; this does not establish actual-index privacy or consumed bytes.
Actual consumed source and import origin need the accepted producer mechanism.
Actual-index/cross-phase obligations that cannot fit this subject stay unsupported.

## Obligation and permitted evidence basis

| Obligation | Permitted basis / failure behavior |
| --- | --- |
| Accepted base/head/trees, registry/lock/pin and current public metadata | Importer-observed hardened Git/byte identities; mismatch refuses/incomplete |
| Owner trust/provenance designation and independently approved input digests | Explicit outside-target operator assertion through an existing authenticated route; never authenticated by the payload itself |
| Canonical natural result, whole coverage, actual consumed inputs and environment/import origin | Registry-approved producer attestation tied to canonical/mechanism identities and exact context; always labeled external-attestation |
| Deadline, cleanup and any required containment/read-only/path/tool/network/disclosure/independence/privacy control | Separately approved controller-observation envelope with accepted observer/profile/mechanism identities, same invocation/context and actual state; a producer/manual assertion cannot supply this |
| Unknown/untrusted provenance | Actual accepted containment witness additionally required; absent declared mechanism/witness stays incomplete |
| Unsupported actual-index/private/reviewer/human/product obligation | Explicit incomplete row, never substituted by this one whole gate |

The observer envelope remains externally supplied evidence, not control enforcement
observed by the importer. Its approval digest/source must come from the existing
owner-authorized controller route. Parsing a claimed observation cannot prove it
was genuine; no real producer/controller trust is established in this task. Where
that route or real enforcement is absent, users must retain incomplete. Synthetic
records test this boundary; they are not a newly created/executed producer.

An issued plan may record an explicit owner designation for the exact trusted head.
Without that designation and matching reported provenance, containment is required.
The registry states whether owner designation is permitted or the subject is fixed
untrusted/always-contained. A caller designation never removes any registered
control, reclassifies that fixed subject or expands effects. An always-contained
registry must include its accepted containment profile.
The registry always requires deadline and cleanup observations for this slice;
other declared mechanical controls are equally mandatory. Controls marked unknown,
unavailable, manually asserted, wrong-profile or unapproved cannot pass. No required
mechanical rule is weakened to preserve policy0.1.

Observer records bind the approved observer/profile/mechanism, producer invocation,
exact plan/context/challenge and required control kinds. They must cover the full
execution interval (including clock precision uncertainty) and cleanup, through
an existing controller route outside producer/target control. A producer-route
statement cannot become an observation merely by changing an ID/basis label.
The importer relies on separately approved source/digest, not self-authentication.

## Data flow, effects and state

`doctor` validates schema2/pin and known clean target, then writes one authoritative
private plan/route record with a durable random challenge, context/registry digests,
source snapshot and issuance time before printing it. No command is dispatched.
Input files and state/cache/toolkit/target roots are separate; receipt bytes are
bounded, opened once without final symlink following and never treated as code.

`import` names that plan, an external producer envelope and independently approved
digest/producer, plus optional separately approved observer bytes/digest/identity.
Common context/challenge validation precedes per-record validation. One gate may
have malformed/duplicate extra records; a validated bound failure cannot be erased.
No cache, conditional applicability or pre-commit phase is accepted; explicit
unsupported input yields incomplete. Omitted required coverage/origin/controls
cannot become pass. Source-origin/subject binding must be valid before a purported
natural failure can be attributed to this target.

The owner-controlled state root has one per-target lock and one atomic authoritative
record per plan. Persist a validated natural failure before later independent
records/control parsing. Preserve original accepted evidence immutably; same bytes
retry idempotently, a new success cannot renew/replace it, and a separately validated
same-context conflicting failure is retained monotonically. Corrupt/unreadable state
is refused, never overwritten with defaults. Reports derive from that record.
Replay protection is local to intact state; no global ledger or execution claim.

Receipt result, coverage, consumed binding, provenance, controls, timing/output,
freshness, unsupported obligations and integrity are separate stages. Existing
fail over incomplete over pass semantics apply. Natural completed failure is
distinct from termination, wrapper/infrastructure error and unknown status.
Deadline codes alone are incomplete. A valid natural failure survives missing
controls, incomplete output/cleanup or later malformed evidence; a wrong source
origin is not a validated failure for the requested target.

Validate budget 1–3600 seconds and import window 1–900 seconds, with original
start/finish/elapsed facts and plan binding. These are validation ceilings only:
no external deadline is enforced by importing it, no old600-second cap changes,
and no real gate fit is claimed. Reimport never refreshes completion timestamps.
Passed evidence ages to incomplete when its window expires; same-context persisted
valid failure remains failure. Handled interruption writes known state when
possible; hard termination may leave only the last atomic record. Recovery imports
the same data rather than running/retrying a gate. Cleanup only owns partial local
writes, never external processes or producer artifacts.

Clock model: same host/boot, integer wall milliseconds plus local monotonic
milliseconds. A hashed OS boot identifier and accepted common clock model bind
producer/controller/importer relationships. Read only kernel boot metadata (Linux
boot-id or macOS fixed sysctl); other models are unsupported. Allow at most 1ms
timestamp precision uncertainty and 2000ms wall/monotonic continuity discrepancy.
Require plan issuance before producer start, ordered finish no later than import,
matching boot/domain and observer interval conservatively covering the operation
plus cleanup. Future time, pre-challenge invocation, reboot/rollback or unsupported
clock relationships are incomplete, not refreshed evidence. Inconsistent elapsed/
budget/window facts are separate incompleteness axes; once a natural failure is
validly bound, later timing/clock incompleteness cannot erase it. Wall elapsed never
proves a monotonic deadline was enforced.

## Concrete acceptance and verification

New invented repositories and data records cover bound success/natural failure,
context/head/ref/index changes, wrong pin/repository/provenance, missing controls,
partial coverage/wrong origins, malformed bytes/routes, finite budget/window,
termination versus failure, unknown cleanup/containment, interruption/recovery,
corrupt/replayed/conflicting state and all deferred modes. No producer/target command
is created or executed to generate a report. Test code may generate explicitly
invented JSON records only. Package qualification exercises the actual new ZIP and
protocol2 bootstrap/shim; relevant shared-primitive/v1-default regressions run without
repeating unaffected old-artifact suites for counts.

Source and new-package tests, independent adversarial code review/fix re-review,
exact-tree/staged publication checks and real README commands are required. Record
platform/runtime, source/tree/digest and limitations. No consumer read/edit/install,
dependency download, provider/private data, global registration, merge, release/tag,
hosted artifact publication or application operation is included.

## Independent critique/disposition

Independent read-only native critique found the architecture and policy0.1 basis
suitable after three corrections, all accepted: registry trust requirements cannot
be removed by caller designation; independent observer source/profile/invocation
and full interval/cleanup scope are required; and the clock model/order/uncertainty
must be explicit and fail closed. Their negative cases join the source/package
acceptance plan. The reviewer inspected public documents only, without code,
consumer/provider execution or private inputs. No obligation was relaxed.
