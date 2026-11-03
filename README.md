# Software Quality

A shared development standard and a versioned quality runner for humans and coding agents.

The path-corrected engine `0.1.2` is a pilot candidate, with policy `0.1` and schema `1`.
There is no published release or verified consumer adoption. The previously frozen
0.1.0/0.2.0 artifacts and adapter 0.1.0 stay unchanged and are held from new adoption
because of process identity and failure-finalization defects. See
[the correction design](docs/decisions/0006-owned-process-finalization.md); new
local candidates require their own reviewed source and qualification evidence.
[The correction record](docs/reviews/process-finalization-fix-v02.md) identifies
the separately built core 0.1.1, external 0.2.1 and adapter 0.1.1 local candidates
and their observed checks and limits.

The 0.1.1/0.2.1 runtime and corrected adapter 0.1.1 candidates also remain
historical and held after an independent integration gate found a path-selection
boundary gap. See the [path correction design](docs/decisions/0007-approved-path-traversal.md)
and [new evidence record](docs/reviews/approved-path-fix-v01.md). New patch artifact
qualification is separate from source integration and consumer pin approval.

Approved selector paths are inspected component by component before canonicalization.
A checked subject hop is refused even when symlinks or parents later exit it;
existing root device/inode identity also detects stable alternate root spellings.
Safe outside aliases and relative inputs are supported; relative tool inputs starting
inside the subject are refused. Existing final-symlink restrictions remain in force.
Inspection is bounded to 40 link expansions and 512 components on a stable owner
filesystem. This is not a race-free execution capability or hostile-code containment.
Initial Python/entry/support loading still requires an approved complete installation.
Cache outputs must be outside the toolkit; an install archive may live inside it.

## Start here

The toolkit's own [pinned inspection setup](docs/toolkit-self-adoption.md) is a
partial self-adoption: required target checks and authentic reviewer evidence stay
incomplete. It uses an approved outside-target R2 bootstrap, not head-side code.

The source-owned [manual review workflow v0.2](docs/review-workflow.md) adds strong
small-PR guidance, specialist review lenses, an independent bug hunt and finding
adjudication. It is a manual supplement to policy0.1; other repositories adopt it
explicitly. Automated orchestration and live reviewer activation are separate.

```sh
git clone https://github.com/orlenko/software-quality.git
cd software-quality
```

Read [AGENTS.md](AGENTS.md), then [HANDOFF.md](HANDOFF.md). The candidate [development standard](docs/development-standard.md) and [toolkit design](docs/toolkit-design.md) describe the intended behavior.

## Safe tests and build

Requires Python 3.11+ on POSIX and Git, with no third-party packages. Execution
requires a usable nonreaping `waitid`/`WNOWAIT` capability and the default SIGCHLD
policy; a benign interpreter probe runs before any target/helper launch. Unsupported
capability refuses execution. Windows execution is unsupported. Use a trusted interpreter with **`-I -S`**: without those
flags, Python startup code can execute before a script can refuse it.

```sh
python3 -I -S tools/test.py
python3 -I -S tools/build.py --output dist/software-quality-0.1.2-root-alias.pyz
python3 -I -S tools/test.py --artifact dist/software-quality-0.1.2-root-alias.pyz
```

Tests use invented disposable repositories and recorded reviewer responses, without
network, live accounts, private media or external reviewers. Test package identities
are synthetic fixtures, not release provenance. The builder requires a clean source
commit and nonexistent output, and prints source/version/SHA-256. Its deterministic
ZIP application contains code, schemas, policy and license; installation extracts
nothing. [Bootstrap evidence](docs/reviews/bootstrap-v01.md) separates actual source
review, packaged checks and missing evidence. Replay does not measure review accuracy.

## Explicit offline installation

Approve publisher `orlenko/software-quality`, full source commit, expected artifact
digest and trusted launcher source through an authenticated owner/review route. A
checksum beside an arbitrary download cannot approve itself. Keep `quality_launch.py`
and `quality_trust.py` together in an approved toolkit checkout outside the consumer
and cache. These files are the trusted bootstrap: never invoke head-side code to
choose them. No installer fetches, upgrades or selects `latest`.

The following values must be independently approved, rather than copied blindly:

