# Approved path traversal before canonical selection

Status: independently critiqued correction and cleared selector inventory before
implementation, 2026-11-02.
Baseline is `bbf912839741f8d52cdde7c862b19df3ac5accf5`. Main remains at
`e543e1a9a27d44e3ec04e862dfb184858985e260`; both earlier exact integration
operations are cancelled. This work proposes new source and local candidates only.

## Problem and observable acceptance

An owner can approve a literal outside-tool path that traverses a target-controlled
symlink. Existing helpers normalize parents or inspect only fully resolved ancestor
endpoints, losing the protected intermediate hop. A head-only link change can
select a different outside interpreter, launcher, metadata client or authentication
root behind the unchanged input. Inspection-only metadata can therefore use an
unapproved client with the approved authentication route, before artifact pins help.

Reject any protected directory/object encountered while following an approved path,
including an intermediate symlink target that later exits the protected root. Check
both the confirmed parent-component example and the equivalent no-parent chain.
Preserve safe system aliases and caller-relative paths that never enter a protected
root. Missing required tools/directories, loops, excessive expansion, unreadable or
unsupported paths return incomplete before helper/auth use. Return and consume the
validated canonical object. Keep normal 0/1/2, known failure priority, ownership,
protocol/pin/closure and caller-directory behavior from decision 0006.

## Selector and preprocessing inventory

| Entry / role | Inputs or defaults | Existing preprocessing and planned responsibility |
| --- | --- | --- |
| Context frontend interpreter | explicit `--python` | `approved_path` currently calls endpoint helper; validate raw caller-relative path with shared walker before launch, require existing executable |
| Context frontend launcher | explicit `--launcher` | `outside_target` currently loses parent evidence; validate raw spelling, require existing file, pass canonical result |
| Metadata client | explicit `--github-cli`, no implicit fallback | same executable helper before owned spawn; every before/after observation revalidates input |
| Metadata authentication | explicit `--github-config`, no inherited token discovery | same helper for directory before constructing GH_CONFIG_DIR; use empty invented auth roots in tests |
| Simple shim | explicit Python/launcher; remainder includes repo | currently strict-resolves approved paths too early; recover one unambiguous explicit repo input before any tool normalization, use shared walker, preserve original caller directory and forward policy args unchanged; refuse unsupported/ambiguous repo syntax before launch |
| External thin shim | fixed adjacent bootstrap, same-process runpy | current root resolution can erase entry spelling; validate raw script/bootstrap/resource paths against explicit repo before runpy where protection is possible; no extra relay or policy engine |
| Both bootstraps | already invoked trusted bootstrap/support code; child default current Python, accepted-base digest-named cached package | user must approve initial interpreter/module loading before this code runs; validate raw reachable child-interpreter/bootstrap/package paths against selected repo before subsequent effects and consume canonical returns |
| Bootstrap install | explicit archive and cache, no target argument | validate stable path traversal without protected subject roots; preserve private exclusive cache rules and actual archive pin validation; this does not infer a consumer authorization |
| Bootstrap state/cache/review | explicit paths | preserve raw spelling until protected-root validation; keep existing root separation; pass canonical validated results instead of pre-resolving away evidence |
| Direct core CLI / runner | current archive/interpreter, explicit state and review | validate paths against repo and existing tool/state/cache separation before reads/writes/children; reviewer digest still required; keep first validated failure recovery unchanged |
| Direct external CLI/store | current archive, explicit state, producer/observer files | replace existing shared primitive; retain raw spelling until check and use returned canonical input; preserve final-symlink restrictions, approvals, locks and immutable request binding |
| Owned-process capability probe | current Python default before helper/target | select canonical interpreter with same walker and caller's protected roots before the benign probe; retain WNOWAIT/SIGCHLD ownership design; generic target argv remains separately owner-authorized execution, not an approved bootstrap selector |
| Git inspection executable | fixed SAFE_PATH lookup | validate selected executable against repo before first Git call; no inherited PATH or auth search |
| Platform clock helper | fixed `/usr/sbin/sysctl` on Darwin; kernel boot-id file on Linux | fixed host installation precondition, no caller override; thread selected repo protection to clock helper validation when invoked by external CLI, retain source-only clock injection APIs |
| Builders/test harness | current approved interpreter; fixed Git and owned source/output paths | trusted maintainer entry, not consumer dispatch; shared Git change applies; no new dependency/provider or unknown target execution |
| Historical real fixture | exact approved harness/root/frozen bootstrap/ZIP and literal owned role commands | preserve historical bytes and manual owner approval boundary; do not rerun expired receipts or treat frozen0.2.0 as a new candidate; no new default-tool claim |

