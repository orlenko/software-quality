# Manual review-workflow verification

Reviewed source increment:
`719d1e8c20090e6d408d26997163fd4cf554581d`, tree
`3d683b71471ff6c6e67f8067a8af00409d8aac61`, against accepted baseline
`a61c56c8b8882a0f13b0a47fcdabbc8cdeafd7b3`.
The six-file change added 357 authored Markdown lines, counted as Git additions
plus deletions against that base, without generated/vendor exclusions. It stays
within the new recommendation; no size enforcement or runtime change was added.

Independent design critique preceded drafting. Its packaging correction and
operational requirements are recorded in [decision 0010](../decisions/0010-specialist-review-workflow.md).
Independent adversarial documentation review then inspected the exact six-file
delta against the previously accepted rules and found no reachable blocker.

A separate manual acceptance review exercised these invented scenarios:

| Scenario | Disposition supported by the instructions |
| --- | --- |
| 2,400 authored lines | Plan working increments below 1,000 where practical; an inseparable larger change records rationale and a bounded review plan without inventing a CI exception. |
| Authentication plus persistent data | Select separate security/privacy and data-integrity contexts at design and implementation; retain other applicability decisions. |
| Two duplicate findings and a distinct defect in the same file | Preserve every original ID/scenario; group only the true duplicate and retain the distinct defect. |
| Confirmed blocker despite clean majority or exhausted rounds | Remain blocked until correction/removal and affected re-review; no waiver. |
| Required reviewer unavailable | Remain incomplete regardless of a clean general report. |
| Source evidence refutes speculation | Record evidence and disposition; reconcile through the authentic report/owner route rather than silently rewriting it. |
| Stack parent/head changes | Invalidate affected evidence, rebind incremental reviews and validate the final combined tree/interactions. |
| Unapproved live route or unavailable fresh context | Remain incomplete without provider fallback, fabricated independence or substitute attestation. |

All eight manual cases had consistent dispositions; no document fix was required.
A separate adjudicator reconciled the finished source and acceptance reports,
checked their declared completeness and found no conflict or remaining blocker.
It had provided earlier design critique, but authored neither finished report and
did not adjudicate its own critique. These are observed native source/document
reviews, not mechanically enforced or recorded-v1 attestations.

At the reviewed increment, 96 local Markdown targets and two anchors resolved;
staged whitespace, factual-status and publication checks passed. Actual content
and public commit metadata were inspected; private paths, raw reports and
customer-derived identifiers/material were excluded. All 13 original/interim/new
archive hashes remained unchanged.

`docs/development-standard.md`, runtime code, schemas, config/lock, pins and trusted
bootstraps remain unchanged. **`docs/toolkit-design.md` changed and is a builder
input.** A future build would contain changed documentation and a new source/digest;
it requires separate qualification. No existing archive was rebuilt or relabeled.

This verifies a documented manual supplement and explicit source-process adoption
in this repository. It does not demonstrate automatic specialist dispatch,
adjudication software, live model effectiveness, authentic reviewer enforcement,
runtime tests, release or fleet adoption. No test suite, build or live provider
call was performed for this documentation change. Final integration and any pinned
metadata observation must retain their own exact source identities; they cannot
be inferred from these manual checks.
