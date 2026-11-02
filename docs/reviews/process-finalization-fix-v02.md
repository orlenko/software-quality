# Process ownership and failure-finalization correction

Current-status note (2026-11-02): this is a historical qualification record. Its
main-status and pending-integration statements describe that earlier checkpoint.
The later [source integration update](approved-path-fix-v01.md#source-integration-update-2026-11-02)
records the completed source operation. The exact artifacts and observations below
remain historical; their held status and qualification limits are unchanged.

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

## External and adapter actual-byte qualification

The actual external 0.2.1 archive passed all 44 selected importer tests. Ordinary
CLI cases use that archive through install/launcher/shim/import; store clock/save
faults remain source-helper assertions. Two isolated drivers import only the
actual package, verify its self identity and inject final-clock KeyboardInterrupt
or output OSError followed by diagnostic KeyboardInterrupt. Current invocations
return 1 for bound natural 7 and 2 without validated failure. These drivers are
instrumented package checks, not real OS-signal evidence or production hooks.

The separate real OS-SIGTERM case watches an accepted checkpoint, signals the owned
CLI, and requires the current invocation's JSON report to identify handled
interruption. It asserts that invocation's exit 1 for bound natural 7, exit 2 for
natural 0 without complete evidence, retained disk verdict and same-byte retry.
A supplementary one-case run uses the identical actual archive and test, selecting
SIGINT in the parent harness instead; both code-0/code-7 assertions passed. No
production module or package bytes were changed for either real-signal case.
Hard termination and unavailable output channels still limit delivery/durability.

Adapter source S2 is `9957f23fb87858f0f157a4e39e79211387a246e2`, tree
`109d9794d2d7a48ec10229a0374831916354f364`. Only compatibility metadata and this
record differ from S. The shared trust/process/frontend and both bootstraps are
byte-identical between S and S2; neither runtime artifact was relabeled or rebuilt.
The actual adapter 0.1.1 bundle `dist/quality-adapters-0.1.1.zip` has SHA-256
`720ee551a1128d24cf5f4a7ff6eb6f2ca80d105796112c83c859130278f04eca` and twelve
members including its manifest. Two clean-S2 builds were identical. Inventory,
member digests, committed source bytes, runtime compatibility source/digest and
shared closure were verified. All twenty context tests passed against the actual
bundle plus actual S core: offline/context handling, metadata helpers, overflow,
timeout, owned cancellation and failure precedence. Metadata responses/helpers
remain invented; no live GitHub/authentication or host registration was exercised.

## Additional caller found during aggregate audit

The final aggregate audit found an advertised simple shim still using
`subprocess.call`: direct SIGTERM could end it while bootstrap/runner work continued,
and Ctrl-C could kill its bootstrap before owned failure handoff. The twenty bundle
context tests did not exercise this caller. Therefore the S2 `720ee…` bundle remains
unchanged but held; its context results do not qualify the entire advertised adapter.
Runtime S core/external archives and their results remain unchanged.

The independently critiqued amendment in decision 0006 reuses the adjacent approved
frontend relay and existing cancellation utility, with explicit launcher/interpreter,
protocol 1 and closure refusal. Replacement adapter source S3 will contain this
reviewed shim correction and new source/bundle tests, rather than only S2 metadata.
Source review found a caller-relative-path compatibility defect in the first fix.
The shim now strictly resolves approved interpreter/launcher paths and supplies the
invoking directory to the existing shared relay; relative target/cache/state inputs
retain their meaning. Missing resources/objects return incomplete/2. The frontend
otherwise retains its previous default directory. Initial shim checks had two
harness errors from attempting unchanged fixture commits; independent fixtures
fixed those errors and all three cases passed. A new relative-directory case and
two affected frontend checks passed with the four shim cases (six tests). A further
injected Path.cwd KeyboardInterrupt case passed after adding an incomplete/2 guard.
The replacement qualification below covers the corrected source. No runtime S file
changes were required.

## Replacement adapter qualification

Replacement adapter source S3 is `a3e74ed210311735395ebd8b4180f8fbb54feed3`, tree
`23e9f771b82f46f1bb932cf263fdcdf16ecb0f3f`. Independent adversarial review accepted
the shim, optional frontend relay directory, tests and follow-up fixes before this
commit. Current simple-shim and frontend payload changes are intentional; runtime
S code, trust/process utilities and both bootstraps remain unchanged.

The corrected `dist/quality-adapters-0.1.1-relay-fixed.zip` has SHA-256
`43435c2770ae093f91c3e5374f0352e13f26ac0435f032c3202ab1e8af754ee4`. Two clean-S3
builds were identical. Its twelve members, manifest source/version/protocol,
committed payload blobs, shared closure and actual S core compatibility pin were
verified. Compared with the held S2 bundle, only the two adapter Python payloads
and source/file manifest change; the compatibility/core identity stays fixed.

All 25 selected checks passed against the actual corrected bundle and S core:
twenty frontend context cases and five direct simple-shim cases. Normal delegation
returns 0/1/2 as appropriate; pin/protocol overrides, missing closure and unavailable
explicit interpreter refuse with 2. Relative approved paths/target/cache/state keep
the caller's meaning. A test-side path-setup KeyboardInterrupt returns 2 before a
core launch. Real SIGINT and SIGTERM each exercise active work and a naturally
completed nonzero leader, require this invocation's run-interrupted report and
exit 2/1, and observe the benign leader/descendant stopped with read-only process
queries. No unknown identity is signaled and no PID reuse is forced. These checks
prove the owned fixture paths, not universal platform cleanup or consumer gates.

The earlier S2 `quality-adapters-0.1.1.zip` / `720ee…` bytes are preserved and held;
only this separately identified corrected bundle is proposed. No artifact was
uploaded or automatically installed. Final aggregate review remains a source and
evidence gate before a separate source integration proposal.

## Reproduction and preservation

Use approved exact source S for runtime builds and exact source S3 for adapter
packaging; building a later documentation commit changes source provenance and
artifact bytes. Builders require clean source and a nonexistent output. Commands
below describe the observed selections; the source-helper distinctions above apply.
The complete runtime selection is intentionally limited to affected paths.

```sh
python3 -I -S tools/build.py --output dist/software-quality-0.1.1.pyz
python3 -I -S tools/build_external.py --output dist/software-quality-external-0.2.1.pyz
python3 -I -S tools/test.py --artifact dist/software-quality-0.1.1.pyz \
  --match 'tests.test_owned_process|tests.test_runner.RunnerTests.test_(complete_check|required_failure|changed_script|command_environment|timeout|definite_failure|missing_command|adapter_uses|interruption|initial_report|launcher_forwards|handled_cancellation)|tests.test_context|tests.test_trust.TrustTests.test_(artifact|archive|python_startup|cached)'
python3 -I -S tools/test_external.py --artifact dist/software-quality-external-0.2.1.pyz
# From separately reviewed adapter source S3, retaining the approved S core:
python3 -I -S tools/package_adapters.py --output dist/quality-adapters-0.1.1-relay-fixed.zip
python3 -I -S tools/test.py --artifact dist/software-quality-0.1.1.pyz \
  --adapter-bundle dist/quality-adapters-0.1.1-relay-fixed.zip --match 'tests.test_context|tests.test_legacy_shim'
```

Supplementary SIGINT reproduction selects the signal in the parent test harness:

```sh
python3 -I -S - <<'PYTHON'
from pathlib import Path
import signal, sys, unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path.cwd()))
import tests.test_external as cases
cases.ARTIFACT = (Path.cwd() / 'dist/software-quality-external-0.2.1.pyz').resolve()
suite = unittest.TestSuite([cases.ExternalTests(
    'test_actual_cli_interrupt_after_checkpoint_preserves_failure')])
with patch.object(cases, 'signal', SimpleNamespace(SIGTERM=signal.SIGINT)):
    result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PYTHON
```

The new trusted bootstrap file SHA-256 identities at S and S2 are:

| File | SHA-256 |
| --- | --- |
| `quality_launch.py` | `978fe442eac4355db441ea5fea1f0a3ac581606fcc2d25f9a0b68b39404bfa8c` |
| `quality_external_launch.py` | `55f9b485a62a488ee09a88a1696559dc840c4d16a849df62676efe148295dbb1` |
| `quality_trust.py` | `2da9b3cc5e53787fa25546b08578c5e0b3fc6b78ff778b65ca60753dc688dd4f` |

New launchers require the new explicit patch pins. Old pins/state are not silently
upgraded or migrated. Earlier frozen core, external and adapter files retain their
original hashes and sources recorded in the historical evidence. The source-70
external bootstrap objects retain their recorded hashes. Prior work refs remain
unchanged. Raw outputs and local archives remain ignored and unpublished. The old
real-executed fixture was not rerun, relabeled or used as proof for the new bytes.

Main remains `e543e1a9a27d44e3ec04e862dfb184858985e260`. Final source integration
is a separate proposal after aggregate review; no fast-forward, main push, tag,
release, hosted archive, consumer pin/install, live provider or adoption occurs here.

Final independent aggregate inspection found no remaining source or qualification
blocker for a new integration proposal. It covered the original ownership and
failure-finalization paths, the advertised shim correction, source S/S3 continuity,
actual archive identities/inventories and observed logs, including their mixed
source/package limits. A separate final factual/publication review cleared the two
document changes. Both reviews used read-only inspection of source, hashes,
archives and existing logs, with no imports, execution, writes or Git metadata
mutations. The integrator checked staged content/metadata and preserved identities.
A documentation-only completion needs no additional runtime rerun. This disposition
supports a new exact work-branch source proposal only; main integration remains a
separate operation and the held S2 bundle is not cleared.