Repo selection establishes the subject root; it does not select a trusted executable.
Initial interpreter/entry/support loading necessarily precedes in-process checks and
continues to require an already approved complete outside-target installation.
This correction cannot retroactively protect an unapproved Python startup or import.
Target check commands are distinct, explicitly authorized consumer execution with
existing trust/containment gates; no new target execution authority is introduced.

## Smallest alternative and one shared mechanism

Leaving affected routes held is the smaller safe alternative; it does not provide
a corrected candidate. Refusing only raw parents is insufficient because no-parent
symlink chains can hide an intermediate protected root. Do not copy path engines
into adapters or assume current outside_path already enforces the required property.

Implement one owned component walker in quality_trust, used by outside_path and
all selector callers. Establish protected roots from the explicit subject/tool
roots, then walk the raw absolute input or raw caller cwd plus relative components.
Before inspecting/following each component, reject lexical entry into a protected
root. For a symlink, read its target and expand that target's components into the
pending walk (absolute resets to filesystem root; relative uses the resolved parent).
Check every intermediate target component before following another hop. Process
parent steps only after the current component has been checked; never use abspath
or Path.resolve on an unvalidated selector. Check the final path too. A single
bounded algorithm also canonicalizes protected-root aliases without a protected
set; do not introduce a second endpoint-only resolver.

Use lstat/readlink so each observed hop is explicit. Bound symlink expansion (40)
and total component work; refuse cycles/depth/unreadable/non-directory ambiguity.
Support nonexisting trailing state/cache paths only for callers that permit creation;
required executables/files/directories remain strict. Caller-relative parent paths
may be supported by the checked walk; if critique selects a stricter bounded refusal,
document it and preserve safe controls with an explicit compatibility disposition.
Safe /var-style and interpreter installation aliases remain supported when no hop
enters a protected root. This is stable owner-filesystem inspection, not a race-free
file-descriptor capability or defense against concurrent hostile filesystem mutation.
No signature, permission, kernel containment or universal trust proof is added.

The thin shim must not duplicate launcher policy parsing. It may extract one explicit
unambiguous `--repo` value (`--repo VALUE` or `--repo=VALUE`) solely to establish a
protected root, refusing duplicates/abbreviations/ambiguity before tool launch;
bootstrap remains authoritative for the rest of protocol, configuration and pins.
Review this boundary explicitly before implementation.

## Effects, compatibility, failures and version closure

Effects are lstat/readlink/existence checks on owner-supplied paths, existing Git
inspection and already authorized owned helper/check invocations. No new source,
private input, account, auth probe, network service or external write is introduced.
Unsafe selector refusal occurs before marker-only helper execution or authentication
use. Canonical returns are passed through child argv/environment; path changes after
selection outside the stable-filesystem assumption are not claimed prevented.
Errors remain incomplete/2 unless the same validated invocation already knows a
required failure; B1/B2 recovery and bounded diagnostics stay binding.

Shared trust bytes and both bootstraps/runtime call sites will change. New identities
are core0.1.2, external0.2.2 and adapter0.1.2, policy0.1 and schema/protocol structures
1/2 unchanged. New clean runtime source R builds distinct ignored versioned core and
external archives; every payload/manifest/source/bootstrap identity needs new review
and affected qualification. After the actual core digest is known, adapter metadata
records R/digest in later adapter source A, whose distinct bundle is qualified. Never
embed an archive digest into its own source or relabel earlier S/S3 artifacts.
Original three archives, held720, core7ea70/externalcb492/adapter43435, bootstrap
objects and previous work refs remain untouched. Old pins/state are never migrated.
No main update, consumer operation, release/tag or hosted artifact publication occurs.

