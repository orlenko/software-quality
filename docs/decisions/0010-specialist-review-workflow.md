# Small changes, specialist review and adjudication

Accepted design, 2026-11-03, against source baseline
`a61c56c8b8882a0f13b0a47fcdabbc8cdeafd7b3`.

Problem: large overlapping changes make review difficult to finish; general
review can miss domain risks, and independent reports need evidence-based
reconciliation. The accepted approach is a strong small-change recommendation,
design decomposition, risk-selected lenses at both stages, an independent bug
hunt and a separate review adjudicator.

Acceptance is an operable manual procedure with reusable role instructions,
explicit inputs/outputs, finding and missing-review handling, and a practical
record format. Reviewers can use existing authorized routes. This is candidate
review-workflow v0.2, a manual supplement to accepted policy0.1; it is not a new
runtime policy release. This repository explicitly adopts its manual process
through AGENTS. Other repositories require their own owner adoption record.

The smaller alternative leaves the current general review without specialist
selection or reconciliation guidance. A new bot/service or generic orchestration
engine would add unnecessary implementation before validating the process.
Keep provider/model choice separate from role and use the existing approved
design-review route rather than copying its persona. A fresh owner-approved
Astra bug reviewer is the initial model candidate to evaluate, not a claim of
superiority or permission to call a provider.

The maintainer coordinates scope and authorized routes. Independent reviewers
inspect the proposal or exact implementation. An independent adjudicator retains
all report references, checks scenarios, groups duplicates and orders fixes;
the named owner handles unresolved disputes. An adjudicator cannot waive a valid
blocker, edit an authentic review into agreement or invent a missing review.
Authors fix code and obtain affected re-review and checks before integration.

Effects are public Markdown changes only: manual workflow, role checklists,
this decision, adoption/link notes and sanitized verification evidence. No runtime,
schema, config, lock, dependency, API, credential, hosted-posting or consumer
changes. Existing R2/A2 source identities, policy0.1, bootstrap bytes and archives
remain frozen; publishing instructions does not activate inference or a GitHub bot.

Independent pre-draft critique accepted the design with one packaging correction:
both builders embed `docs/development-standard.md` while runtime policy remains0.1.
Keep that standard byte-for-byte unchanged and publish a separate supplement,
avoiding a mislabeled future artifact. The correction was accepted before drafting.

The critique also required explicit lens selection/capabilities, genuinely fresh
bug review, separate completeness/disposition records, original finding identities,
exact-source fix/re-review binding and honest manual-versus-automated status.
All are incorporated. Native advisory review is not an enforced attestation.
The critic executed no source, tests, imports, APIs or Git writes.

Verification uses independent adversarial documentation review under the prior
baseline, local links/anchors, actual staged publication/metadata checks and manual
walkthroughs of large/stacked changes, conflicting findings, missing review,
stale source, false positives and persistent blockers. No runtime tests or live
model-quality result are claimed. Publish only newly authored generic material;
keep private evidence and customer-derived identifiers or content out of Git.
