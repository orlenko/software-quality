# Initial maintainer handoff

Prepared 2026-11-02. This is a documentation bootstrap for a dedicated quality-toolkit maintainer. No runtime implementation, consumer command, release tag, or consumer adoption is being claimed.

## User goal

Several personal software projects are developed concurrently by humans and agents coordinating through an orchestra. Their quality processes vary. Maintain shared development rules and reusable quality tooling in one public, tagged repository so improvements can be made consistently, without copying the full policy into every project.

The desired consumer experience is `/quality` or `$cmd_quality` processing the current PR through the same versioned runner. An explicit base/head mode must also support repositories that do not use PRs. Each consumer keeps a small configuration and lock containing local facts and the adopted version.

## Read and coordinate

1. Read [AGENTS.md](AGENTS.md), the candidate [development standard](docs/development-standard.md), and [toolkit design](docs/toolkit-design.md).
2. Inspect the actual checkout and existing diff. Another session may already be working here.
3. Connect through the installed Agent Orchestra skill using the session's own membership. Obtain the conductor's current implementation brief and repository-mapping results; report your repository identity, branch and role. A connected seat or delivered message is not task acceptance.
4. Reconcile the candidate with the current brief before implementation. Existing consumer rules remain binding, including stronger review gates and compatibility promises.

The architecture received independent design critique before this bootstrap. The candidate is suitable for mapping and bounded pilots, not a declaration that every repository has adopted it. The conductor coordinates rollout and has requested consumer mappings; use the current reports rather than repeating costly inventories. Prefer an established product and a lightweight experiment for the first pilots.

## First implementation milestone

Settle and record runtime/package, execution backend, independent reviewer interface, maintainer/integration workflow and dependency choices. The repository identity is `orlenko/software-quality`; newly authored bootstrap material is MIT licensed. Validate redistribution rights separately before introducing any third-party assets.

Then build the smallest useful runner:

- Validate configuration, the accepted version pin, prerequisites and execution/reviewer capabilities.
- Resolve an immutable target and accepted base configuration, lock and entry point.
- Show the effective plan and effects; run only the already authorized checks and independent review route.
- Validate stage results and emit a unique local evidence report tied to all source/tool identities.
- Return fail for a definite required-check failure or valid blocker; otherwise incomplete for missing or stale required evidence; pass only when all required stages pass.

Command names in the design are a proposed interface, not available executables. Keep the first release focused on one runner, one schema, one lock and one independent reviewer protocol. Existing skills can distribute thin adapters. Automatic fixing, posting, merging, deployments, telemetry, dashboards and fleet scheduling are outside this first milestone.

## Design findings already resolved

- Deterministic local-model checks may be normal default tests; costly or nondeterministic integrations can be opt-in.
- A documented manual integration sequence is valid when evidence and tree stability are recorded.
- Removing a blocker from scope requires an authorized decision and actual removal or disablement of the reachable behavior, followed by review.
- Disputed review findings need a named adjudicator and recorded evidence; valid blockers cannot be waived merely because review has repeated.
- Adoption evidence becomes stale when gates, isolation, reviewer routes or integration mechanisms change. Small projects can use short answers and links instead of extra paperwork.
- Base-approved command text is not sufficient trust: changed scripts, imports or build plugins may execute target code. Unknown provenance is untrusted; unavailable containment means inspection-only with required tests incomplete.
- Reviewers need enforced tool/path/network permissions and an authorized source-disclosure scope. A locally launched CLI can still use hosted inference.
- Approve initial publisher/source/digest identities through a trusted path. A checksum fetched beside an arbitrary artifact cannot establish its own trust.
- Adapter upgrades must respect the consumer's accepted pin and protocol. Head-modified bootstrap code must not choose the tool that reviews it.
- Keep per-stage completeness, with definite failure taking precedence in the overall result.

## Product evidence and qualification

Start designs with the user's problem, observable success and failure/recovery behavior, the smallest alternative, usability and complexity. Product checks demonstrate the affected workflow or output. For experiments, preserve the protocol, representative outputs, uncertainty and separation of automatic results from manual corrections; use meaningful comparisons where possible and respect media/model rights.

Test the runner with invented fixture repositories and recorded reviewer responses. Required scenarios include changed head-side launcher/configuration, a changed script behind an unchanged command, missing isolation, missing reviewer, invalid reviewer output, moving head, interrupted execution, mixed fail/incomplete results, adapter pin bypass, and invalid artifact/schema identity. Test both source and the packaged artifact; offline replay does not prove live-model accuracy.

The first pilot is complete when the pinned install and local configuration are committed, appropriate gates and independent review are demonstrated on a representative change, and gaps or exceptions are explicit. Report mapped, partial and verified adoption separately. Consumer edits and rollout remain scoped work coordinated with their owners.

## Next safe action

Read the design, confirm the live assignment with the conductor, and write the short implementation decision and independent design-review response. Implement only after those choices are recorded. No API subscription, paid model, hosted upload, or private reference is required merely to read this handoff or start the design.
