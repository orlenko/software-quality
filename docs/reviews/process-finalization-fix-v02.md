# Process ownership and failure-finalization correction

This record covers new patch candidates core/adapter 0.1.1 and external 0.2.1.
Policy 0.1, schema structures 1/2 and adapter protocols 1/2 are unchanged. It does
not upgrade a consumer or replace earlier frozen artifacts. The older source
integration proposal was cancelled after independent review found two blockers;
main remains unchanged while the new work branch is qualified.

[Decision 0006](../decisions/0006-owned-process-finalization.md) records the user
problem, acceptance criteria, alternative, responsibilities, data effects,
failure behavior, test plan and independent design critique before implementation.

Independent adversarial source review covered the aggregate correction against
baseline `60a706165934b7730e04f76b928469de2f1b427e` and previously accepted rules.
Review found and drove fixes for premature child reaping, known failure loss across
finalization, recovery accidentally consuming unpublished positive receipts,
frontend formatting interruption, legacy pipe-close faults, bootstrap blocking
output, and interrupted fallback diagnostics. The corrected paths received
follow-up inspection. Review used native independent agents for source inspection;
no imports, target execution, edits, private source access or Git metadata writes
were performed by these current reviewers. This is an observed inspection-only
review, not a claim of a separately enforced reviewer sandbox. Historical review
boundary disclosures in earlier records remain unchanged.

The shared trust utility retains an unreaped owned identity through the last
signal. No uncertain or released identity authorizes a fallback signal. Actual
reaping and a separate read-only group observation establish cleanup; EPERM and
an attempted signal do not. A benign owned interpreter probe checks the required
capability before helper/target launch. Cancellation handlers record requests and
remain installed through cleanup and bounded output.

Import recovery binds immutable request identity before retaining knowledge of a
validated failure. It distinguishes remembered facts, atomic visibility and
confirmed durability. Recovery reconciles uncertain publication against the sealed
ledger, never rolls back a visible replacement, and never consumes an unpublished
positive receipt. Failed/partial output does not erase a known failure; without
validated knowledge the invocation remains incomplete.

## Source checks before artifact qualification

All data and executable fixtures were newly authored, owned and disposable. No
consumer gate, credentials, live metadata, provider or real PID reuse was used.
The first 14 new process/caller tests passed. The affected source selection then
ran 51 tests: one failed because a pre-existing lock diagnostic had been replaced
by a generic message; the bounded diagnostic was restored. The two-case affected
recheck passed. The importer source-mode selection ran 44 tests: one old assertion
expected a JSON report for a different immutable requested head. The corrected
contract refuses that request before binding, with exit 2, no JSON and unchanged
ledger. That assertion now checks all three. The three-case affected recheck passed,
including strengthened actual SIGTERM code-0/code-7 invocation exits and pre-file-
fsync storage faults. A further signal-test assertion requires this invocation's
JSON report to contain handled interruption evidence; its separate rerun passed
for both natural 0 and 7. These attempts are not represented as a clean full-suite pass.

Source mode assembles synthetic-source fixture packages. Package fault drivers
instrument only the owned package under test; they are distinct from real OS signal
checks and are not production hooks. Fake OS identities test reuse/lost ownership
without signaling any real unrelated process. Owned real children test ordinary
exit and descendant cleanup; uncertain platform cleanup is reported honestly.

At runtime source S, clean-commit builds, actual-package checks and adapter
qualification were pending; subsequent observed results are recorded below. Their exact identities and results must be recorded separately
before proposing a new integration target. No Linux qualification, live reviewer,
consumer adoption, release/tag, hosted artifact publication or registration follows
from this source record.

## Runtime source and local core qualification

Runtime source S is `1997a279126b0d04d9e52f0a0d26ab75bed4d7cc`, tree
`ee23de8895366efd692920274ad0bf7341bec84f`. Independent review covered the
committed implementation bytes; only the source-check outcome sentence was added
after the last read-only publication disposition. The clean source produced each
runtime archive twice in separate ignored filenames; repeat bytes were identical.

| Local artifact | Version | SHA-256 | Inventory |
| --- | --- | --- | --- |
| `dist/software-quality-0.1.1.pyz` | 0.1.1 | `7ea70e52c8526ec370f5dbce894de8527932f3c39c8afb7ba83567f01eef40b1` | 29 members |
| `dist/software-quality-external-0.2.1.pyz` | 0.2.1 | `cb4927a5290ba0da0892f9671e703b4ade0307a564f451f69236f165ca5b45d5` | 20 members |

Both manifests name S and policy 0.1 with their original schema structures 1/2.
Every payload digest and inventory member was checked against the actual archive
and S's committed blobs. The expanded core now includes external modules/schemas;
its actual archive's complete import closure was checked in isolated Python,
including shared evidence exports. This does not turn its v1 entry point into an
external route. The separate external archive contains exactly seven quality
modules and seven external schemas, no core CLI/process/runner modules. Its shared
trust file contains the generic ownership utility but the external entry does not
dispatch a target gate.

The actual core affected selection passed 51 tests on Darwin arm64, Python 3.14.7.
Twenty context cases use the source frontend and actual core; twelve legacy cases
exercise actual core execution/launcher behavior; four trust cases validate actual
artifact/default-pin/startup boundaries; fifteen process/caller cases exercise
source helpers, fake OS faults and owned benign children. This is a mixed evidence
selection, not 51 actual-package-only cases or a full historical suite rerun.
No Linux or Python 3.11 execution was performed.

The adapter compatibility metadata now records this observed core source/digest
and patch versions without changing either runtime ZIP. Adapter source S2 is a
later metadata/evidence commit; its bundle still requires actual qualification.
This avoids embedding an artifact digest inside its own source identity.
