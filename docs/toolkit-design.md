# Shared software quality toolkit

Candidate design, 2026-11-02, alongside the [development standard](development-standard.md). This repository holds shared quality rules and the initial runner candidate. The [implementation decision](decisions/0001-minimal-runner.md) and [README](../README.md) describe its bounded explicit-target/manual-review interface. Release publication, live reviewer automation and consumer adoption are not implemented or claimed.

## One source with small consumers

This repository will contain the generic policy, design and code-review rubrics, a small command-line runner, configuration schema, agent adapters, and its own tests. Keep consumer-specific test commands, architecture maps, threat models, and exceptions in the consumer. A reference to an existing local document is enough; adopting the toolkit must not mean copying the standard into `AGENTS.md`.

The existing public skills repository already distributes agent-neutral skills and a design-skeptic plugin. Reuse that distribution path for thin adapters where practical; do not maintain a second full design-skeptic persona or bury toolkit execution logic in two different harness prompts. Keep each persona's source in one place and package or reference it with an explicit version. A standalone CLI lets humans and automation use the same workflow. Harness adapters translate invocation and progress reporting only.

The desired experience is `/quality` or `$cmd_quality` resolving the current PR and calling the pinned runner. The CLI must also accept an explicit repository, base and head so direct-to-main repositories and experiments without PRs can use it. The exact harness registration is an implementation detail to verify in each supported harness; the runner contract is authoritative. Independently updated adapters must resolve the consumer's accepted pin, check their protocol compatibility, and leave policy and verdict semantics to that artifact. An incompatible adapter reports an actionable failure; it must not substitute another version or rubric.

## First useful release

Keep the first release to configuration validation, exact-diff inspection, trusted local checks, one independent review route, and a structured evidence report. Start with one general code-review lens and the existing design-review lens; add specialist routing only where pilots show that it catches missed defects. Do not start with a fleet scheduler, database, dashboard, automatic fixes, merge controller, hosted service, or telemetry.

Conceptual commands for the broader design; see the README for current Python entry points:

```text
quality doctor
quality check --pr 123
quality check --base <accepted-base> --head <reviewed-commit>
quality design <proposal-path>
```

`doctor` validates the pin, schema compatibility, required tools, local check definitions, independent reviewer availability, and isolation declarations. It reports gaps without installing hooks or changing repository settings. `check` resolves the target, shows its execution plan, runs authorized checks and review, and writes a local report. Without an authorized execution or reviewer route, it performs inspection and reports incomplete. Existing session authorization remains usable; it must not ask again on every invocation.

Design critique stays advisory, with recorded responses; code blockers govern integration. Initially, all output stays local. Posting a PR comment is a separate authorized action. Fixing code, committing, pushing, merging, deploying, and changing the policy are outside the first runner's effects.

## Reproducible releases and updates

Release one tested artifact from an identified source commit. Publish a readable version tag and an artifact digest; consumers lock the full source identity and digest, rather than trusting a mutable tag or `latest`. Initial adoption approves the repository identity, known source revision and expected digest through an authenticated maintainer/review path. A checksum fetched beside an arbitrary download proves consistency, not publisher trust; it cannot establish its own expected pin. The installed artifact includes policy and schema versions, source revision, and runtime requirements. Version engine, policy, and schema explicitly so a runtime fix cannot silently change review obligations.

A tiny launcher should resolve the pinned install from a local cache and run offline once installed. Initial installation or an intentional update may fetch a verified release. Validate downloaded content before extraction or execution, keep installs immutable, and refuse a missing or mismatched pin. Do not run downloads as shell scripts or install arbitrary dependencies during a review. Keep toolkit, target checkout, and run-output paths distinct and verify the resolved repository identity.

Normal upgrades are small reviewed pin changes, with release notes and policy differences. The conductor can coordinate the same upgrade across repositories, with a pilot first. Do not silently advance consumers at session start. A central withdrawal notice can flag an unsafe version and require an upgrade; it cannot silently substitute different code. Cached operation is reproducible, but offline status must not imply that the tool checked current withdrawal notices. Rollback selects a previous verified release and records why.

Apply the previous accepted toolkit and rubric when reviewing a toolkit update or a consumer policy/configuration change. Resolve the lock and configuration from the accepted base, not the PR head. Use an already trusted installed entry point or base-version launcher; never execute a head-modified bootstrap script to discover the trusted runner. Otherwise the change could approve itself by relaxing its own rules. Bootstrap the first release with an independent recorded design and code review. Development-checkout overrides are explicit and marked experimental; their reports cannot stand in for release qualification.

## Local configuration

One small versioned file plus a lock record should declare only local facts: check commands and their effects, state-isolation entry point, architecture and threat-model references, review route, integration policy, and approved exceptions. Keep credentials outside configuration. Use strict schema validation; unknown fields, missing required assets, unsupported schema versions, and missing reviewer routes must produce an actionable failure or incomplete result. No silent fallback that weakens the review.

