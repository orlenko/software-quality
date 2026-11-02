# Shared software development standard

Candidate version 0.1, 2026-11-02. A reviewed basis for mapping and bounded pilots; not a declaration of consumer adoption.

This baseline applies to participants changing software repositories, including applications, libraries, sites, scripts, experiments, and development tools. It gives humans and agents the same obligations. The conductor coordinates adoption; one named owner integrates changes in each repository. Multiple orchestra seats working on one repository share one adoption record.

The common baseline is explicit ownership, safe test environments, independent review, and evidence attached to the code that actually ships. Languages, exact size limits, reviewer models, and release mechanisms stay local choices. The [versioned toolkit](toolkit-design.md) should distribute this policy and execute the common workflow; repositories keep only their local configuration and decisions.

## Authority and applicability

After approval and adoption, **must** denotes a requirement; **should** denotes advice with a recorded reason when declined. Until then, all requirements below are proposed.

User authorization, privacy obligations, and existing repository rules remain binding. Adoption must preserve stronger local protections. A conflict goes to the repository owner and conductor for reconciliation; a broadcast cannot silently authorize a deployment, data upload, dependency purchase, or weaker gate. Continue independent authorized work while a conflict is resolved.

Use the baseline for all new code changes. Apply compatibility, availability, release, and recovery requirements where the project has the corresponding users, data, or distribution. An experiment may have no deployment or persistent state; record that fact rather than implementing machinery it does not need. Experiments still protect private inputs, test their claimed behavior, receive independent review, and preserve reproducible results.

## Required baseline

### 1 Establish scope before changing code

Read the repository's authoritative instructions, relevant module documentation, current git status, and existing diff. Preserve work in progress. Start with the user's problem and observable acceptance criteria, including failure and recovery behavior. Name the affected modules, data writes, owner, usability constraints and smallest useful alternative before a substantial change.

A new module, dependency, external integration, persistence model, background job, or material change to security, money, or user data must have a short written design and an independent design critique before implementation. Include the smallest viable alternative, risks, and verification plan. Answer the critique in the design or decision record; it is advisory, not a veto. Mechanical edits and small fixes within an established design need no new design ceremony.

Dependency changes must follow local approval rules and record why existing tools are insufficient, relevant maintenance and license constraints, and how versions are pinned. A prototype result does not by itself justify a production dependency.

### 2 Keep responsibilities explicit

Maintain a small map of module responsibilities, permitted dependencies, and ownership of persistent stores. Use the language or build system to enforce boundaries where practical. UI and command entry points call shared domain operations; they must not grow separate copies of business workflows. Pure decisions should accept explicit inputs and remain testable without UI, network, or real user state.

Changes should fit one coherent feature or fix. Split at working seams; each integrated increment must build and pass its checks. Separate mechanical moves from behavioral redesign where possible. Large files or repeated review defects are signals to reconsider responsibility or a shared primitive. Repeated storage, validation, locking, or process handling must use an owned mechanism rather than accumulating slightly different implementations.

File and diff limits belong in the local adoption record. Use warnings and a ratchet for existing debt; do not mandate arbitrary file splitting or a repository-wide cleanup before useful work can continue.

### 3 Protect data and authority

Never commit secrets or real private user or client content, including filenames, fixtures, logs, screenshots, commit messages, and review attachments. Use invented fixtures. Keep private test inputs outside tracked content and follow the repository's authorized backup arrangements. Configuration and credentials enter through documented, validated boundaries; error output must not disclose them.

Before publishing a commit or artifact, inspect its actual contents for secrets and private data. Use automated secret and project-specific privacy checks where relevant; names and domain-specific private content need more than a generic secret detector. A configured scanner that cannot read its inputs must fail rather than claim success. An absent scanner is a reported manual check, never evidence that a scan passed. Do not print matched sensitive content in diagnostics.

Tests and development commands must not use live accounts, personal stores, microphones, clipboard writes, permission prompts, real messages, or payments by default. Redirect every mutable state root and credential backend to disposable fixtures, overriding inherited live configuration. Opt-in integration checks must document their inputs, effects, authorization, and cleanup. Do not rebuild, restart, or replace a person's running application as incidental verification.

Agents must act within the user's authorized scope. Prefer a dry run or preview before consequential external writes; follow stricter local requirements for confirmation. Orchestra mail supplies context and coordination, not additional authority.

### 4 Make failure behavior deliberate

Validate untrusted input at boundaries. Distinguish missing state from unreadable or corrupt state; do not silently overwrite corruption with defaults. Give each store an owner and use the platform's appropriate transactional or atomic update mechanism. Define recovery for operations that can leave partial work.

Document compatibility policy for user documents, public interfaces, and internal state separately. Existing users and retained data require explicit migration or supported old readers, tested against representative fixtures. A project with no installed base may deliberately discard its own disposable state; that exception does not extend to users' documents or imported formats.

