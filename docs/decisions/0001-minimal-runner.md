# Minimal runner and pilot contract

Status: proposed implementation choices, 2026-11-02. Governed by the bootstrap
AGENTS.md and toolkit design at `c2cd0500e9a4c4d2beb8b28f3fcc67a4d947c585`.
This decision is not consumer adoption or release publication.

The user needs repeatable quality evidence across personal repositories without
copying policy or trusting a change to choose its own reviewer. The smallest
alternative is a documented manual gate. Keep that available: this runner
automates identity, command orchestration and evidence validation, while an
operator still supplies independent review through an explicit protocol.

## Choices and responsibilities

- Python 3.11+ and its standard library; no runtime or build dependencies. Use
  typed modules, immutable data records and strict JSON boundaries. One owned
  validator handles the small published schema vocabulary; it is not a general
  JSON Schema implementation. Schemas describe configuration, lock, review and
  evidence. No dependency installation during checks.
  The first backend supports POSIX macOS/Linux only, using process groups and
  advisory file locks. Invoke both trusted launcher and artifact with a trusted
  interpreter using `-I -S`; require isolated startup before parsing arguments.
- A deterministic Python ZIP application containing code, policy and schemas, built from
  an identified clean Git revision. An externally trusted launcher verifies an
  operator-approved SHA-256 before installing or executing. Cache the regular
  ZIP file without extraction, verify its identity before every execution, and
  refuse mutable aliases or mismatches. A source-checkout run is experimental
  and cannot provide release-qualified pass evidence.
  The artifact does not establish its own publisher trust. Installation is an
  explicit local operation; no downloader, release publisher or automatic update.
- Inspection uses Git with hooks, external diff/text conversion and inherited
  Git environment disabled. Also disable fsmonitor, replacement objects, lazy
  fetching, pagers and optional writes; ignore system/global Git configuration.
  Resolve full base/head commit and tree identities;
  load config/lock only from the accepted base. Require full object IDs at the
  public interface. A repository identity in the accepted config must match the
  operator's expected identity. This does not authenticate the remote publisher.
- The runner accepts an explicit base/head; PR discovery is deferred to thin
  adapters. A pinned adapter calls the trusted launcher, never target code, and
  cannot replace the accepted artifact or policy. Initial adoption explicitly
  approves base config/lock and launcher through the repository owner's route.
- Default provenance is untrusted and no containment backend is implemented.
  Inspection and recorded review remain possible; required execution is
  incomplete. Trusted-local execution requires both accepted-base permission
  and explicit operator authorization for this invocation. It uses a disposable
  Git export, fresh HOME/TMP/cache roots and an allowlisted environment with no
  inherited credentials. It is not a sandbox: a trusted command has host access.
  No submodules, LFS hydration, package downloads, hooks or target launchers.
  Export raw tree/blob entries, without archive attribute transformations; refuse
  symlinks and gitlinks. Fresh roots do not isolate platform credential stores.
  A required accepted check isolation wrapper must cover its actual data stores
  and effects; insufficient declared capability leaves execution incomplete.
- Checks are argv arrays, never shell fragments; a shell may be named explicitly
  only as part of an accepted trusted command. Record their declared effects,
  bounded timeouts/log sizes and exit status; keep raw output private in the run directory.
  A zero exit is successful command evidence, not product correctness proof.
- The only first reviewer interface is `recorded-v1`: an independent human or
  agent supplies a strict JSON attestation bound to repo/base/head/trees,
  effective configuration digest, reviewer identity, policy and artifact.
  Accepted config declares reviewer identity, required read-only boundary and
  authorized source disclosure. Operator passes the outside-target response and
  expected digest explicitly. No reviewer process, provider, media viewer or
  source upload is launched. The attestation records actual permissions and
  disclosure; mismatched, absent or unenforced boundaries are incomplete.
  This is a trusted external attestation protocol, not cryptographic proof of
  independence or permission enforcement. Do not accept head-supplied responses.
  Two-step workflow: generate the effective plan/context, commission the review,
  then pass the response and independently approved digest. Read/hash/parse the
  same bytes, with bounded input size.