Show the effective merged policy and configuration, including their origins. Shared mandatory rules cannot be switched off by a local override. Optional additions may be merged by named key; changing or removing a protection must be explicit and approved. Every configured behavior must have an end-to-end test showing that the runner actually consumes it, rather than merely accepting and printing it.

Check the accepted base configuration and commands when reviewing an untrusted PR; proposed configuration is input to review, not authority to execute. For initial adoption, an authorized owner approves the initial configuration. Treat source, PR descriptions and comments as review data, not instructions that can alter the runner's policy or authority. Inspecting source must not execute PR code. Base-approved command text is insufficient protection: the PR can modify the scripts, imports or build plugins it calls.

Declare execution mode and required capabilities. **Trusted local** mode applies only to changes designated trusted by the owner's accepted workflow, with disposable state roots. **Untrusted** mode requires an enforced disposable boundary that restricts host paths, secrets, network and processes as needed by the threat model; a git worktree alone is not that boundary. Unknown provenance defaults to untrusted. The first release may lack an untrusted execution backend: it must then inspect/review without running that code and report the required tests incomplete. `doctor` reports absent or insufficient isolation rather than claiming safe execution.

The reviewer route must also declare tool permissions, accessible paths, network use and whether source reaches a hosted provider. A CLI running locally is not evidence that inference stays local. Use the repository's authorized provider and disclosure scope, with read-only review permissions; do not silently fall back to a hosted model or give a reviewer arbitrary shell access. Missing authorization or required containment makes that review stage incomplete. Keep provider credentials separate from the environment that executes target tests.

## Evidence and failure handling

Each run records target repository, base/head/tree identities, toolkit source and artifact identity, policy/schema versions, effective configuration digest, check commands and results, reviewer identity and report reference, accepted exceptions, and remaining gaps. Record whether the source tree changed or the evidence became stale. Keep reports local and ignored by default; explicitly publish only a sanitized evidence summary to the repository's durable location.

Use three outcomes: **pass**, **fail**, and **incomplete**. A missing required check, skipped required reviewer, invalid reviewer output, timeout, interrupted run, or stale source identity makes that stage incomplete, never pass. Overall, a definite required-check failure or valid blocker takes precedence: **fail** even if another stage is incomplete; otherwise any incomplete required stage means **incomplete**; only all required stages passing means **pass**. Preserve every stage's status in the report. Validate findings against a small schema; a model's claim of success is not the runner's final result. Include a concrete scenario, location, consequence, severity and disposition. Keep findings deduplicated without dropping independent defects.

Give runs unique identities. Prevent conflicting runs from overwriting reports, propagate subprocess failures, and clean up only artifacts that the run owns. Prefer a single run at a time per target initially; add wider concurrency controls only after measuring contention. Reports distinguish a queued review from a running review and a completed local report from an externally published one.

## Test the toolkit as a product

Use small invented fixture repositories for Swift, TypeScript, Python, and documentation-only changes. Replay recorded reviewer responses to test parsing, severity handling, and report generation without model calls. Keep a few known-defect cases to check that useful review coverage survives policy changes; deterministic replay cannot prove live-model accuracy.

Test both source and packaged artifact: clean installation, offline pinned use, integrity failure, schema mismatch, effective configuration, moving PR head, missing reviewer, interrupted run, dirty checkout, mixed failure/incomplete results, and equivalent adapter arguments. Include a malicious head-side configuration/launcher change, a changed build script behind an unchanged command, missing containment, and an adapter update attempting to bypass the pin. Change expected results through review rather than automatically accepting new snapshots. The toolkit's own release must pass its independent gate and artifact smoke test before consumers adopt it.

## Ownership and delivery

The conductor names one toolkit maintainer and one integrator per consumer. The maintainer owns generic rules, schemas, releases and compatibility notes; repository owners own local facts and integration. The conductor reconciles disputed cross-repository policy and approves exceptions. Keep a ledger of adopted versions and verification references, not a separate review database.

Agree the pilot baseline and this narrow contract, then implement the minimal runner, pilot it on one established product and one lightweight experiment, and reconcile findings before tagging a broadly recommended release. Consumer migration should be one small pin/config/adapter change per repository; no wholesale rewrite of existing instructions.

The repository is `orlenko/software-quality`; newly authored material uses the MIT license. Before implementation, settle runtime and packaging, execution backend, supported independent reviewer interface and integration workflow. Use existing installed reviewer capabilities first; do not require a new API subscription or hosted upload. Keep public assets standalone and documentation links resolvable. Inspect source licenses before reusing any source code. The implementation must be newly authored, using portable engineering patterns rather than importing private code, prompts, or fixtures.
