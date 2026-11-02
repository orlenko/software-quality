# Proposed external canonical-gate evidence contract

Design only, not an implemented protocol or permission to execute. The
[decision](decisions/0003-pilot-compatibility.md) chooses this bounded interface and
records its independent critique. Examples are invented non-executable case data.

## Proposed identity, trust and freshness contract

Only an accepted-base registry may name a required external gate, its canonical
entry/source identity, input scopes, allowed effects, provenance/boundaries, evidence
basis, applicability rule and budget. A PR/head-side adapter, summary, config or
response cannot select those rules or change the trusted importer. Source identity
covers scripts/imports/plugins called behind unchanged command text. Unknown target
provenance still requires actual enforced containment; otherwise execution evidence
is incomplete, including when execution happens outside the toolkit. A mutating
merge/deploy driver is not a substitute check; integration/publication observations
stay separate under their own authority.

The proposed envelope is data only, supplied outside the target/toolkit/cache with
an independently approved digest through the owner's authenticated evidence route.
Accepted producer identity and expected digest establish the chosen trust path,
not mathematical proof of execution. A self-supplied checksum, identity string or
timestamp cannot authenticate itself. The first interface would be unsigned and
explicitly operator-trusted, with no source upload, provider fallback or credential
sharing. Consumers that require stronger producer authentication cannot pass using
this interface alone.

Each planned run would issue a fresh local challenge bound to the exact repository,
accepted base/head/trees, config/lock/tool/policy/schema identities and required gate
manifest. A producer records that context during its normal authorized gate run;
the importer never starts or demands a duplicate run merely to populate a report.
Without a previously issued challenge, existing results remain separate diagnostic
evidence; wait for a normal authorized run or separately approved work, rather than
manufacturing a binding afterward. Cache reuse has the explicit exception below.
Duplicates never choose the last result; replay protection is limited to the intact
owner-controlled local record described under recovery, not a server/database.

The receipt must preserve these **declared and actually consumed** axes as required
by its accepted gate. Matching only the headline commit is insufficient:

| Scope | Required binding and invalidation |
| --- | --- |
| Committed source | Exact base/head/trees and canonical gate/tool identities |
| Actual staged index | Actual entries/modes/stages and content identity before/after, plus intended committed tree; a synthetic index is a different scope |
| History/refs/ref stdin | Ordered commit set, required base/current-main refs, actual invocation inputs and any selected dependents |
| Working/untracked/ignored inputs | Exact approved readiness/identity witness for inputs actually consumed; missing private inputs stay missing |
| Dependencies/imports | Check interpreter/environment/lock/distribution identities and first-party resolved import origins/content, with accepted generated-artifact rules |
| Applicability/coverage | Accepted selector identity and immutable inputs, required selected gates and their completeness; no unexplained skip/zero-selection |
| Timing/effects/control | Budget, elapsed/completion/cleanup evidence, authorized effects and actual control witnesses |

Pre/post observations must be stable, but equality alone does not establish which
inputs were consumed. Each accepted gate must name its identity mechanism: immutable
reads, owned serialization/locking covering other writers, runtime instrumentation,
or an explicitly accepted external attestation mechanism for that fact. Record
`endpoints-matched` separately from `consumed-inputs-established`. A file/index/ref
that changes and is restored during a gate does not qualify on endpoint comparison
alone. Required mechanical enforcement cannot be supplied by a weaker manual claim.

Applicable public metadata is checked again
at import and at the owner's normal integration gate. A finite freshness window
is necessary but never sufficient. A changed index/ref/input/dependency/selector
invalidates affected evidence immediately. A stale or unrelated failure is not
silently attributed to a new context. Another valid, bound failure still wins.
Private inputs/readiness witnesses and raw output remain private; public summaries
use only deliberate sanitized facts, not private names, patterns, hashes or paths.

The first proposed interface accepts only receipts already bound to a known target.
Its positive application case is a canonical gate whose normal subject is already
known commit H, not an arbitrary pre-commit invocation.
It does not promote a pre-commit receipt into proof for a later commit merely because
one tree matches: gates may also consume HEAD, metadata, message, refs and private
inputs. Partially staged or historical pre-commit evidence remains separately scoped;
if it cannot bind the requested committed target, that obligation is incomplete.
Any safe cross-phase reuse needs its own reviewed equivalence rule, not a hidden
normalization or a compulsory extra consumer run.