- One integrator owns source and integration. Independent native reviewers may
  inspect newly authored public toolkit files under this session's existing
  authority; they must not access private inputs or execute target code. No
  separate provider CLI or hosted fallback is added. Code review is evaluated
  against the bootstrap rules, not new rules introduced by this implementation.

## Effects, recovery and evidence

Only explicit install writes a new cache entry. Check/doctor write unique local
run directories outside target/tool installations. Checks write within their
disposable export by convention; trusted-local mode cannot enforce that limit.
The orchestrator makes no target checkout changes, network calls, external posts,
commits, pushes, merges, deployments, automatic fixes or telemetry. Trusted checks
retain host access and can cause their owner-declared effects; disposable roots
are a convention rather than enforced containment. Maintainer
Git commits/pushes are separate from runner execution and release publication.

Each run atomically writes an initial incomplete report before executing and a
final validated report after execution. Interrupted or killed runs retain an
incomplete report; handled command timeout/cancellation must stop the owned process
group. Hold a per-target lock and never overwrite another run or clean up its
files. Locks coordinate a single state root; operators must share that root for
one target. SIGKILL can leave child processes; no guaranteed cleanup is claimed
after uncatchable termination. Report invalid input safely without echoing
credentials or private source.

Evidence includes exact source/artifact/schema/policy identities, accepted base
config and lock digests, source status before/after, inspection summary, command
results and review findings. Dirty or changing checkout makes required evidence
incomplete, even though checks inspect an exported immutable commit. Required
failure or a validated open blocker wins over incomplete; only all required
stages passing yields pass. Unknown fields, duplicate JSON keys and invalid
identities fail validation; missing capability/evidence remains incomplete.

## Observable acceptance and tests

Invented fixture repositories and recorded reviews must demonstrate:

1. Clean accepted pins, immutable targets, strict config and complete checks plus
   an authorized independent attestation can pass, with unique validated reports.
2. Head-side config/lock/launcher changes never choose policy or execution; a
   changed script behind an unchanged accepted command is never run without
   explicit trusted-local authorization.
3. Missing containment/reviewer/authorization, invalid review, dirty or moving
   source, timeout and interruption stay incomplete. Required command failure
   and valid open blocker take precedence over other missing evidence.
4. Pin/schema/source mismatch, archive traversal and modified installed code are
   refused before executing package code. The artifact works offline and its
   packaged tests exercise the same code as source tests.
5. Inherited secrets are absent from command environments, report output is
   private, Git configuration cannot run target code during inspection, and
   adapters cannot substitute head-side pins. No live account or paid model.

Run standard-library unittest tests with invented disposable roots; validate
documentation links, status claims, staged content and metadata manually.
Independently review code, fix blockers, re-review affected fixes, then bind the
recorded checks and review to the final source tree. Artifact smoke tests and
installation evidence are separate from source review and live-review accuracy.

## Pilot handoff and limits

The candidate contract is one installed artifact/approved digest, one accepted
base configuration and lock, explicit base/head, local report, trusted-local
permission if appropriate, and an externally obtained independent attestation.
Stronger consumer gates remain separate required checks. An established product
and a lightweight experiment will receive separate adoption assignments; no
consumer is accessed or modified by implementation work. PR lookup, live reviewer
automation, untrusted execution, artifact publication and consumer rollout are
deferred. A source or artifact candidate is not a recommended released version.

## Independent critique

The separate read-only native reviewer `design_critique` assessed this document
against the accepted bootstrap rules before implementation. No target code or
private files were executed/read by the reviewer. All four required corrections
were accepted: disable Git fsmonitor/replacement/lazy-fetch routes; export exact
raw blobs and refuse symlinks/gitlinks; separate orchestration effects from host
access retained by trusted checks; require isolated Python startup for launcher
and application. Corresponding invented-marker and snapshot tests are required.

The reviewer preferred direct ZIP execution over extraction. Recommendations
accepted: POSIX-only initial support, bounded output, honest SIGKILL limits,
explicit two-step review workflow and same-byte review validation. These are
implementation obligations, not evidence that they work yet.