## Test and review plan

Before code: independent design critique, inventory completeness and dispositions.
Before integration proposal: adversarial source/fix review, all valid blockers fixed
and re-reviewed, then final aggregate advertised-caller/closure/publication review
against previously accepted rules. Preserve historical deviations and mixed evidence.

Owned inert filesystem helpers first reproduce/refute both unchanged-literal chains,
with and without parents. Pure path tests cover protected final/intermediate roots,
symlink target parents, multihop/relative/absolute aliases, safe system-style aliases,
caller-relative controls, cycles/depth, missing objects and canonical return use.
No real tools/authentication are used. Negative source AND actual corrected bundle
cases cover every explicit/default selector and both shims; marker-only invented
helper code must not execute, and invented empty auth roots must not be consumed.
Package/default/bootstrap/input-root checks exercise the shared runtime primitive.
Selected affected ownership, known-failure finalization, cancellation, relative,
protocol/pin and resource-closure cases remain satisfied. State precisely which
fault helpers run source and which CLI paths exercise actual archives/bundles.
No unrelated historical reruns, expired fixture receipts or inflated pass counts.

Record exact source/trees, payload/archive/bootstrap hashes, deterministic repeats,
observed results/platform limits, failures/rechecks and preserved identities. Return
one new exact main proposal only after all gates clear; the cancelled bbf operation
cannot be reopened or silently substituted.

## Critique dispositions before implementation

Independent design critique accepted the one-walker architecture and R/runtime-digest/
adapter-A patch sequence subject to the following reconciled requirements. A separate
inventory audit identified the same boundary details. Neither review executed code,
imported modules, edited files or wrote Git metadata. The pre-code inert reproduction
confirmed that BOTH old helpers accept the no-parent hidden chain, selecting different
outside objects after only a subject-link change; raw-parent refusal alone is not a fix.

### Per-role protection and terminal-link policy

This is a caller matrix, not one global forbidden-root set. Initial approved resources
must legitimately live in their toolkit; cached code must legitimately live in cache;
ledger files must legitimately live under private state. Require existing regular
objects for tool/archive reads and directories for auth, retaining existing exclusive
write and final O_NOFOLLOW behavior where applicable.

| Validated role | Protected roots | Terminal symlink | Missing tail |
| --- | --- | --- | --- |
| Approved Python/launcher/Git/client/auth selectors | original subject repo | allowed only when every hop stays outside | forbidden |
| Bootstrap/support selected for later delegation | original subject repo | safe alias allowed, initial load still precondition | forbidden |
| Current/cached runtime archive | original subject repo | refused before canonical return, preserving regular-byte rules | forbidden |
| Install archive | none: explicit subjectless installer | refused | forbidden |
| Install cache | current approved toolkit; no subject is inferred | retain respective v1/v2 cache policy | new directory tail allowed |
| V1 run cache | original repo and approved toolkit; preserve state separation | safe alias only as previously supported | permitted only where creation already permitted |
| V2 run cache | original repo and approved toolkit; preserve state separation | refused as existing cache interface requires | same creation policy |
| V1 state | original repo and tool/cache separation | safe alias only as previously supported | directory tail allowed |
| V2 state | original repo, toolkit and cache | refused before canonical forwarding | directory tail allowed |
| V1 review input | original repo and toolkit | refused before canonical forwarding | forbidden |
| V2 producer/observer inputs | original repo, package/cache and state | refused before canonical forwarding | forbidden |
| Authoritative ledger and temporary output | inside validated state, not forbidden from its own root | preserve internal final O_NOFOLLOW/exclusive/private checks | existing creation rules only |
| Owned-probe interpreter | original subject AND snapshot when applicable | safe aliases outside protected roots | forbidden |
| Default host clock executable/boot file | original subject | executable alias may be safe; boot file retains final no-follow | forbidden |