```sh
TOOLKIT=/path/to/approved/toolkit
SOURCE=REPLACE_WITH_APPROVED_FULL_SOURCE_COMMIT
DIGEST=REPLACE_WITH_APPROVED_ARTIFACT_SHA256
CACHE=/path/to/private/quality-cache
python3 -I -S "$TOOLKIT/quality_launch.py" install \
  --artifact "$TOOLKIT/dist/software-quality-0.1.2-root-alias.pyz" \
  --sha256 "$DIGEST" --source "$SOURCE" --cache "$CACHE"
```

Installation creates a private regular cache file named by digest and validates its
inventory/metadata/bytes. Every invocation verifies cached bytes before executing.
An interrupted install can leave a refused partial entry: inspect/remove only that
entry and repeat the explicit install. Rollback chooses a previously approved pin
and records why. There is no online withdrawal check; offline use makes no claim
about current withdrawals.

## Accepted configuration and plan

Consumer adoption is a separate scoped owner decision. The invented
[configuration](examples/config.json) and [lock template](examples/lock.template.json)
show the formats; replace zero identities with approved values. Commit accepted
`.quality/config.json` and `.quality/lock.json` through the consumer's existing
gates. The first schema provides no policy waivers. Consumer commands, stronger
rules, architecture, threat model and integration remain consumer-owned.

The launcher and runner resolve configuration and lock **only from the accepted
base commit**. Unknown fields/versions are refused. All configured checks and
review routes are required. Referenced instructions/architecture/threat-model/
integration documents must exist at base. Changed scripts behind unchanged commands
still require an authorized execution boundary.

Keep target, toolkit, cache, reviewer response and state separate; state and cache
must be outside target/toolkit and each other. Share one state root per target for
lock coordination. Use full 40/64-character commit IDs. Expected repository identity
is an explicit operator input matched against base configuration, not remote
authentication.

```sh
TARGET=/path/to/consumer
STATE=/path/to/private/quality-state
BASE=REPLACE_WITH_ACCEPTED_FULL_COMMIT
HEAD=REPLACE_WITH_REVIEWED_FULL_COMMIT
IDENTITY=example/demo
python3 -I -S "$TOOLKIT/quality_launch.py" doctor \
  --repo "$TARGET" --base "$BASE" --head "$HEAD" --identity "$IDENTITY" \
  --cache "$CACHE" --state "$STATE"
```

`doctor` writes a unique report and prints the effective plan, declared effects and
immutable review context. It never runs target checks. Its incomplete result (exit
`2`) reflects missing check/review evidence. Inspection disables inherited Git
configuration/environment, hooks, fsmonitor, configured filters, replacement
objects, lazy fetching and external diff/text conversion. Object alternates are
unsupported. Exports use raw tree/blob contents without archive transformations;
symlinks, submodules, invalid paths and oversized exports leave execution incomplete.

## Independent review and check

Commission all required independent reviews using the emitted context and existing
permitted routes. Follow [recorded-v1](docs/reviewer-protocol.md); store the JSON
response outside target/toolkit and independently approve its SHA-256. This runner
does not launch reviewers, upload source/media or supply provider credentials. It
validates **external attestations**, not mechanically observed review execution,
independence, enforcement, actual disclosure or review quality. If the required
boundary is unavailable, retain incomplete evidence instead of inventing an
attestation. A local viewer sending private pixels into a hosted context is still
disclosure; source-review authority alone does not approve that.

The separate [source review controller candidate](docs/source-review-controller.md)
can produce bounded source-review witnesses after explicit public-source API
approval. It is outside the existing artifacts and does not generate independent
attestations or enable consumer execution. Its offline test command is documented
there.

```sh
RESPONSE=/path/to/private/independent-review.json
RESPONSE_DIGEST=REPLACE_WITH_INDEPENDENTLY_APPROVED_RESPONSE_SHA256
python3 -I -S "$TOOLKIT/quality_launch.py" check \
  --repo "$TARGET" --base "$BASE" --head "$HEAD" --identity "$IDENTITY" \
  --cache "$CACHE" --state "$STATE" \
  --review "$RESPONSE" --review-sha256 "$RESPONSE_DIGEST"
```

Unknown provenance defaults to inspection only: **there is no untrusted containment
backend**. To execute explicitly trusted maintainer changes, accepted config must
declare `trusted_local: true` and `isolation: owner-approved-wrapper`, and the
operator adds `--execute-trusted` under the existing authorization for the displayed
effects. The owner-approved wrapper must cover every real data store, credential
backend and network effect. Fresh HOME/TMP/XDG roots and a credential-free
environment do not isolate platform stores or restrict host access.