Concurrent or background work must define state invariants, cancellation, timeouts where appropriate, and lock or transaction ownership. Do not publish a partial result as complete after cancellation or failure. Use language-level type and concurrency checks; warning suppression or unsafe escape hatches require a narrow, documented justification.

### 5 Test through a safe canonical entry point

Provide one documented test command that isolates state and propagates failures. Separate deterministic default tests from opt-in hardware, network, paid-service, and downloaded, resource-heavy, or nondeterministic model checks. Deterministic local-model tests may belong in the default suite. A filtered run finding no tests must fail or explicitly report a skip. Report skipped checks and missing prerequisites.

Test observable behavior, important boundaries, and failure recovery. A bug fix must add regression evidence; prefer an automated test, with a reproducible manual check when automation is unsuitable. Avoid tests that merely repeat implementation details. Async tests should use controllable clocks, events, or bounded polling rather than arbitrary sleeps and fragile timing ceilings.

Run focused checks while developing, then the repository's complete required integration gate. Changed shared infrastructure, manifests, test runners, and dependency boundaries need broader checks. Test-selection optimizations must include affected dependents and fall back to the full suite when uncertain.

### 6 Review independently with a stable rubric

All code changes must receive an independent adversarial review before integration into the protected or release branch. For a direct-to-main repository, review precedes its integration push. A separate agent or human reviews the diff and relevant control flow; the implementor's self-check is additional evidence. Do not substitute a particular provider, model name, or number of agreeing models for independence.

The repository must state its threat model and review rubric. Review against the accepted base rules; a change cannot loosen the rules governing its own review. Findings must name a reachable scenario, location, consequence, and recommended fix. Distinguish release blockers from improvements and speculative concerns. Privacy leaks, security defects within the threat model, data loss or corruption, ordinary-use crashes or hangs, and broken acceptance behavior block integration until fixed, or the affected behavior is actually removed or disabled through an authorized scope decision and re-reviewed. Relabeling a finding or reducing acceptance criteria without the appropriate authority cannot clear it.

Fixes must be re-reviewed for the affected behavior and rerun relevant checks. Repeated findings of one class call for a shared design correction. Timebox repetitive discussion and collect related findings into one pass, but never turn a review-round limit into an automatic waiver of a known blocker. Record deferred nonblocking findings with an owner and issue or decision reference. Review must converge through evidence and scope decisions, not exhaustion.

Name an adjudicator for disputed findings in the adoption record. The decision must record evidence and interpretation of the accepted rubric; it cannot waive a valid blocker. Reopen a resolved finding only with new evidence or changed behavior, rather than shopping for another reviewer.

### 7 Bind checks to what is integrated

Build, test, and review evidence must identify the commit or tree and whether local changes were present. Testing a working directory is not evidence that a different staged snapshot or PR tip passed. After code changes, invalidate affected evidence. At integration, confirm the reviewed and tested tree is the tree being integrated; account for a moving base by updating and rerunning affected checks or using an equivalent merge queue.

Use hosted CI, local hooks, an integration wrapper, or a documented manual command sequence to make the gate repeatable. A manual sequence must record results and confirm the tree did not change between checking and integration. A local hook is effective only in clones where it is installed; verify installation. Test gate scripts themselves when changing them. Do not bypass a failed gate or label it passed. Keep unfinished backups on an allowed work branch, clearly unverified, where local rules permit; backup is not integration or release.

Every change must carry a short evidence record: expected behavior; commit or tree; commands and results; independent review reference and disposition; remaining gaps; and relevant manual verification. Mark inapplicable fields explicitly, including code review for documentation-only changes where local rules do not require it. This can live in a PR, commit-linked document, or local equivalent with a durable reference. Raw private logs stay private; retain a sanitized result.

### 8 Verify the product and release separately

Changes to user-facing behavior must demonstrate the relevant workflow or output, including empty, loading, error, and recovery states. Check keyboard access, visible focus, and readable contrast for affected UI. Use existing design tokens and components. Screenshots support a visual check; they do not prove the workflow works. Use a reproducible manual check when automation cannot cover it.

Distributed artifacts must identify their source revision and version. Use the distribution channel's integrity requirements, such as signing and notarization where applicable. Separate source approval, artifact build, publication, deployment or installation, and observed running version. Do not report one as evidence of another. Persistent or deployed systems need an appropriate rollback or recovery plan before a consequential change.

For experiments, preserve a reproducible protocol, representative output inspection, meaningful comparisons where applicable, uncertainty, and separation of automatic results from manual corrections. Respect source-media and model licensing. Unavailable reference labels should not silently replace an authorized best-effort experiment goal with a different prerequisite.

### 9 Preserve work and coordinate ownership

