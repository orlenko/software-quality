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
