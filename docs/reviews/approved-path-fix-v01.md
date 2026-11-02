# Approved path traversal correction

This record covers new core0.1.2, external0.2.2 and adapter0.1.2 candidates. Policy
0.1, schema structures1/2 and protocols1/2 are unchanged. Main remains e543e1a;
previous exact source integrations are cancelled. No consumer or release is cleared.

[Decision 0007](../decisions/0007-approved-path-traversal.md) records the pre-code
selector inventory, effects, alternatives, failure/compatibility/version plan and
independent design critique. A separate independent inventory review required
per-role roots, terminal-symlink policy, conservative shim repo extraction,
per-start probe protection and rooted initial/issuance/final clocks. All requirements
were recorded before implementation; both gates cleared.

The old helpers were reproduced only on newly authored inert disposable paths.
Both accepted the no-parent hidden-hop chain, selecting different outside objects
behind the unchanged literal after only a subject-link change. The frontend also
accepted the parent form; the old shared helper's raw-parent refusal did not solve
the no-parent case. No tool, authentication, real account or credential was used.

## Source and fix review

One shared lstat/readlink component walker checks every protected hop before parent
normalization or another link can hide it. Canonical returns reach argv/environment
and readers. Required terminal-link refusal happens during the first walk, before
canonical forwarding. Relative selectors start at the captured caller directory;
starting inside the subject refuses. Safe aliases and finite repeated-link paths
are supported. Creation callers accept only a new normal tail after a missing
component. Work is bounded to 40 symlink expansions and 512 components. Ambiguous `//`
anchors, inaccessible strict objects and unsupported traversal refuse incomplete. This is
stable owner-namespace inspection, not a race-free filesystem or execution capability.

Independent adversarial source/fix review drove three further corrections: raw repo
roots use the same bounded walker; frontend cache/state checks include a separately
approved launcher's toolkit root; and the external shim checks its raw entry spelling
before deriving a later bootstrap. Initial already-loaded interpreter/support/entry
code remains an explicit approved-installation precondition. No retroactive load
protection is claimed. The shim extracts and canonically rewrites exactly one repo
argument; the bootstrap retains policy/pin authority. Original repo roots remain at
all child/probe lookups, even after snapshot creation or cached OS capability proof.
Initial, issuance and final clock defaults carry those roots too.

Two independent source/fix reviews found no remaining source blocker. Review was
read-only public-source and existing-record inspection, without module imports,
execution, edits or Git metadata writes. This is observed review behavior, not an
enforced reviewer sandbox. Earlier disclosed review deviations remain historical.

## Source diagnostic checks

All filesystem subjects, helpers, responses and auth roots are invented, owned and
disposable. Marker helpers use isolated Python; auth roots contain no credentials.
Negative tool/auth cases assert the marker did not run. Safe controls record the
actual client entry and canonical auth directory. No live provider or consumer ran.

- The first 11 path tests passed, but a 4096-component work cap made the oversized
  negative take about 67 seconds. Tightening the cap to512 retained all checks; the
  same oversized case passed in0.244 seconds. This measures the owned case, not a
  wall-time guarantee for all filesystems.
- The next 16 source checks passed, including frontend and simple-shim tool/auth
  parent/no-parent A/B cases and safe controls.
- A 27-case new-source selection passed after adding bootstrap/direct-core paths,
  external-shim delegation, unsafe-data failure retention and default-clock roots.
- The affected source selection passed65 tests:20 context,5 simple-shim,15 owned
  process/caller,12 runner,10 trust and3 review cases. These preserve the affected
  ownership/finalization, Git, relative, protocol/pin and closure behavior.
- The importer source suite passed49 cases. A subsequently added instrumented
  package clock-default case passed with three other refined/default controls in
  a four-case selection. The original-subject roots reach initial/issuance/final
  default clock reads, and known failure remains1 when final clock selection fails.
  The clock and core-default driver assertions were then strengthened to require
  the unsafe injected selection was actually reached and checked with subject
  roots; the two-case recheck passed.
- The legacy direct-path KeyboardInterrupt case was strengthened to assert the
  injected callback ran after an explicit repo was supplied; its recheck passed.

Selections overlap; counts are not summed. Source mode uses synthetic-source
fixture ZIPs and direct helpers. Instrumented drivers patch only the owned test
process, with no production code/clock override. Actual clean-commit archives and
adapter bundle remain separately pending; source checks do not qualify those bytes.
No expired real fixture or historical unaffected suite was rerun for renewed claims.