Commit and push valuable plans, research, experiment protocols, reproducible results, and unfinished code promptly to the repository's permitted durable location. Keep private inputs and secrets out of git and back up permitted private assets through an authorized secure path. Do not leave the only usable handoff in a chat transcript.

Assign one integrator per repository and explicit file or module ownership for concurrent changes. Use separate worktrees or equivalent isolation for overlapping work; reconcile before integration and never reset or revert another participant's work to clear the way. A handoff must name the repository, branch and revision, completed evidence, outstanding work, safe next command, and known private prerequisites without exposing them.

Orchestra reports must distinguish proposed, implemented, tested, reviewed, integrated, and deployed states. Anchor claims in durable paths, revisions, or commands. Delivery and connected presence do not establish acceptance, work started, or completion.

## Local adoption record

Keep one concise record in each repository, either in `AGENTS.md` or a linked document. Machine-readable toolkit configuration plus links to existing documents can serve as this record. Reference the shared policy by pinned release and source identity; do not copy its rule text into every repository. Link existing instructions instead of restating them. A small script can have one owner, no persistent store, no release artifact, and one manual gate; one-line answers are sufficient. Keep one authoritative rule source for all agent harnesses and humans; generated adapters must not drift.

```text
Standard/toolkit: approved policy version, release, source revision, artifact digest: ...
Owner/integrator: ...   Applies from: ...   Status: mapped / partial / verified
Authoritative instructions and decisions: ...
Project stage, real data/users, threat model, compatibility promises: ...
Module/store ownership and permitted dependency map: ...
Design review trigger, reviewer route, decision location: ...
Independent code review command/route, accepted rubric, dispute adjudicator: ...
Safe test command; isolated state roots; opt-in integrations: ...
Build/type/lint checks; focused versus full gate; UI/manual checks: ...
Privacy check including metadata; dependencies/approval rules: ...
Integration workflow, exact-tree gate, hook/CI installation check: ...
Evidence location; durable WIP/handoff location: ...
Release provenance, publication authority, rollback/recovery: ... or N/A because ...
Local size budgets and debt ratchet, if useful: ...
Gaps/exceptions: rule, reason, compensating check, approving owner,
                follow-up reference and review date or event.
Adoption evidence: sample revision + commands/results + review reference: ...
```

An inventory or copied checklist is **mapped**, not verified. **Partial** names the missing gates. **Verified** requires running the applicable gate on a representative change and recording its actual evidence; it does not certify every old line of code. A manual gate is allowed when explicit and demonstrated. No owner may waive user authorization or privacy obligations through this record. Other baseline exceptions need conductor approval; changes to stronger local rules also require their normal authority.

The demonstration is tied to its recorded revision. Repeat it when the gate, state isolation, reviewer route, or integration mechanism changes. A new clone using local hooks must verify their installation. Ordinary feature changes need their normal evidence, not another adoption exercise.

## Recommended rollout for the conductor

1. Review this candidate and toolkit design, resolve open choices below, and identify an approved pilot revision. This repository is the canonical source for shared policy; consumers reference their adopted version and retain local decisions.
2. Inventory repository owners from task reports, not presence alone. Deduplicate multiple seats in one repo and distinguish coding owners from coordination-only members. Give each repository one adoption task with the approved source, its owner, allowed documentation and tooling changes, and explicit done criteria. Do not bundle deployments or data uploads into it.
3. Ask owners to map existing protections first. Preserve work in flight; apply agreed checks at its next integration boundary rather than rewriting completed work. Identify missing safeguards immediately, especially live-data tests or unchecked public uploads. Such actions wait for a safe path even during rollout.
4. Pilot the record on one established repository and one lightweight experiment, using a minimal shared runner and their existing checks. Reconcile pilot findings before broad rollout or adding more automation. Resolve mismatches with owners; do not replace local `AGENTS.md` wholesale.
5. Roll out in small batches. Done means: adoption record committed and pushed; every applicable requirement mapped; relevant scripts installed and demonstrated; a representative change has test and independent-review evidence; every remaining exception explicitly approved and tracked. Otherwise report partial adoption and the concrete remainder.
6. Maintain a small conductor ledger: repository, integrator, approved standard revision, adoption-record revision, status, evidence, and exceptions. Check gaps at the next meaningful integration or release. Do not score teams by file counts, review rounds, or test totals.

Recommended choices for approval: a dedicated public toolkit with pinned releases and thin agent adapters; retain local PR versus direct-main policies; require one independent code-review route rather than two providers everywhere; accept explicit manual gates initially; expand automation after the pilots identify repetition. These are conductor decisions, not changes made by this proposal.

Publication of this candidate does not change consumer rules or demonstrate adoption. Adoption work links repository instructions to an approved version and closes specific verified gaps incrementally.