The walker has an explicit terminal-symlink policy applied when the final supplied
component is first observed, before consuming a canonical result. Do not canonicalize
then ask whether the original input was a link. Metadata client/auth validation both
finish before any owned helper starts; no authentication data is probed to validate it.

Absolute paths start at filesystem root. Relative paths use the separately captured
caller directory and process its components through the same walk; they are never
made absolute using abspath first. A relative selector starting inside the subject
is refused even if parents would subsequently exit it. Absolute safe outside inputs
remain usable when the operator runs the approved command from the subject. Safe
relative controls from an outside caller directory continue to work. This deliberate
boundary is documented, rather than silently treating protected cwd as trusted.

The walker processes parent components without erasing previously inspected hops.
An existing non-directory with pending components (including parent) is refused.
After a missing component, allow only a new normal trailing directory sequence for
creation callers; refuse parent re-entry or any strict-read request. Bounded symlink
expansion/work provides cycle refusal without falsely treating every repeated link
as a cycle: a finite path can revisit a link. Filesystem inspection assumes stable
owner-controlled namespace state; it is not a universal mount/hardlink identity proof
or a race-free execution/file-descriptor capability.

Thin-shim extraction accepts exactly one --repo VALUE or --repo=VALUE, refusing
mixed duplicates, --r/--re/--rep abbreviations, empty/malformed/option-looking values
and -- delimiter ambiguity. It returns both the canonical subject and an argv copy
whose sole repo value is replaced by that canonical subject; all other policy args
retain literal boundaries. No downstream parser can subsequently select a different
repo through an alternate spelling. Install exception is explicit and conservatively
recognized for the same-process external shim only; other no-repo forms refuse before
a subsequent selector is used. This is context extraction, not duplicated lock,
configuration, protocol or verdict policy. Disable outer-shim abbreviation as needed.

OwnedProcess requires protected roots at construction/start; empty roots are explicit
owned maintainer/install cases, never a silent consumer default. Every start validates
the default interpreter before a cached WNOWAIT capability may return. OS capability
proof can be cached; path approval is root-specific and cannot. Legacy execute receives
the original subject from runner in addition to snapshot, so materializing a snapshot
does not discard protection of the source checkout. Every consumer relay passes its
subject roots explicitly; fake OS tests explicitly designate their invented roots.

Default Git uses the checked raw SAFE_PATH result before its first invocation, without
fallback. Initial, issuance and final clock reads all carry original repo protection:
create gains an explicit subject/protected-root parameter; receive already has Git.repo.
Captured default callable arguments become explicit defaults resolved with those roots,
while owned source-test injection remains an internal callable, not a production clock
or code override. These additive internal interfaces do not change CLI protocols,
evidence schema structures, accepted policy obligations or consumer pin semantics.

Cache traversal through the approved toolkit is refused as required by the README's
outside-toolkit cache contract; this deliberately tightens earlier implementation
paths that allowed toolkit-contained caches. Install input archives may legitimately
live in the toolkit while the private output cache must not. No cache is inferred
from the target. This distinction is tested and documented; existing pins are not
silently migrated. State/cache overlap checks continue in both directions after
canonical path validation, rather than mistaking an allowed parent for separation.

After the dispositions above were recorded, the independent inventory reviewer
cleared the inventory for implementation: no further caller/authority conflict was
found. Walker correctness, independent source/fix review and actual candidate
qualification remain separate gates. The independent design critique accepted the
single-walker architecture and version/closure sequence with these recorded rules.

## Stable system aliases discovered during final qualification

After the first R/A candidates passed their selected checks, final owned namespace
inspection found a supported-platform alias not represented by a symlink: on this
Darwin host, two spellings of the same owned checkout/root have equal device/inode
identity and distinct resolved strings. An inert ignored fixture confirmed the
lexical-only walker could traverse that alternate subject spelling, then a head-
controlled link, and accept an outside object. No real tool/authentication or consumer
was used. The first R/A archives stay unchanged and held; passing counts did not
cover this alias and cannot waive it.

