# Manual review workflow v0.2

Candidate supplement to [policy0.1](development-standard.md), 2026-11-03.
This defines a usable manual process. Each repository records explicit owner
adoption, applicable routes and capabilities; publication does not adopt it fleet-wide.
This repository adopts it through [AGENTS](../AGENTS.md). Stronger local gates,
accepted-base rules, source disclosure and execution boundaries stay binding.

The current runner does not dispatch specialists or adjudicate reports. The
standalone source controller handles one bounded conversation and remains
unqualified for live use. These instructions add no automatic API calls, GitHub
comments, model fallback, merges or attestations. Missing required capability or
review remains incomplete. See the [design decision](decisions/0010-specialist-review-workflow.md).

## Plan small, complete changes

PRs should aim for about **500 changed authored lines** and strongly prefer
**fewer than 1,000**. This is a recommendation, not a CI or merge-size blocker.
Larger coherent changes should explain why splitting is impractical and describe
a bounded review plan. Stricter local limits still apply.

Count additions plus deletions, including handwritten tests, configuration and
documentation. Report generated/vendor content and pure mechanical moves
separately with their sizes and verification; those labels do not exempt risk or
justify hiding handwritten behavior changes. State the comparison base and counting
method so an estimate remains understandable.

During design, divide large features at behavior/responsibility seams. Give each
increment its own acceptance criteria, checks and dependency boundary. Each
integrated increment must work and pass its applicable checks. Separate mechanical
moves from behavioral redesign where practical; do not split into arbitrary slices
that require temporarily broken interfaces or lose the acceptance behavior.

For stacked PRs, identify each immutable parent/head and review each incremental
diff. Restacking or changing a parent invalidates affected descendant evidence.
Before the stack reaches the protected branch, validate the combined tree and
review cross-increment interactions. Recombining reviewed pieces never makes an
unreviewed merge result approved. Do not divide a mandatory full gate into passing
subsets or use a missing real Git index as a reason to fabricate one.

## Select reviewers before implementation

Write the user problem, observable acceptance, smallest useful alternative,
responsibilities, data effects, failure/recovery behavior and test plan. Identify
the proposed increments and select applicable lenses from the
[shared role instructions](review-roles.md).

Always identify the independent design/general review route for substantial
designs. Record specialist selection and rationale at both design and code stages:

| Lens | Typical trigger |
| --- | --- |
| Security/privacy | Authentication, permissions, secrets, sensitive data, untrusted input, new network/disclosure boundary |
| Data integrity | Persistence, migrations, transactions, shared stores, concurrency, partial writes or recovery |
| Reliability/performance | Background work, cancellation, timeouts, resource limits, contention, scale-sensitive paths |
| Product/domain/accessibility | Changed user workflow/output, domain claims, keyboard/assistive use or observable acceptance behavior |

For a lens not selected, record a short reason. A relevant unavailable specialist
is a missing required review, not an inapplicable lens. Additional locally required
routes cannot be collapsed into one general reviewer or dropped for cost, time or
model availability. Trivial changes within an established design need no new design
ceremony, but retain applicable code, documentation and local review obligations.

Give each selected specialist a separate reviewer context and report. Reusing a
conversation under several labels does not provide several independent reviews.

Bind each reviewer to its actual identity/role, exact proposal or source revision,
rubric revision, allowed inputs/tools/paths/network and disclosure scope. Assigning
a label, model or fresh conversation does not itself prove independence or enforced
permissions. Reuse the approved design-review mechanism; the role checklists here
are focus areas, not copies of another persona or a new permission grant.

## Review the design

Use independent skeptical general design critique and applicable specialist
lenses before substantial implementation. Review the proposed behavior and
failure modes, not imagined implementation details. Record findings, responses
and changed decisions, including the planned increments.

A separate adjudicator reconciles reports using the procedure below. At this
stage it recommends design decisions; critique remains advisory. The owner records
accepted/rejected advice and rationale. Existing privacy/security/authority rules
still apply, and an advisory label cannot authorize prohibited effects. Materially
changed design decisions receive affected critique before their implementation.

## Review the implementation

After an increment is written, run appropriate authorized focused checks. Give
an independent general bug reviewer the accepted rubric, exact base/head/tree,
acceptance criteria, relevant surrounding control flow and actual check results.
It should first form its findings without the author conversation or other
reviewers' conclusions. A reviewer with prior exposure must disclose it; a new
label cannot make that review fresh.

