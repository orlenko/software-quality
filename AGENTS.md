# Working on Software Quality

These rules apply to humans and agents changing this repository. Read [HANDOFF.md](HANDOFF.md), the relevant design, and the current git status and diff before editing. Preserve others' work.

## Scope and status

This is the shared policy and tooling repository. The candidate standard describes intended consumer practices; publishing it does not adopt it on any consumer's behalf. The initial runner is a pilot candidate; no release or consumer adoption is claimed. Report only commands and scenarios supported by actual evidence.

Keep generic policy, schemas, orchestration and verdict semantics here. Consumer repositories keep their commands, architecture, threat model, permissions and explicit exceptions. Agent adapters invoke the pinned runner; they do not implement separate policy engines.

## Public repository

Development and orchestra rollout are scoped to personal projects. Keep employer and client identities, references, proprietary code, prompts, configurations and internal details out of public assets, including commit messages and discussions. Use personal project inputs and newly authored generic material.

Use invented data and newly authored examples. Never publish secrets, private source or user content, internal research, private checkout paths, captured transcripts, or confidential organizational details in files, logs, commits, issues or reviews. Review the actual staged content and metadata before pushing. Keep local credentials, reports and private notes ignored.

Ideas may inform new work; code, prompts and fixtures from other projects require their own redistribution rights and compatible licenses. Do not import private material as a shortcut.

## Design and review gates

This repository follows the [review and test process v0.3](docs/process.md), approved by the owner on 2026-11-13 ([decision](docs/decisions/0011-lighter-review-process.md)). It replaces the manual review workflow v0.2 here. Read it before changing anything.

Local facts for this repository:

- **Tiers.** There is no sensitive-path list here today, so code and configuration changes are C and Markdown-only changes are Docs. The runner is a pilot with no consumer route; when it gains one, the owner adds a path list.
- **Process text.** A change to `docs/process.md` or to this section needs the owner's approval before it is merged. Do not follow the review, re-review, retest, record or adoption rules in `docs/development-standard.md`; v0.3 replaced them.
- **Frozen file.** `docs/development-standard.md` is embedded in the runner package as policy 0.1 with a recorded digest. Do not edit it; put process changes in `docs/process.md`.
- **Design.** A new module, dependency, stored format or external effect gets a short design note under `docs/decisions/` and one independent critique before code.
- **Reviewer.** One independent adversarial review of the diff per change, by a fresh reviewer that did not write it.
- **Tests.** Focused: `python3 -I -S tools/test.py --match <regex>`; full, once on the final head: `python3 -I -S tools/test.py`. Markdown-only changes get a link, factual-status and publication check instead.
- **Owner decisions about process** are added below as dated lines.

2026-11-13: the owner approved process v0.3 for this repository and for the consumer repositories whose `AGENTS.md` points to it.

## Execution boundaries

Separate source inspection from target-code execution. An approved test command can call scripts changed by the target diff. Unknown or untrusted code requires enforced containment; a worktree is not a sandbox. If the required execution or reviewer boundary is unavailable, report incomplete instead of running unsafely.

Reviewer tools and hosted source disclosure must stay within the existing authorization. Keep reviewer authentication away from target test environments. No silent hosted fallback, automatic source uploads, private-data access, application restarts, or consequential external writes outside the user's scope.

## Working agreements

Keep changes coherent and independently verifiable. Make the runtime, package, execution backend, reviewer interface and dependency choices explicit before adding implementation dependencies. Use strict types and validated boundaries in the chosen language. Reuse owned primitives and keep policy out of UI or harness-specific prompt copies.

Maintain the README's real install/run/test instructions as implementation appears. Commit and push useful plans, decisions and reproducible results; use a work branch for unfinished implementation. Keep one integrator and explicit ownership for overlapping work. Separate source integration, artifact build, publication and observed consumer adoption in every report.
