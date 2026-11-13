# Lighter review and test process

Owner decision, 2026-11-13, against source baseline `36b0b85`. It introduces [review and test process v0.3](../process.md) and retires the manual review workflow v0.2 accepted in [decision 0010](0010-specialist-review-workflow.md).

## Problem

Features in the owner's personal repositories took far too long. Most agent time went to reviewing, re-reviewing and retesting, and very little to writing code. These are personal applications; the process had grown to match a larger product.

## What was measured

Thirty days of git history, hosted and local review results, CI runs and agent session records across the active personal repositories. Detailed evidence is kept privately. In summary:

- Findings that turned out to be reachable defects with a real consequence came almost entirely in the first review round. Of the sampled findings from round four onward, one mattered, and an earlier review fix had introduced it.
- Later rounds mostly reviewed code that earlier fixes had added.
- Review missed environment and integration faults. More defects of consequence reached the main branch and were found by use than were caught by review, and most of them were on a small set of sensitive paths. Most review rounds were spent on changes that touched none of those paths.
- A new review after a clean result, a rebase or a merge from the main branch found nothing.
- Specialist lenses and adjudication produced a large volume of findings, of which two mattered; both were deferred and neither had been fixed at the time of this decision.
- Reviewing design and process documents in rounds found nothing that mattered.
- In two of the repositories test runs were the largest share of agent time in the sampled sessions, because the full suite ran on every intermediate head. On one long series of changes in a third, review took more than half of agent time and writing code about one percent.
- Reviewer style findings raised as high severity cost rounds without preventing defects.
- Agents had extended "bind evidence to the reviewed tree" into digest and byte-count checks of every review document, which no rule asked for.
- In one repository a narrow reviewer rubric with a round budget had already cut findings per change by an order of magnitude with no visible rise in escaped defects.
- An owner instruction to lighten the process was lost when one agent session handed over to another.
- The runner in this repository returned "incomplete" on every consumer run and no session invoked it. Its cost was adoption paperwork.

## Decision

Adopt process v0.3:

- The tier of a change comes from the files it touches, using a short sensitive-path list and trigger list in each repository.
- One review round per change. A re-review happens only after a fix to a blocker, looks only at the fix diff, reports blockers only, and is capped at 1, 2 or 3 rounds by tier. A cap never clears a blocker; an open blocker at the cap goes to the owner.
- The full suite runs once, on the final head. A review stands after a conflict-free rebase or merge.
- No specialist lenses by default and no adjudicator below the top tier. One design critique per feature.
- Sensitive changes get a short smoke checklist built from the defects that review missed.
- A blocker is fixed in the same change or blocks the merge. Only the owner may defer or accept one, in a dated line.
- Owner decisions about process are written as dated lines in the repository's `AGENTS.md` so they survive session handoffs.
- A short record replaces the ten-field review record. No digest or byte-count binding of documents.

The rules on secrets, private data, safe tests, external effects, format compatibility, untrusted code, hooks and regression tests are unchanged, and only the owner may change the process text, a repository's process block, its "do not report" list or its tier and style scripts, or remove or weaken a hook, a CI check or a gate.

## Alternatives not taken

- Keep v0.2 and add round caps only. This leaves the specialist, adjudication and record costs, which produced the least.
- Drop review for low-risk changes. The first round is where review earned its cost, so it stays for all code.
- Make the runner enforce the tiers. The runner is a pilot with no working consumer route; rule text takes effect now and scripts follow.

## Effects

Markdown only. `docs/development-standard.md` is unchanged byte for byte, because it is embedded in the runner package as policy 0.1 with a recorded digest; where it differs from v0.3 on design critique, review, re-review, retesting, records and adoption paperwork, v0.3 governs in repositories that point to it. No runtime, schema, configuration, lock or dependency change. The runner remains a pilot in this repository. Consumer repositories adopt v0.3 through their own owner-approved edits; publishing this text adopts nothing on their behalf.

## How this change was reviewed

`AGENTS.md` required a change to the process to be reviewed under the previously accepted rules, which means the full v0.2 workflow. The owner decided that this transition is reviewed once: this decision record plus one independent critique of the plan and of the process text, followed by the owner's approval of each repository's edit. That is a one-time exception made by the owner, recorded here.

The independent critic reviewed two drafts of the plan and accepted the fourth. Its corrections are incorporated: the tier is decided from the changed files and never by an agent's judgment; a cap sends an open blocker to the owner and never clears it; trigger lists were added after path lists alone were shown to miss known escapes; smoke items that would touch a live keychain or account were split into automated items in throwaway environments and owner-run items; the merge-on-green exception excludes repositories where a merge ships by itself.

The critic then reviewed the process text and this record. Changes made as a result: the owner-only rule now covers a repository's whole process block and any weakening of a hook, CI check or gate; files that instruct agents, hooks and CI configuration are never the Docs tier; accepting or deferring a blocker is stated once, as the owner's decision in a dated line; the reviewer marks each finding as blocker or not, and a rejected blocker mark is recorded; the "do not report" item on same-user races was narrowed to hostile programs, so races between a repository's own sessions stay reportable; a feature a person can turn on in a shipped build counts as running code; a review that runs after a merge leaves a pending line in the record; the Release tier was limited to version numbers, checksums and URLs of release artifacts.

## Check after two weeks

On 2026-11-27 the same measurements are repeated: review rounds per change, time from first commit to merge, share of agent time in test runs, `Escape:` lines by tier, the share of changes in tier B per repository, any `Reviewed: pending` line whose review never ran, and a sample of tier C findings that the reviewer marked as blockers and the author rejected. If escapes rise on tier C code, that surface is proposed to the owner for B.

## Follow-up

Issue policy 0.2 of the development standard with the sections that v0.3 supersedes removed and its digest updated, as an ordinary change, so that the frozen text no longer states rules that are not in force.
