# Thin command and context integration

Status: proposed, 2026-11-02; governed by accepted rules at `e543e1a`.
The previously reviewed engine/artifact at `74b9b49` remains unchanged.

Users need a short harness entry that selects the intended personal repository
and exact change, calls its accepted runner, and explains missing review evidence.
The smallest alternative is the existing explicit-target Python shim plus brief
skill instructions. Keep it usable and add only bounded metadata resolution.

## Responsibilities and boundaries

New code stays in `adapters/`; core policy/schema/verdicts and trusted bootstrap
remain unchanged. A versioned compatibility declaration records adapter protocol
1 and the tested runner source/artifact. No new runtime dependencies. The owner
approves the adapter, launcher and Python paths outside the target; a head-side
adapter/config/branch/PR description is never authority to select code or a pin.

A shared `quality_context.py` frontend accepts explicit personal eligibility,
expected `owner/repo`, target path, full accepted base, approved launcher/Python,
cache/state and either a full head, explicit PR number or current-branch PR.
Eligibility is an owner assertion, not inferred from a GitHub username. Validate
identity against accepted-base configuration before metadata lookup. The core
still validates complete config/lock and controls artifact selection and verdict.
The existing simple explicit-target shim remains compatible.

Metadata lookup is opt-in: an explicitly approved outside-target `gh` executable,
owner-approved outside-target authentication directory, and explicit permission
for GitHub metadata reads. Select `github.com` in argv/environment, discard inherited
GH/debug/proxy configuration, disable prompts, and supply only the named auth source.
Fixed GET endpoints retrieve PR metadata (including descriptions at the gh process);
static client projection emits only allowlisted identity/refs/state. Do not claim
that projection prevents metadata retrieval. No diff/comments/media endpoints.
No implicit network, remote inference from a URL, fetching Git objects, credential
probes, extension execution or alternate provider. Use trusted Git primitives for
local inspection. Keep metadata-process credentials out of target test environments;
only the existing trusted launcher invokes the runner. Do not print response bodies
or credentials. Bound subprocess time and returned metadata bytes.

Skills prefer an already authorized metadata connector when available; they can
resolve immutable IDs through it and use explicit mode. The optional CLI route is
for environments that explicitly choose that route, not an automatic fallback.
This session uses invented responses only; no live consumer metadata request.

For explicit PR: require expected repository, open state, number, full base/head,
local object availability and metadata base equal to the owner-approved base.
For current PR: only an attached same-repository branch with exactly one candidate;
fork/current-branch ambiguity requires explicit PR or explicit full IDs. Never
choose the first candidate. Request one bounded page of 100; a full page is
potentially truncated and refused. Bind the attached local ref/HEAD before lookup,
immediately before launch and afterward, requiring local HEAD equal to the PR head.
Explicit-PR inspection may intentionally select another locally available commit.
Metadata can nominate a head for inspection, but
trusted execution in PR mode additionally requires an explicit expected full head
and the existing execution permission; a moving PR cannot authorize new code.

Read the selected PR twice before launch and again afterward. All selected identity,
base/head/ref/state fields must remain stable. Changes before launch refuse it;
changes or missing metadata afterward leave current-PR context incomplete, while
retaining a definite core failure. Even stable observations are not an atomic
GitHub integration gate. The core's report remains evidence for immutable commits,
not a mutable PR tip. Print a separate context receipt, with observed metadata,
core exit and current-PR completeness; never rewrite the core evidence/verdict.
Frontend exits preserve core failure; otherwise incomplete core/missing or stale
required context yields incomplete, and only complete context plus core pass passes.
Explicit mode records PR freshness as not requested.
Handled cancellation forwards to the owned launcher and leaves context incomplete.

## Harness entry and distribution

Author a concise Codex `cmd-quality` SKILL.md and Claude `quality` SKILL.md,
with shared procedure in a supporting reference. Codex's documented skill name
guidance uses hyphens; deliver `$cmd-quality` and clearly identify `$cmd_quality`
as an unregistered requested spelling, not a promised alias. Claude supports
`/quality` for a locally registered skill; plugin distribution may namespace it.
Never interpolate raw arguments into shell injection syntax or pre-authorize tools
in frontmatter. Inputs are data; resolve/quote argv deliberately.

Official source checks: [OpenAI skill guidance](https://learn.chatgpt.com/docs/build-skills)
describes explicit dollar invocation and SKILL.md discovery;
[Claude skills](https://code.claude.com/docs/en/skills) describes slash invocation,
local skill locations, plugin namespaces and argument substitution. Templates
are authored here, not installed/registered. No global settings, plugins, hooks,
consumer changes or writes in the skills distribution repository. Coordinate
layout compatibility with its owner. The owner confirmed skill-directory assets,
relative resources within the package and namespaced plugin invocations; no alias
or unqualified plugin name is established. Preserve one shared workflow and no duplicated
policy engine. Distribution must retain supporting references; copying only a
SKILL.md without its referenced procedure is unsupported.

The workflow first obtains a plan; commission every required independent recorded
review through existing authorized routes, then check with that actual external
response/digest. Never invent missing evidence or describe attestation validation
as reviewer execution. Report exact target, outcome and gaps, with current-PR status
separate. Stronger local checks, policy decisions and product evidence stay intact.

## Effects and failure handling

The frontend may read explicitly authorized GitHub metadata, inspect local Git
objects and invoke the approved outside-target launcher. The launcher writes its
normal unique local reports. Explicit trusted checks retain their existing owner
authorization and host-access limits. No default target execution, live reviewers,
source uploads, release publication, consumer installs/edits, posts, fixes, merges,
deployments or app restarts. Raw request data/credentials remain private.

Missing prerequisites, wrong identity, ambiguous/moving context, absent local
objects, closed PR or missing lookup permission refuse/incomplete. No automatic
fetch/install/retry through another repository/provider. Explicit-target mode
works offline and intentionally makes no current-PR freshness claim. Unexpected
subprocess exit/cancellation stays incomplete; preserve definite runner failure.

## Observable acceptance and checks

Invented fixtures cover explicit fallback and equivalent core arguments; unchanged
accepted artifact/pin despite head-side adapter/config edits; wrong repository;
missing tool/permission/object; ambiguous and moving PR/base/head; expected trusted
head; current branch/fork limits; safe fixed GET argument handling and credential
separation. Fake metadata executables are newly authored fixtures, never real gh
queries. Test commands through the retained pinned ZIP as well as source helpers.

Independent design critique and adversarial code/fix review precede integration.
Skill frontmatter/reference validation and independent scenario evaluation supplement
code tests; they do not establish actual harness registration. Document real setup
and explicit-target usage, version mapping, metadata authorization and deliberate
limits. Keep the original pilot artifact intact; no release tag or consumer adoption.

## Independent critique

The separate read-only native design reviewer assessed this before implementation
against accepted `e543e1a` rules. All four corrections were accepted: explicit host
and controlled outside-target authentication/environment; local ref/HEAD stability
for current-PR mode; explicit frontend exit precedence; and accurate description of
client-side projection versus retrieved metadata. Recommendations accepted: refuse
potentially truncated candidate pages, allowlist receipt fields, reuse trusted
`quality_trust.py` primitives, validate complete packaged skill references, and
retain immutable target/core/context identities on cancellation or lookup failure.
No target execution, private inputs or live metadata request occurred in critique.