Use independent specialist implementation passes for the selected risks. Inspect
actual code and its dependencies, including boundary/failure paths and interactions
with earlier increments. Source inspection never authorizes executing unknown code.
If context, source access, authorization or required containment is missing, record
the exact incomplete scope instead of guessing or switching providers.

The general bug hunt looks for consequential functional regressions and ordinary
failure scenarios. It complements domain specialists. Keep role and approved model
separate: a fresh approved Astra reviewer is an initial candidate for this role,
not evidence that it outperforms a hosted reviewer. Live use needs its own approved
source/model/account route; an existing key grants no authority. GitHub review
delivery may be added later without changing these source/evidence rules.

## Reconcile reports and order fixes

The review adjudicator is separate from the implementer and the authors of the
reports being reconciled. It receives the accepted rubric, exact source/context,
all original reports and reviewer completeness records. It can request bounded
source evidence or a safely authorized reproduction; it cannot run target code
or acquire new access merely because a dispute is difficult.

For every finding:

1. Preserve original report ID/finding ID, location, scenario and consequence.
2. Check the claim against source and accepted behavior. Separate evidence and
   confidence from impact. Unsupported speculation needs clarification or a
   documented rejection; uncertainty about a required review remains incomplete.
3. Group only the same underlying defect. Retain all original references and
   each distinct scenario/consequence; related defects are not automatically duplicates.
4. Classify confirmed blockers versus improvements under the accepted rubric.
   Order fixes by impact, likelihood/reachability and dependencies. More votes,
   a preferred model or a desire to finish cannot establish correctness.
5. Record the decision, evidence, priority and next owner/action. Disputed findings
   go to the repository's named owner/adjudicator without erasing the original claim.

Keep **required-review completeness** separate from finding disposition. A clean
report from one lens cannot replace a missing required lens. An accepted valid
blocker remains blocking until fixed and re-reviewed, or its behavior is actually
removed/disabled through an authorized scope decision and affected re-review.
Reclassification, deferral, a review-round budget or an aggregate summary cannot
waive it. A rejected false positive needs evidence and recorded disposition;
disagreement with an authentic required report must be reconciled through its
approved review/owner process, not silently rewritten by the judge.

## Fix, re-review and integrate

Maintain stable finding/group IDs and source-bound dispositions. The author fixes
confirmed defects; the affected reviewer verifies the fix and relevant checks
rerun. Changed dependencies or new risk can require additional lenses. Resolved
findings reopen only for changed behavior or new evidence; untouched old claims
are not rediscovered as new work. Record deferred nonblocking items with an owner
and durable follow-up. No cycle limit automatically clears a known blocker.

Before integration, run the full applicable canonical gate, reconcile findings,
confirm required reviews are complete and bind evidence to the actual final tree.
A changed base/head invalidates affected evidence. Preserve incomplete stages and
definite failure priority; no adjudicator or model summary becomes a toolkit pass.
One integrator performs the separately authorized source integration. Release,
artifact builds, publication, installation and observed adoption remain distinct.

## Keep a compact record

The PR or linked durable record can use this shape; exact headings are optional:

```text
Problem / acceptance / increment boundary:
Accepted rubric and immutable proposal/base/head/tree:
Diff size and counting base; larger-change rationale if needed:
Required lenses; selection and inapplicability reasons:
Actual reviewer identities, permissions and completeness:
Original report references:
Finding/group | original IDs | evidence | blocker/improvement | fix priority:
Decision/dispute | owner | source-bound fix/re-review/check reference:
Full integration gate and final tree:
Remaining gaps and nonblocking follow-up:
```

The finding ledger is a manual coordination record, not an extension to
`recorded-v1`. Its grouping/priority/rejection notes must not be injected as
unsupported schema fields or used to convert a witness into an independent
attestation. Preserve authentic per-route evidence and its approval requirements.
Use neutral role names and newly authored examples. Customer-specific identifiers,
source, prompts, fixtures and confidential process details stay out of public assets.

Evaluate the process on a few small authorized changes using confirmed findings,
missed known defects, false positives and human agreement with dispositions.
Offline protocol checks do not establish live model effectiveness. Do not purchase
or activate another review service simply to complete this manual workflow.