Checks use argv arrays and bounded time/output in disposable snapshots. A shell
explicitly named in argv has normal shell authority. The orchestrator makes no
external writes or target changes; trusted checks retain host access and can cause
their declared effects. No downloads, fixes, posts, commits, pushes, merges,
deployments, app restarts or telemetry are orchestrator actions.
Each check gets a fresh snapshot; tracked raw bytes and executable modes are
verified before/after. Mutations make snapshot evidence incomplete. Command exit,
bounded output/cleanup and snapshot integrity are separate required stages, so
missing output or mutated files cannot erase an observed command failure.

Private schema-validated `report.json` records exact source/artifact/policy/schema,
base/head/trees, config/lock digests, plan, command results, external review
boundaries/findings/dispositions, remaining gaps and checkout status before/after.
Raw bounded logs stay private. Ignore local state in the consumer and deliberately
sanitize any published summary.

Exit `0`: all required stages pass. Exit `1`: definite required command failure or
valid open blocker. Exit `2`: incomplete evidence/refused input. Failure wins over
incomplete. Dirty/moving source, absent evidence/capability, invalid review, timeout
and unfinished stages never pass. Unknown/duplicate review records cannot erase a
valid blocker. An initial report survives hard termination. Handled interruption
requests cancellation through owned process groups. Signals require an unreaped
identity; cleanup requires an actual wait and separate empty-group observation.
Uncertain cleanup remains incomplete. SIGKILL may leave orphaned descendants. Inspect a
stale run before repeating commands with non-idempotent effects.

## Adapters and limits

[adapters/quality.py](adapters/quality.py) is a protocol-1 agent-neutral shim:

```sh
python3 -I -S "$TOOLKIT/adapters/quality.py" \
  --launcher "$TOOLKIT/quality_launch.py" --python /path/to/approved/python3 \
  doctor --repo "$TARGET" --base "$BASE" --head "$HEAD" --identity "$IDENTITY" \
  --cache "$CACHE" --state "$STATE"
```

It delegates policy/verdicts and accepted-base pin selection to shared code and
cannot override the `check` artifact. The separate [command/context candidate](docs/command-adapters.md)
adds shared skill templates, offline explicit context and optional authorized
read-only GitHub metadata. Templates are shipped, not installed/registered;
documented local entry spellings are `/quality` and `$cmd-quality`, with no promised
underscore alias. Automated live review, enforced untrusted execution, release
publication and consumer rollout remain later work. There is no `quality
design` command. Every stronger local review route must be represented; one generic
attestation cannot replace multiple required reviews. See the
[implementation decision](docs/decisions/0001-minimal-runner.md).

Newly authored material is available under the [MIT license](LICENSE).

## Import-only candidate 0.2

The separate [external gate candidate](docs/external-import-v02.md) implements
schema2 validation of one already-known committed target and externally supplied
canonical-gate/controller evidence. It never runs that gate. Engine `0.2.2`,
policy `0.1` and protocol2 require their own accepted pins; v1 inputs are rejected.
The reviewed source is integrated; it has no release or consumer installation. The
[source integration update](docs/reviews/approved-path-fix-v01.md#source-integration-update-2026-11-02)
records the operation and distinct artifact build sources. Source integration and
local artifact qualification are separate gates.
Synthetic qualification does not establish a real producer, controller or adoption.

```sh
python3 -I -S tools/test_external.py
# Requires a clean reviewed source commit; output must not already exist.
python3 -I -S tools/build_external.py --output dist/software-quality-external-0.2.2-root-alias.pyz
python3 -I -S tools/test_external.py --artifact dist/software-quality-external-0.2.2-root-alias.pyz
```

The [owned real-executed fixture qualification](docs/reviews/external-fixture-qualification-v01.md)
now records one harmless invented gate: natural pass/failure, real timeout and
controller interruption, with measured consumption, supervision and cleanup through
the unchanged frozen 0.2 artifact. Timeout/interruption remain incomplete. This
qualifies the narrow fixture route; consumer security, dependencies, live reviewers
and adoption remain unqualified. Reproduction requires the documented exact-source
review/approval procedure and a disposable outside-target root.
