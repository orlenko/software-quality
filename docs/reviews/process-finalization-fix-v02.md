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

Actual clean-commit runtime builds, actual-package checks and adapter qualification
are still pending. Their exact identities and results must be recorded separately
before proposing a new integration target. No Linux qualification, live reviewer,
consumer adoption, release/tag, hosted artifact publication or registration follows
from this source record.
