# Real-executed fixture qualification

Status: one approved real attempt exposed two fixture issues; corrected source
has passed independent static fix review and awaits fresh execution. This record will distinguish
actual measurements from expected reference identities and procedural restrictions.
The [design](../decisions/0005-real-executed-fixture.md) records scope, smaller
alternative, responsibilities, writes, mechanisms, clocks and failure behavior.

## Design critique

Independent inspection accepted the serialized-input mechanism and direct-parent
SIGINT driver. Accepted conditions: actual parsed intake precedes deliberate
blocking; captured bytes and completed stages remain distinct; logical compiled
Git origin does not prove installed-module provenance; retain unreaped leaders
through final possible signals; establish actual gate/producer/controller waits
and group cleanup; never alter late or missing facts to satisfy frozen validation;
shared-owner roles do not establish OS independence. No new execution was used
for this critique.

## Static source review and response

Independent adversarial static review/fix re-review found no remaining blocker
or deferred finding in staged tree `b3fd1fdc0fa217747f8c94cb429b8ebf8d0f7586`.
Pre-execution fixes include exception-safe driver/producer/controller lifetimes,
cancellation before gate launch and explicit incomplete root cancellation,
non-reaping capability checks, actual arming/PGID/check/action observations behind
deadline claims, and atomic readiness publication. New review executed/imported
no code and made no Git writes. Later documentation does not alter these bytes.

| Reviewed input | SHA256 |
| --- | --- |
| Harness | `382df952786d195a567ffe08c0e3fe235aee8cbfef410e73c541572e4f7f9a72` |
| Gate | `c00524e97c23df35156ff9acc0abad0ac5bf82cc648f9316b31bed6a09f83ca9` |
| Profile file | `7b1cf42db4a3cbadba7f180c0bc36ccbdac4540b018ed72db602b9ecb7840aaf` |

The [earlier import review](external-import-v02.md) retains its disclosed reviewer
`git write-tree` metadata write beyond the requested read-only mode. This new
review is instructed to use non-mutating source/object/hash/AST inspection; that
historical event is not an enforced reviewer-boundary witness.

## Owner approval and execution

Owner approval recorded before execution, 2026-11-02: as the delegated fixture
owner, I approve only the exact independently reviewed hashes above and the frozen
artifact/bootstrap identities in decision0005 for this one disposable qualification.
Approved command templates, executed from copied approved bytes:

- existing isolated Python `-I -S OWNED/harness/qualify_external_fixture.py prepare --root OWNED`;
- the same entry with `run --root OWNED --case CASE`, once each for pass/fail/timeout/interrupt;
- fixed frozen bootstrap install/doctor/import commands limited to the owned fixture;
- the reviewed literal child-role commands and owned PID/group signals specified
  in that harness, including direct-parent SIGINT after measured intake.

Initial environment is cleared and contains only PATH, LC_ALL and owned HOME/TMPDIR.
The harness explicitly constructs child environments and observes the actual gate
environment. Exact private argv/environment, immutable source/tree/profile identities
and invocation timestamps are retained in the ignored run root before execution.
No source/pin substitutions or extra commands are approved. Fixture-head trust
approval follows setup inspection and precedes any gate; separate producer/controller
receipt approval follows actual measurement inspection and precedes import. Those
later approvals cannot be presumed from this source approval. Existing user scope
permits these effects without another confirmation. Approval cannot substitute for
an unmeasured mechanical control. Runtime results remain pending.

## First actual attempt and superseding approval

Source `89c3c99279edfe309ec22ab804454d254eaaad3c` was approved and invoked only
after review. Setup created one owned subject/four commits. The first pass input
actually completed all parse/sum/compare stages and naturally exited0. Qualification
stopped: Darwin returned EPERM for an unnecessary signal to the already-exited
producer group, so no controller receipt was produced. The actual full environment
also contained an OS-added CF encoding variable; its unexpected fingerprint correctly
left consumed establishment false. This was not a passing qualification/import.
Raw first-attempt evidence is retained ignored. Read-only post-failure probes found
the recorded controller, producer, gate and group absent; actual gate and controller
waits were recorded. No unknown process was signaled in cleanup.

Independent static fix review accepted two fixture-only corrections: signal only
while WNOWAIT reports the owned leader live, retaining unknown on permission/group
uncertainty; explicitly supply a synthetic CF encoding/country in the predeclared
environment and still compare the entire actual environment. No observed field is
dropped, no receipt is restamped, and no frozen tool is patched. The gate is unchanged.
The reviewer executed neither fix nor cleanup probes and made no writes.

Superseding exact-source owner approval, recorded before fresh execution:

| Input | SHA256 |
| --- | --- |
| Harness | `b86f0d91dd946c22d201c082a2adc7183c932bc0f7baea5bc10aeeb723269e1b` |
| Profile | `6b4f60af50716ca5e85d2ded3d1fc912aa5cc154dfef9e28c9e86c2c62a27370` |
| Gate | unchanged `c00524e97c23df35156ff9acc0abad0ac5bf82cc648f9316b31bed6a09f83ca9` |

As fixture owner I approve only these reviewed bytes with the same bounded commands,
fresh disposable subject/root, new exact-head approvals/challenges and independently
inspected producer/controller receipts. Initial failed evidence remains immutable.
This does not approve any core/schema/policy/adapter/version/pin change or additional
consumer/workload. New runtime results remain pending.

## Limits

This is one newly authored invented Git subject and one tiny canonical gate with
four case commits. It cannot qualify consumer dependencies, private/privacy,
product checks, live reviewers, hostile producers or enforced filesystem/network/
read-only/independence boundaries. Only deadline/cleanup process supervision is
registered. Any absent/unprovable required fact remains incomplete. Source main,
old adapter/design branches, policy and frozen source/artifact/pin remain unchanged;
no consumer adoption, release or hosted artifact publication follows.