## Packaging and remaining gate

Shared trust and bootstrap/runtime bytes changed, requiring new runtime source R,
core0.1.2/external0.2.2 archives and explicit new bootstrap hashes. After actual core
qualification, later adapter source A records its exact R/digest and builds a distinct
adapter0.1.2 bundle. Generated inventories, source/member/archive hashes, repeats,
actual-package tests and final aggregate/publication review must bind those bytes.
Do not rebuild from a documentation head and transfer prior artifact approval.

The bundle distributes protocol1 frontend/simple-shim resources. The separate
protocol2 shim/bootstrap stays a source entry exercised with the actual external
archive; source-only marker bootstrap instrumentation is labeled separately. A
bundle test cannot be represented as executing a protocol2 member it does not ship.

All three original archives, held720, core7ea70/externalcb492/adapter43435, earlier
source/bootstrap objects and work refs remain preserved. No old pin/state migration,
main update, archive upload, release/tag, registration, consumer operation or service
change occurs here. Darwin/Python3.14.7 is the observed platform; Linux/Python3.11,
live providers/reviewers, hostile-code containment and consumer adoption remain
unqualified. A new exact source proposal follows only after the remaining gates.

## Initial runtime R actual-byte qualification (held)

Reviewed clean runtime source R is `6ab57e0d0f6dbc786d081ec85d34bdc7230b3503`, tree
`cde0338ea84f6fa3ccaf62c3b52a926228c27574`. The staged source/publication gate was
independently cleared before committing; reviewed blobs matched staged/working bytes.
Two builds of each new versioned local archive were byte-identical.

| Local archive | Version / schema | SHA-256 | Members |
| --- | --- | --- | --- |
| `dist/software-quality-0.1.2.pyz` | 0.1.2 / 1 | `baefa1331deae8cefcd4eb030887cf8a7a9425d2bac3eb37eb5823e3d3a0d33d` | 29 |
| `dist/software-quality-external-0.2.2.pyz` | 0.2.2 / 2 | `6c4082b2d663e7f71480e333482486bb82e06ad354c7a21b98d7866b27ffe934` | 20 |

Every inventory/member digest and committed payload blob was checked against R.
Generated entrypoints match their reviewed literal builders. Actual expanded-core
module origins/import closure, evidence aliases and patch identities were verified
in isolated Python, without dispatching a target gate. The separate external ZIP
retains exactly seven quality modules and seven external schemas, without core CLI,
process or runner modules. Shared trust contains generic helpers but adds no external
gate-dispatch entry.

The actual core selection passed88 checks on Darwin arm64/Python3.14.7. It includes
65 affected regression cases listed above,11 pure source walker/context tests and12
caller/default cases. Source-bootstrap and source frontend/shim tests use the actual
core archive; direct package/default tests import that archive. The copied protocol2
shim/marker-bootstrap experiment is source-only and makes no initial-load prevention
claim. Counts are mixed source-helper/actual-byte evidence, not88 package-only tests.
The independent reviewers inspected the source; they did not rerun these checks.

Adapter compatibility now records R and the actual observed core digest. Later
adapter source A contains that metadata, leaving both runtime archives unchanged.
The actual external selection also passed50 checks:36 established importer cases,
8 finalization cases and6 approved-path/default cases. Ordinary CLI routes use the
actual R archive; source store/clock injection helpers remain separately labeled.
Isolated package drivers import only the actual R archive and verify reached unsafe
clock selection before asserting refusal at initial, issuance and final phases.
The final known-failure invocation remains1. Parent/no-parent receipt/observer paths,
terminal-link refusal and immutable retained failure slots are exercised too.
Adapter-A build/qualification, final aggregate and publication checks remain pending
at this checkpoint.

## Stable root alias finding and reviewed correction

Final qualification inspection found a supported Darwin namespace alias that is
not a symbolic link: two spellings of the same owned root have equal device/inode
identity and distinct resolved strings. An owned inert fixture demonstrated that
the first lexical-only R walker missed that root before a subject-controlled link
selected an outside object. No tool/authentication or consumer was used. The actual
R88/external50 and adapter31 passes did not exercise this case and cannot clear it.