## Coverage, dependencies and actual controls

All obligations remain in the accepted registry. An external canonical selector may
attest that a locally conditional subgate is not applicable only with its accepted
identity, complete input set and explicit reason/witness. Report applicability
separately from execution. The importer does not execute arbitrary predicates or
infer correctness from a zero exit, summary, filtered test count or cache label.
Missing/changed selectors, unexplained zero selection, or zero work for an applicable
required gate are incomplete. A witnessed false accepted condition satisfies only
the applicability obligation; it never claims command execution. Required shared
rules cannot become conditional. A post-failure scope edit cannot clear a blocker.

A complete cached result is usable only if the accepted canonical gate explicitly
allows reuse and its equivalence rule binds every required source/input/ref/
environment/coverage axis. A requirement for an uncached run cannot use this route.
Record original result ID, original completion/context/outcome/coverage and producer,
current canonical invocation ID/challenge, equivalence rule/version and the actual
current equivalence assessment with its consumed-input mechanism. Preserve all
original times; a new attestation/challenge cannot renew them.

For non-cached work, the import window starts at that canonical invocation's actual
completion. For permitted cache reuse, it starts at completion of the new challenged
canonical equivalence assessment, **and** original result age must remain within
the accepted cache-age limit (proposed ceiling 3600 seconds, default zero/disabled).
The assessment must re-establish every required volatile axis and complete scope;
it is not a timestamp-copying operation. Report cache reuse as cache reuse, not a
new uncached run. Missing original identity, age policy, assessment or mechanism
means incomplete, not renewed freshness. Otherwise insufficient caching remains
partial evidence. Do not split an overlong whole gate just to fit the current
timeout: equivalence must be established independently before such decomposition
can be accepted. Per-commit and affected-dependent coverage must include the entire
accepted commit/target set, with an explicit whole-gate fallback where required.

Preprovisioning is a separate authorized activity. The receipt must distinguish
toolkit Python from check Python, approved dependencies from unexpected downloads,
and imports from the bound source from editable imports in another checkout.
Fresh environment roots alone establish none of these. Missing environment/origin
witnesses are incomplete. An absent private input causing a skip does not pass its
privacy check; a source-only subset remains source-only. An already accepted manual
alternative needs its own actual bound evidence, never a relabeled scanner pass.
This proposal neither
opens private inputs nor permits their use or disclosure through an attestation.

Represent three separate objects: **required controls** from accepted policy,
**actual controls** with state `enforced`, `unavailable` or `unknown` and their
mechanism/evidence references, and **manual facts** with an identified attestor and
scope. Every observation also declares its basis: toolkit-observed metadata,
external producer attestation or manual fact. An attestation about enforcement is
not enforcement performed by the importer. Unknown/unavailable actual controls
cannot satisfy an enforced-control requirement; a flag or identity string alone
does not supply the missing witness. Evidence basis must meet the accepted rule.

The first increment would not launch reviewers or weaken the existing read-only,
path/tool/network/disclosure and independence obligations. Inaccessible review
routes remain incomplete. Local inference or source-review authority cannot be
inferred from where a CLI/viewer runs. Human/product/experiment evidence stays a
separate required obligation where the consumer already requires it; unit/coverage
success cannot establish domain accuracy. Do not create a new reference-label
prerequisite or backfill unavailable historical design critique.

## Finite budgets, failure and recovery

Proposal: external routes declare an owner-approved whole-gate wall budget of
1–3600 seconds, plus a finite receipt-import window no greater than 900 seconds
after completion. These are proposed ceilings, not evidence that any consumer fits
them. Local executed checks retain their existing 600-second limit. A longer
external budget would require an explicit reviewed registry/version adoption;
there is no override in the frozen runner. Runs that need more than the proposed
ceiling remain unsupported until a separately justified decision.

The external producer/its existing execution owner must own timeout, cancellation,
process-group cleanup and disposable effects. Elapsed time inside a budget does
not prove an enforced deadline existed; any required timeout/cleanup mechanism
needs its own actual control witness. The importer cannot stop or contain
an already external job. Receipts record actual elapsed/completion and separate
command result, output completeness, cleanup and input stability. Unknown elapsed,
budget overrun, interrupted output or unverified cleanup is incomplete even with
zero exit. An outcome witness distinguishes a naturally completed required command
from deadline/signal termination, wrapper/infrastructure failure and unknown
completion. A valid bound naturally completed nonzero command remains failure when
another axis is incomplete. A timeout wrapper's 124/137 (or any unexplained nonzero)
alone is not that witness: termination-only evidence is incomplete. Do not infer
outcome kind from the number or discard a witnessed natural failure after cleanup.
SIGKILL may leave orphaned work; inspect/reconcile owned processes and
effects before retrying. No implicit retry of a non-idempotent gate.

