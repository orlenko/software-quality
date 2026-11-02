# Working on Software Quality

These rules apply to humans and agents changing this repository. Read [HANDOFF.md](HANDOFF.md), the relevant design, and the current git status and diff before editing. Preserve others' work.

## Scope and status

This is the shared policy and tooling repository. The candidate standard describes intended consumer practices; publishing it does not adopt it on any consumer's behalf. There is no implemented runner or release yet. Do not report proposed commands or test scenarios as working features.

Keep generic policy, schemas, orchestration and verdict semantics here. Consumer repositories keep their commands, architecture, threat model, permissions and explicit exceptions. Agent adapters invoke the pinned runner; they do not implement separate policy engines.

## Public repository

Development and orchestra rollout are scoped to personal projects. Keep employer and client identities, references, proprietary code, prompts, configurations and internal details out of public assets, including commit messages and discussions. Use personal project inputs and newly authored generic material.

Use invented data and newly authored examples. Never publish secrets, private source or user content, internal research, private checkout paths, captured transcripts, or confidential organizational details in files, logs, commits, issues or reviews. Review the actual staged content and metadata before pushing. Keep local credentials, reports and private notes ignored.

Ideas may inform new work; code, prompts and fixtures from other projects require their own redistribution rights and compatible licenses. Do not import private material as a shortcut.

## Design and review gates

Before nontrivial implementation, write the user problem, observable acceptance criteria, smallest alternative, responsibilities, data effects, failure behavior and test plan. Obtain an independent design critique and record the response. Keep architecture and runtime choices in short decision records under `docs/decisions/`.

Every code change receives an independent adversarial review before integration. Findings need a reachable scenario and consequence. Fix valid blockers and re-review affected fixes; track deferred nonblocking work. Review changes to the policy and runner against the previously accepted rules, not rules introduced by the change itself. The first implementation uses a separately recorded bootstrap review.

Run the safe checks appropriate to the change, bind results to the reviewed tree, and report failures and missing evidence honestly. Use a documented manual check when automation is unsuitable. Documentation-only work needs link, factual-status and publication checks rather than a fabricated runtime test pass.

## Execution boundaries

Separate source inspection from target-code execution. An approved test command can call scripts changed by the target diff. Unknown or untrusted code requires enforced containment; a worktree is not a sandbox. If the required execution or reviewer boundary is unavailable, report incomplete instead of running unsafely.

Reviewer tools and hosted source disclosure must stay within the existing authorization. Keep reviewer authentication away from target test environments. No silent hosted fallback, automatic source uploads, private-data access, application restarts, or consequential external writes outside the user's scope.

## Working agreements

Keep changes coherent and independently verifiable. Make the runtime, package, execution backend, reviewer interface and dependency choices explicit before adding implementation dependencies. Use strict types and validated boundaries in the chosen language. Reuse owned primitives and keep policy out of UI or harness-specific prompt copies.

Maintain the README's real install/run/test instructions as implementation appears. Commit and push useful plans, decisions and reproducible results; use a work branch for unfinished implementation. Keep one integrator and explicit ownership for overlapping work. Separate source integration, artifact build, publication and observed consumer adoption in every report.