The initial adapter A is `48b6c9fb5b247d21f1d5bcfbe50b77b8786f5e0b`, tree
`2b7e7eb1b686a7f8564f504d53d858cddc3d9cc5`; its unchanged local bundle
`quality-adapters-0.1.2.zip` has digest
`cdeea80ed1b58852f1843b2efc3df08ba50a4dc18365c165a41a6b8876b39130`.
Its31 selected context/shim/marker checks passed, but it and the two R archives
above remain HELD. Their source identities/bytes and observed results stay historical.

The pre-code amendment `0402ef373d428eedd505c66997fecc6613339b9f` records independent
design acceptance of a bounded identity check inside the SAME walker. Existing
protected roots contribute observed device/inode identity; each existing component
is checked against those identities immediately after lstat and before another hop.
Future missing roots retain lexical protection without invented identity data.
This handles the verified stable root alias; it is not a universal mount/subtree,
permission, signing or race-free capability proof.

Independent source/fix review cleared the addition and its tests. The first14
root/walker/selector checks passed, including the real owned platform alias and an
injected identity safe/negative control. The marker matrix covers both forms and
A/B for every frontend tool/auth role and simple-shim selector. The external receipt
case refuses valid-looking natural7 bytes behind the same protected alias, leaving
original/failure slots empty. No unsafe helper or auth route executes. The expanded33-case new-source
selection passed, including all new alias cases and prior path/data/default controls.
Source review then identified the initial filesystem-root component as another
identity boundary: it and absolute-link resets now use one observed root stat.
The three-case RootIdentity recheck passed, including a portable alias-of-root
refusal and distinct safe control. The later code still requires new R2/A2 checks.

New exact runtime R2 and later adapter A2 use distinct `-root-alias` filenames with
the same authorized unreleased patch versions. Adapter compatibility is reset to
pending until R2's actual core is qualified. Nothing overwrites or relabels R/A or
earlier sources/archives. Actual R2/A2 qualification and final aggregate/publication
review remain pending at this checkpoint; no earlier cancelled main target revives.

## Alias-consistent separation and private locking

The same review found two related contracts still comparing path strings. Reverse
state/cache/toolkit/target separation now reuses the SAME protected walker in
within and external overlap checks, in both directions. Only exact protected-root
rejection becomes membership; unreadable/unsupported/budget errors propagate.

Existing private advisory locks also hashed spelling, so two clones could use
state aliases to take different plan locks and overwrite a retained failure.
Pre-code amendment `02bf885` records independent critique and closure requirements.
The correction keeps an opened no-follow directory descriptor and acquires a
separate object-identity lock, then the legacy spelling lock, throughout the critical
section/recovery. Partial failures close every descriptor; locks are never unlinked.
Lock objects must be regular/private/same-owner and nonblocking; malformed plan IDs
are rejected by the shared private-directory helper before identifier-derived lookup.
This preserves earlier same-spelling coordination without clearing old unsafe alias
routes or migrating any pin/state. It does not assert a hostile-filesystem capability.

The eight owned lock/separation tests passed, covering alias contention, safe sibling
control, legacy-second-lock contention release, noninheritable descriptor cleanup,
interrupted partial acquisition, nonregular/private lock refusal, and malformed IDs
before lookup. A twelve-case wiring selection found one inherited direct-core omission:
state could physically contain the runtime/cache root because the reverse check
was absent. Adding all bidirectional repo/tool/state checks fixed it; the focused
recheck passed. The other eleven cases passed, including actual CLI contention from
a second physical clone sharing an aliased plan: no record bytes changed while
blocked, and retained natural7 returned failure after release. These are fresh owned
fixtures, not old consumer/fixture executions or renewed receipts.

Independent source/fix review cleared the identity, separation and locking additions.
New exact R2/A2 artifacts and full affected checks remain pending; none of the earlier
R/A passes are transferred to these changed bytes.

The expanded46-case new-source selection passed after those fixes. A final safe
control exposed another string comparison: hardened Git can report the normal
spelling of a repository selected through its stable namespace alias. Git root
comparison now uses bidirectional same-walker membership, accepting the equivalent
root while refusing a nested directory. The two-case positive core/CLI and external
alias-doctor-to-normal-import control passed in1.488 seconds. Both independent
source/fix reviews cleared the resulting source; exact R2/A2 qualification remains
pending and earlier candidates stay held.