Validate common context first, then each required route independently. Invalid
common context is unbound/incomplete. Unreadable/invalid envelope bytes cannot yield
a trusted route by salvaging fragments. Inside a valid bound envelope, a malformed
extra route must not erase a
valid failure elsewhere. Preserve valid failures in conflicting duplicates and
interrupted import. Overall remains fail over incomplete over pass; pass means
all required obligations complete under their accepted evidence bases, with
`external-attestation` labels intact. It does not certify historical code or adoption.
### Proposed local record and crash scope

One authoritative plan/route record lives in the owner-controlled, ignored state
root outside target/toolkit/cache; producer receipt files are separately outside
those roots. The run challenge/context must be durable before it is handed to a
producer. A per-target lock in that shared state root excludes concurrent import;
one atomic replacement records each validated route's digest, result and consumed
status together. Persist a validated failure before processing later independent
routes. Reports are derived from that authoritative record, not independently
committed consumption/report files.

An interruption before acceptance leaves an incomplete pending route. Retrying the
same plan/route/digest resumes or returns its persisted result without executing
anything. Keep the original accepted evidence immutable. A second receipt cannot
replace that history or provide a new success, but a separately authenticated and
validated same-context conflicting failure must be retained as additional evidence
in the same authoritative record. Its aggregate becomes fail with conflicting
evidence incomplete, rather than ignoring a known failure because the slot was
consumed. Neither time passing nor a later pass erases a persisted valid failure
for the same context. If context changes, require a new plan and retain the prior result only
for its prior context. Recovery removes only owned unaccepted partial files and
never resets the record to make evidence reusable. Replay protection holds only
within this intact authoritative local state: deleting/cloning it, using another
state root or machine defeats global single-use claims. Lost state requires a new
plan; it is not permission to restamp old receipts. No server/global ledger is
proposed.

## Proposed implementation/version scope, not authorization

One later toolkit task may implement an **import-only** `external-checks-v1`
protocol: strict bounded data validation, accepted-base gate/subject/control registry,
plan challenge and outside-target evidence digest handling, source/input freshness
checks within authorized inspection, per-axis reporting and replay-safe local state.
Reuse owned Git/JSON/report primitives. It starts no target check, dependency
provisioner, reviewer, remote write or Git-aware execution backend for these routes.

Proposed identities: engine/package `0.2.0`, config/report schema `2`, and a new
approved launcher/adapter protocol `2` for explicit external-evidence inputs.
Keep the old engine/schema/protocol and artifacts available unchanged. Policy `0.1`
may be retained only if accepted-rule review confirms the local manual evidence
basis already satisfies every requirement; otherwise policy change/adoption needs
its own explicit approval. Neither version numbers nor this design approve that
choice. No silent schema migration, adapter fallback or consumer pin update.

Implementation acceptance would use invented repositories and producer records
for [these declarative cases](cases/compatibility-v01.json), including full
scope/negative cases, both prior artifacts unchanged, malformed/duplicate/replayed
receipts, moving metadata, wrong import origins, budget/interruption/cleanup and
failure precedence. Test both source and new package, then independently review
the code/fixes against previously accepted rules. Those tests have not run here.

Separate later consumer-owned work may establish an approved producer/wrapper and
dependency environment; actual private checks, reviewer boundaries, stable pilot
selection and installation each need their existing scope/authority. No consumer
or executable wrapper is created by the import-only toolkit proposal.

Unresolved before a real pilot: owner acceptance of operator trust/evidence basis;
which exact canonical inputs/selection/cache rules can be witnessed; safe dependency
and source-origin provenance; budgets and actual cleanup capability; real reviewer
enforcement/disclosure; stable accepted bootstrap/target; existing local policy and
product/human evidence. Preserve those decisions with their current owners rather
than repeating questions. Inspection-only incomplete rehearsal remains the honest
current fallback. No whole-gate or verified-adoption pass is available from this
design alone.
