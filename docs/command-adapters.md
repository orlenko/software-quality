# Command/context candidate

The adapter is version `0.1.2`, protocol `1`; its
[compatibility record](../adapters/compatibility.json) will identify the separately qualified runtime source and digest after new qualification.
[The path correction record](reviews/approved-path-fix-v01.md) records the new
qualification; the earlier ownership correction stays historical. This is a software-quality source/skill bundle,
not an installed plugin, registered command or adopted consumer workflow.

The [Codex template](../adapters/skills/cmd-quality/SKILL.md) uses `$cmd-quality`;
the requested `$cmd_quality` spelling is not an implemented alias. The
[Claude template](../adapters/skills/quality/SKILL.md) can become local `/quality`
only after separate authorized registration. Plugin installations may namespace
both names. Official [OpenAI documentation](https://learn.chatgpt.com/docs/build-skills)
describes explicit skill invocation; official [Claude documentation](https://code.claude.com/docs/en/skills)
describes local slash invocation and plugin namespaces. These are documented host
interfaces, not evidence this new package has been discovered by either host.

Both templates reference one [procedure](../adapters/workflow.md). Preserve the
entire package, including supporting resources. The existing skills distribution
owner confirmed that eventual plugins retain their skills/resources within the
package and use host manifests/catalogs; this task does not edit that repository,
create host manifests there, install plugins/hooks, or change global settings.
Do not place a head-modifiable adapter/launcher in the target and trust it as bootstrap.

## Build and verify the bundle

From a clean reviewed adapter-source checkout:

```sh
python3 -I -S tools/test.py
python3 -I -S tools/package_adapters.py --output dist/quality-adapters-0.1.2-root-alias.zip
python3 -I -S tools/test.py \
  --artifact dist/software-quality-0.1.2-root-alias.pyz --adapter-bundle dist/quality-adapters-0.1.2-root-alias.zip
```

The runtime and adapter source identities are separate. Build the runtime from a
reviewed source commit, qualify its actual bytes, then record that source and digest
in the adapter compatibility metadata before building the adapter bundle. Packaging
an adapter never advances a consumer's accepted pin. The bundle contains `bin/`,
`skills/`, shared workflow, compatibility, license and source/file-digest manifest;
it has no installer. Tests extract only the owned verified bundle into disposable
state. The full shared trust/process closure must accompany the frontend.

The previous adapter 0.1.0 bundle and core 0.1.0 artifact remain frozen historical
objects. Their [original evidence](reviews/command-adapters-v01.md) stays historical;
those affected routes are held from new adoption. New 0.1.1 qualification is
recorded separately and does not establish adoption. No plugin installer or standalone registration installer is supplied.
Copying only a skill directory breaks its shared resources. Local unqualified names
are documented host forms, not a tested install recipe for this bundle.

The first local 0.1.1 bundle is also held: aggregate review found its advertised
simple shim still bypassed owned cancellation. Historical
`quality-adapters-0.1.1-relay-fixed.zip`, from source S3 in the ownership correction
record, fixed that relay. Those exact S3 bytes remain frozen but are also held after
the later path-selection finding. The new 0.1.2 candidate requires its own source/digest and qualification;
no older file is silently replaced.

## Explicit mode works offline

Use approved outside-target adapter and launcher sources plus a trusted Python
3.11+ interpreter on macOS/Linux. For source mode, `FRONTEND` is
`APPROVED_ADAPTER_SOURCE/adapters/quality_context.py`; in a separately approved
unpacked bundle it is `APPROVED_BUNDLE/bin/quality_context.py`. No extraction or
registration has happened merely because a ZIP was built.

```sh
python3 -I -S "$FRONTEND" \
  --launcher "$APPROVED_LAUNCHER" --python "$APPROVED_PYTHON" \
  --repo "$TARGET" --identity "$PERSONAL_REPOSITORY" --personal \
  --base "$ACCEPTED_BASE" --head "$IMMUTABLE_HEAD" \
  --cache "$APPROVED_CACHE" --state "$PRIVATE_STATE" --action doctor
```

All values are owner-approved inputs; full IDs are required. `--personal` is an
owner eligibility assertion, not proof from a name/remote. The expected repository
must match accepted-base configuration. Core config/lock/entry point remain
authoritative, including required checks/review routes. The retained
[simple shim](../adapters/quality.py) still supports its original explicit-target
argument format. Missing prerequisites/pin/protocol/evidence never trigger a fetch,
install, provider substitution or head-side bootstrap.

Doctor produces an incomplete plan until required check/review evidence exists.
Follow the actual shared workflow and [review protocol](reviewer-protocol.md),
then use `--action check` and the real outside-target `--review`/`--review-sha256`.
Only forward `--execute-trusted` under existing authorization for the exact trusted
change and accepted wrapper/effects. The context helper does not perform live
review, prove reviewer permissions or create substitute attestations.

## Optional GitHub metadata

The skill prefers an already authorized metadata connector, with explicit-ID core
arguments and manual before/after context verification. It cannot infer a provider
permission from availability. If the environment explicitly chooses CLI metadata,
replace `--head` in the frontend command with:

```text
--pr 7 --allow-github-metadata
--github-cli APPROVED_OUTSIDE_TARGET_GH
--github-config APPROVED_OUTSIDE_TARGET_AUTH_DIRECTORY
```

`--current-pr` selects only one open candidate for the attached same-repository
branch, whose local HEAD must equal the PR head. Zero/multiple/full-page candidates,
fork ambiguity, detached/moving branch, closed/moving PR, missing local objects or
base different from the owner-approved base refuse/incomplete. Explicit PR mode
may inspect a different locally available head. No Git object fetch occurs. In PR
mode trusted execution also requires explicit expected `--head`; metadata cannot
designate new trusted code. Unsupported context can use explicit full-ID mode with
the missing current-PR freshness claim clearly recorded.

Only fixed GET metadata endpoints on `github.com` are supported. Use an existing
owner-approved auth directory, not target-selected configuration. The controlled
environment omits inherited GH tokens/debug/proxy/settings, disables prompts and
sets host/config explicitly; telemetry and update notifications are disabled.
The [GitHub CLI API](https://cli.github.com/manual/gh_api) and
[environment](https://cli.github.com/manual/gh_help_environment) references document
these flags/settings. The REST metadata response, including descriptions,
reaches the approved gh process; client-side projection emits only identity/ref/state
fields. No raw responses, credentials, PR body or other source/media are printed
or persisted by the frontend. No live metadata query was used to qualify this
increment; tests use an invented executable and responses. Enterprise hosts,
proxy-dependent routes and automatic auth provisioning are unsupported here.

The selected PR is observed twice before delegation and once afterward. Current
mode also compares local ref/HEAD. A final separate `context` JSON line records
immutable target, selected observations, `core_exit`, context completeness and PR
freshness. Explicit mode records `not-requested`. Stable observations do not lock
the remote PR or replace exact-tree integration. The core report stays unchanged:
it concerns immutable commits. A moved/missing context cannot turn its pass into
a current-PR pass. Frontend exit is `1` for observed core failure, otherwise `2`
for missing/stale context or incomplete core, and `0` only for core pass plus
complete requested context. Handled cancellation is incomplete context and forwards
to the owned launcher, preserving an observed failure.

The engine still has no untrusted containment, real Git index in exports, live
reviewer integration or check timeout above 600 seconds. Consumer privacy/product/
domain/integration obligations remain separate where unsupported; partial/cached
tests do not stand for their full gates. No consumer execution/install, live-review
upload, release publication, comments, fixes, merges, restart or deployment is
authorized by this package. Consumer rollout remains separately scoped.

Approved paths retain their caller spelling until the shared traversal check.
Every symlink hop is checked before selecting canonical Python/launcher/client/auth
objects. Safe outside aliases and caller-relative inputs remain supported, including
safe parent steps; a relative selector starting within the subject is refused even
when it would later exit. The simple shim requires one exact `--repo VALUE` or
`--repo=VALUE`; duplicate/abbreviated repo forms and `--` ambiguity refuse before
selecting a tool. Other launcher policy stays in the pinned runner. Existing final-
symlink restrictions and bounded stable-filesystem limits are explicit in decision 0007.
