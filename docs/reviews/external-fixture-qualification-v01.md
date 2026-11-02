# Real-executed fixture qualification

Status: bounded qualification completed, 2026-11-02. Four real executions and
honest imports through the unchanged frozen artifact are recorded below. This record will distinguish
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
artifact/bootstrap identities in decision 0005 for this one disposable qualification.
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
an unmeasured mechanical control. Runtime results were not presumed by this prior approval.

## First actual attempt and superseding approval

Source `89c3c99279edfe309ec22ab804454d254eaaad3c` was approved and invoked only
after review. Setup created one owned subject/four commits. The first pass input
actually completed all parse/sum/compare stages and naturally exited 0. Qualification
stopped: Darwin returned EPERM for an unnecessary signal to the already-exited
producer group, so no controller receipt was produced. The actual full environment
also contained an OS-added CF encoding variable; its unexpected fingerprint correctly
left consumed establishment false. This was not a passing qualification/import.
Raw first-attempt evidence is retained ignored. Operator metadata also recorded
PATH directory order differently from the actual initial outer launch (the same
two system directories); that deviation is retained, and fresh launch records
match the exact provided environment. Read-only post-failure probes found
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
consumer/workload. Fresh runtime results follow below.

## Actual qualification and cleanup

Corrected source `c870a04eedd4b749aeb2e627235032bc17a9b49d`, tree
`e52e8c96d10cab99f6187777e1fbdff9d68ba97e`, ran from copied approved bytes
on macOS/Darwin 27.2.0 and Python 3.14.7. Before setup, the owner retained exact
source/hash/profile/argv/environment approval and invocation records. Setup's four
commits were inspected for exact reviewed gate, invented inputs, registry and
frozen pins; exact-head approvals preceded each gate invocation. Each case used
its own actual issued challenge. Producer and controller bytes were inspected and
separately approved by digest before their imports. No failed receipt/challenge
was reused or observation time altered.

| Case | Actual gate result | Producer span | Completed coverage | Frozen import at recorded time |
| --- | --- | --- | --- | --- |
| pass | natural exit 0 | 288 ms | whole parse/sum/compare | pass, exit 0 |
| fail | natural exit 7 | 285 ms | whole parse/sum/compare | fail, exit 1 |
| timeout | terminated by SIGTERM (-15) | 3111 ms | parse only | incomplete, exit 2 |
| controller interruption | parent driver SIGINT; gate SIGTERM (-15) | 300 ms | parse only | incomplete, exit 2 |

These spans include producer inspection/attribution, not just gate computation.
For timeout, the actual group SIGTERM occurred 5 ms after the scheduled 3-second
monotonic deadline; producer completion and cleanup followed later. The frozen
report correctly kept natural-result, coverage, budget and deadline-observation
incomplete. All real timestamps remain as measured. The controller observation
means active measured finite process supervision, not a hard real-time OS limit.
For interruption, the owner-approved direct-parent driver observed parsed intake
and sent a real SIGINT; the controller handled it and terminated its owned group.
The report kept natural-result and coverage incomplete. Neither terminated case
was relabeled as a natural nonzero failure or whole completed gate.

Actual gate intake hashes matched captured committed code/input and the declared
runtime/environment in all four corrected cases. Logical compiled origin matched
the captured Git H; no first-party filesystem import or dependency provenance is
inferred. Controller raw observations retained prelaunch arming, actual PGID,
50/50/434/36 supervision checks, signal events, real gate/producer/controller waits
and empty-group observations. Read-only final probes found every recorded owned
controller/producer/gate PID and group absent. All four cleanup observations were
complete; no outstanding owned child or cleanup block remains. Initial failed-run
PIDs/groups were also absent. Disposable raw evidence is retained for inspection,
not deleted or committed.

[Selected measured facts and exact file-digest references](../cases/external-fixture-observed-v01.json)
identify each local invented head/tree, wall-clock boundaries, counts, producer/
controller receipts, raw observations, intake, waits, logs, owner approvals,
invocations and frozen import outputs. Paths in that manifest are generic names
relative to each ignored case directory; raw contents, absolute private paths,
account details, environment values and captured transcripts are not published.
The owner retains the actual ignored roots and exact argv. The evidence is an
owner-attested experiment, not a public cryptographic authentication service.

Frozen source/payload/bootstrap hashes were rechecked unchanged, including ZIP
`958a5261f752e523eec74a75ffa3719b1536f966a67db3a482d5e5bd6e9b1cd4`.
No core/schema/adapter/policy edit was needed, and no frozen-importer representation
block occurred for these cases. Earlier source branches/artifact bytes remain
unchanged. No unaffected old suite was rerun for counts. These are historical import verdicts;
positive evidence expires or becomes incomplete after source/context movement.
Approval-before-invocation order, exact source/profile continuity, relative links,
selected public facts and staged publication content/metadata were manually checked.

## Reproduction boundary

This is a manually approved fixture, not an automatic test entry or generic runner.
Create a new owned private root outside toolkit/subject, copy the exact reviewed
harness/gate/profile plus frozen bootstrap pair/ZIP, and check all stated digests.
Record exact clear-environment commands before using the approved `prepare` role.
Inspect/approve the resulting four heads before any `run --case CASE`. Run/import
each case within its 60-second window, inspecting and independently approving actual
producer/controller receipt digests first. Use the frozen protocol 2 import command
from [usage](../external-import-v02.md), with the actual issued plan/context and
approved identities. Retain exact argv, raw evidence and cleanup observations in
that owned ignored root. A source fix requires review and new approval before
execution; a lost challenge or aged positive receipt cannot be repaired by restamping.

## Limits

This is one newly authored invented Git subject and one tiny canonical gate with
four case commits. It cannot qualify consumer dependencies, private/privacy,
product checks, live reviewers, hostile producers or enforced filesystem/network/
read-only/independence boundaries. Only deadline/cleanup process supervision is
registered. Any absent/unprovable required fact remains incomplete. Source main,
old adapter/design branches, policy and frozen source/artifact/pin remain unchanged;
no consumer adoption, release or hosted artifact publication follows.