Independent design critique accepted a bounded correction inside the SAME walker:
for existing protected roots, record observed (device,inode) identity. In addition
to lexical prefix protection, reject a traversed existing component whose lstat
identity equals such a root, before following another hop or leaving through a
parent. Missing future cache/state roots keep lexical protection without invented
identity evidence. This inspects only the supplied paths/roots; it introduces no
mount-table enumeration, permission/signature proof or hostile-mount capability.
The universal-filesystem limitation does not waive this confirmed stable system
alias. Initial approved loading and stable-owner-namespace assumptions remain.

Add portable injected-identity and real owned platform-alias negative controls for
parent/no-parent paths and selector execution/auth use. Preserve safe /var aliases,
canonical-client/auth and caller-relative controls. Independently review and qualify
this affected shared primitive/caller closure again from a new exact runtime source
R2 and adapter source A2. Patch identities stay the authorized unreleased0.1.2/0.2.2/
0.1.2, but new filenames include `-root-alias`; no earlier local archive is overwritten
or relabeled. Rebind adapter metadata only after the new core's actual qualification,
then return a new exact source proposal after aggregate review. Main is unchanged.

## Alias-consistent separation and lock identity

Independent review identified two related existing contracts that also need the
verified stable-root aliases, before replacement source freezes. Reverse separation
cannot compare canonical strings: state under one spelling may physically contain
cache/toolkit under another. Reuse the SAME protected walker in within() and the
external bidirectional overlap predicate. Catch only protected-root rejection as
membership; propagate other inspection failures honestly. This introduces no second
path engine or weaker separation rule. Add injected identity and real owned alias
ancestor/sibling controls for state/cache, toolkit/cache and target/cache.

Existing advisory locks hash path spelling. Equivalent target/state spellings can
therefore create different lock files; imports from distinct physical clones sharing
one physical plan could both read a baseline and overwrite a retained failure. Use
stable observed directory object identity for the shared lock key, holding an opened
non-follow directory descriptor during the lock lifetime. This is private advisory
coordination, not target execution/permission or universal namespace containment.
Keep the legacy spelling lock too, in a fixed object-lock-then-spelling-lock order,
to preserve coordination with earlier same-spelling operations; the held old alias
routes are not newly qualified. Do not delete/migrate old lock/state files or transfer
old pin approvals. Device/inode metadata is local and never becomes a public subject
identity or signature. No protocol/schema/policy field changes are introduced.

Plan identifiers must be validated as the existing bounded hex identifier BEFORE
any path lookup/open for a lock object. Reuse the private existing-plan-directory
validation before locking and loading; reject missing/symlink/nonprivate plans. Test
malformed IDs cause no lookup, equivalent target-root locks collide, and two distinct
clones' inner plan locks collide across state aliases. Use owned directories and
nested nonblocking lock attempts or benign owned multiprocessing, no real consumer
or private auth. Failure priority/atomic ledger rules remain unchanged; actual mixed
old unsafe aliases are not claimed compatible. Independently critique this lock
amendment before implementation, then re-review source/tests and requalify R2/A2.

Independent lock/separation design critique accepted the direction with four
requirements, recorded before this implementation: membership catches ONLY the
exact protected-root diagnostic and propagates all other errors, using already
validated operands; hold the no-follow directory identity FD and BOTH lock FDs for
the entire critical section/recovery and close every partial acquisition on error;
use a distinct object-lock filename namespace, never unlink locks, and require
opened locks to be regular/private with nonblocking special-file refusal; validate
plan IDs before any identifier-derived lookup/lock, without claiming unrelated
approved CLI context work did not occur. Existing same-owner/private-state and
stable-filesystem assumptions remain explicit. Add a second-lock contention release
case and known-failure retention after alias contention. No structural blocker was
found once these details were recorded; source/fix and actual-byte gates remain.
