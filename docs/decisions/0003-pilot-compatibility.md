# Proposed compatibility contract: external canonical-gate evidence

Status: design proposal, 2026-11-02. No feature, schema, wrapper, execution,
installation, release or adoption is implemented by this decision. Governed by
accepted repository rules at `908995c`. Private planning informed the problem;
this document and its examples are newly authored generic material.

## Problem and decision

An established personal application needs real index/history/ref/conditional and
long integration gates. A small personal experiment also needs its actual index,
preprovisioned dependencies, exact import origins and separately authorized input
and human evidence. A raw Git-free export cannot truthfully reproduce all of that.
A successful public subset cannot qualify the missing obligations.

**Select A: propose a strictly context-bound, owner-trusted external-check receipt
interface.** Reuse canonical gates within their existing approved workflow, import
their evidence as external attestations, and retain every unsupported requirement
as incomplete. Importing evidence never authorizes its execution. The toolkit would
validate identity, provenance, coverage and completeness; it would not claim to have
executed or contained the external command.

| Option | What it can establish | Cost / decision |
| --- | --- | --- |
| Current candidate, diagnostic only | Immutable inspection and honest missing-stage reports after an accepted bootstrap | Supported today within its documented limits; retain this fallback |
| A: external canonical-gate receipts | Explicitly trusted attestations for the actual workflow and consumed inputs | Proposed minimum; operator/producer trust is unavoidable and visible |
| B: Git-aware snapshot wrapper | Selected checks on an explicitly modeled Git-aware snapshot | Reject as universal/default compatibility fix: a manufactured index/ref/cache/private-input environment is not the actual one |

B remains a possible later backend for genuinely snapshot-safe checks. Making it
general would require new Git/filter/ref/worktree ownership, dependency/import
isolation, private-input permissions and enforced execution boundaries. A copied
index is still synthetic; setting up a temporary Git directory does not demonstrate
the actual staged-index privacy gate. Those costs are larger than importing existing
authorized evidence and still leave manual/product/reviewer obligations unresolved.

Observable acceptance for A: one future report distinguishes actual-index evidence
from snapshot evidence, complete canonical gates from subsets/cache hits, operator
attestation from observed execution, and required controls from actual controls.
Wrong/stale/unproven evidence cannot pass. A valid required failure survives another
route's missing evidence, timeout, cleanup uncertainty or malformed extra record.

## Preserve the current candidates

- Runner: source `74b9b498058b11a3d99409e2d1166cbf9d171e9e`, artifact SHA-256
  `9403401102f01d87991fb2de5405eff4b7012480c955e858b8bb0a0fa2bee6a2`;
  engine/policy/schema `0.1.0`/`0.1`/`1`.
- Adapter: source `5843cf3f1375c40338d0ca4338241641a4d5fee9`, bundle SHA-256
  `3f7f0bb6be8ced3d1e3f47e749449fcac0ef9923d4b56162f16ce9a5ff313142`;
  adapter/protocol `0.1.0`/`1`, final evidence at `908995c`.

The current [configuration](../../quality/schemas/config.json) caps executed checks
at 600 seconds. [Exports](../../quality_trust.py) omit Git metadata and refuse
symlinks/gitlinks. The [review contract](../reviewer-protocol.md) requires its accepted
boundary and labels external attestations. There is **no** current external-check
receipt or conditional applicability mechanism. Neither existing pin changes here.

## Proposed boundary and follow-on scope

The [detailed contract](../compatibility-contract-v01.md) is the single specification
for input scopes, operator trust, actual controls, freshness, coverage, budgets,
failure and recovery. The [case data](../cases/compatibility-v01.json) records
hypothetical outcomes, never executed results or runtime inputs.

Responsibilities stay explicit: consumer owners establish canonical gate semantics,
producer authenticity, authorized effects and actual enforcement; an execution owner
runs/cleans up an already authorized gate; the toolkit would only validate/import
its evidence and inspect authorized public metadata. It cannot retroactively contain
an external job, prove an attestor truthful, or authorize private input/disclosure.
All raw evidence/credentials/private inputs stay outside public assets. Only a later
importer would write owned local plans/route records/reports; this task writes docs
and invented data only.

Proposed next implementation: import-only `external-checks-v1`, strict accepted-base
registry and context/control validation, outside-target provenance, atomic local
plan/route state, per-axis reporting and synthetic source/package checks. Propose
engine/package `0.2.0`, schema `2` and launcher/adapter protocol `2`; no version or
policy change is approved here. Retaining policy `0.1` depends on accepted-rule
review of each obligation's evidence basis. Actual producer/wrapper/dependency setup,
reviewer enforcement and consumer bootstrap/install are separate later scopes.

Known-target receipts do not solve every real pre-commit gate. Cross-phase reuse,
actual private checks, cache/selection equivalence, safe import origins, real budgets
and enforcement, stable pilot selection, local policy and human/product evidence
remain explicit prerequisites. No repeated author question or new inventory is
needed to finish this generic design. The current incomplete diagnostic alternative
is available without pretending these prerequisites are solved.

## Independent critique and response

A separate native read-only design reviewer inspected the public proposal/cases
against accepted `908995c` rules, without execution, private planning or providers.
All material findings were accepted: establish consumed inputs beyond endpoint
comparison; distinguish natural command failure from timeout/wrapper termination;
bind cache origin/equivalence/challenge/freshness explicitly; and preserve valid
non-applicability without allowing unexplained zero work. Corresponding negative
and positive cases and detailed rules are recorded in the contract.

Bounded clarifications were also accepted: explicitly limit known-target/pre-commit
reuse; use one durable authoritative local plan/route record for crash/replay
semantics; distinguish unreadable envelopes from malformed records; keep budget
enforcement with the execution owner; and leave policy/evidence-basis approval
unresolved. This critique is advisory design evidence, not a runtime test pass or
approval of a new execution/provider route.

Affected-design re-review found no remaining design blocker or policy weakening.
Its final precaution was accepted: original accepted evidence stays immutable,
while a subsequently validated same-context conflicting failure is retained and
forces fail rather than being ignored as a duplicate. A dedicated thirtieth case
records that invariant. Review is suitable for this bounded proposal only; it
does not approve implementation, execution, policy change or adoption.

## Validation and publication

Document/data checks: JSON syntax, unique IDs and declared fields for 30 invented
cases; local link resolution; manual scenario/authority/factual-status inspection;
whitespace and actual staged content/metadata/privacy inspection before push.
Runtime/schema/bootstrap/adapter files and both recorded artifact hashes remain
unchanged. Main and the completed adapter branch retain their previous revisions.
No runtime suite, consumer gate, package build, installation or live reviewer is
run for this design. Case outcomes are proposed semantics, not observed passes.
