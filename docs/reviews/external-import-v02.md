# Import-only candidate qualification

Scope: work-branch engine/package `0.2.0`, schema 2, protocol 2, unchanged policy
`0.1`; accepted review rules are the repository/policy at `c6b311f`. No consumer
or producer provisioning, private inputs, provider calls, dependency installation,
main merge, release/tag or hosted artifact publication is part of qualification.

## Design review

[Decision 0004](../decisions/0004-external-import-slice.md) records the user problem,
observable acceptance, smaller incomplete alternative, responsibilities/effects,
failure/recovery and test plan. Independent read-only design critique required
three changes: caller trust cannot remove registry controls; approved observer
source/invocation/profile and full interval/cleanup must bind the same operation;
clock domain/order/uncertainty must be explicit. All were accepted before code.
Policy 0.1 is retained because externally attested synthetic candidate facts are
separate from hard mechanical control obligations, which require independently
approved actual controller observations. Parsing does not prove their reality.

## Independent adversarial source review

The independent source reviewer identified six reachable blockers, all accepted:

1. An outside alias entering a target ancestor then linking back out could choose
   an input/state path. Reuse the owned per-ancestor canonicalization rule in a
   shared helper; preserve lexical state paths through bootstrap delegation. Refuse
   parent components too, preventing symlink-plus-parent normalization bypass.
2. Sampling issuance before Git inspection admitted a pre-challenge invocation.
   First durably write a non-importable challenge, then sample issuance and
   atomically publish the issued record. A half-issued record is refused.
3. Within-tolerance wall rollback could extend a short window. Require producer
   wall/monotonic start/finish and admission facts, validate both temporal orders
   and freshness ages. Reimport cannot refresh either completion clock.
4. A success completing after the observed deadline could pass inside the broader
   registry budget. Bind observation intervals/deadline/cleanup on both clocks and
   require completion within the observed deadline plus declared 1 ms precision.
5. Late metadata timeout or clock-read failure could return generic incomplete
   after this invocation already persisted natural failure. Catch those late
   failures, checkpoint explicit gaps and retain fail precedence.

6. Observer wall/monotonic fields could describe contradictory instants while
   passing each independent inequality. Require every observer interval, cleanup
   and deadline clock pair to agree within the supported continuity model.

Each has a negative/recovery test; cases include a safe macOS `/var` alias,
within-tolerance rollback, contradictory observer clock pairs, late deadline success/failure and an actual ZIP process
interrupted after its failure checkpoint. Fix re-review found no remaining blocker in staged tree
`97378137d6f5b300dbdcc2d12cd1c6cc04ad799f`. No deferred finding remains.
The review used the prior accepted rules without target execution, consumer/private
reads or provider calls. The reviewer ran `git write-tree` to confirm this supplied
hash, outside the requested read-only mode; it wrote Git metadata, made no source
edit, and returned the same tree. No enforced reviewer boundary is claimed.
Later qualification-document edits do not alter the reviewed payload bytes.

## Qualification evidence

On macOS/Darwin 27.2.0, Python 3.14.7, the final reviewed source suite
`python3 -I -S tools/test_external.py` passed 36 tests in 55.303 s on the staged
reviewed tree above. The four relevant v1-default source regressions also passed
in 2.406 s: complete reviewed check, interrupted report/lock release, artifact
identity refusal and strict JSON. Subsequent production edits only tightened a
new external-only path helper; v1 default calls do not use it. Old artifact suites
were not rerun. The actual new-package run
`python3 -I -S tools/test_external.py --artifact dist/software-quality-external.pyz`
passed the same 36-case suite in 55.163 s. CLI cases use the actual installed ZIP;
internal deterministic clock/fault/store assertions still use source helpers,
as documented below.
Two clean builds and byte comparison were identical. The 20-member ZIP inventory
was inspected: no v1 runner/process/CLI module, unchanged policy text, and all
payload source bytes equal the independently reviewed staged tree. The source
commit differs from that reviewed tree only in this qualification document.

| Identity | Value |
| --- | --- |
| Package source commit | `70a054bcbc77605d1d4f7c5a2fdc2af30c33705a` |
| Package source tree | `77be96ff925004566e380fee17dc4e74cfb24475` |
| Local artifact | ignored `dist/software-quality-external.pyz` |
| Artifact SHA256 | `958a5261f752e523eec74a75ffa3719b1536f966a67db3a482d5e5bd6e9b1cd4` |
| Versions | engine/package 0.2.0, config/report 2, adapter 2, policy 0.1 |

Manual actual-package checks additionally verified protocol 1 refusal with otherwise
valid complete doctor arguments (no state created), a MAX_JSON+1 approved receipt
refused without poisoning a later valid import, and budget 3600/window 900 validation
ceilings. The bounds check validates data only. A reproducible sequence
using the owned invented fixture follows:

```sh
python3 -I -S - <<'PY_CHECK'
from pathlib import Path
import sys, tempfile, zipfile
sys.path.insert(0, str(Path.cwd()))
from quality_trust import MAX_JSON, parse_json, sha
from tests.external_support import Fixture, config
package = Path('dist/software-quality-external.pyz').resolve()
data = package.read_bytes()
with zipfile.ZipFile(package) as archive:
    source = parse_json(archive.read('manifest.json'))['source']
settings = config()
settings['gate'].update(budget_seconds=3600, import_window_seconds=900)
with tempfile.TemporaryDirectory() as directory:
    fx = Fixture(Path(directory), package, sha(data), source, settings)
    rejected = fx.command('--adapter-protocol', '1', 'doctor',
        '--repo', str(fx.repo), '--base', fx.base, '--head', fx.head,
        '--identity', 'example/invented', '--cache', str(fx.cache),
        '--state', str(fx.state), '--trusted-head', fx.head)
    assert rejected.returncode == 2 and 'invalid choice' in rejected.stderr
    assert not fx.state.exists()
    plan = fx.plan()
    envelope, observer = fx.facts(plan)
    result, output = fx.receive(plan, b'x' * (MAX_JSON + 1), None)
    assert result.returncode == 2 and output['report']['overall'] == 'incomplete'
    result, output = fx.receive(plan, envelope, observer)
    assert result.returncode == 0 and output['report']['overall'] == 'pass'
PY_CHECK
```

The old source refs remained main `e543e1a`, adapters `908995c`, compatibility
`c6b311f`. Old ignored runner/artifact hashes remained
`9403401102f01d87991fb2de5405eff4b7012480c955e858b8bb0a0fa2bee6a2`
and `3f7f0bb6be8ced3d1e3f47e749449fcac0ef9923d4b56162f16ce9a5ff313142`.
Staged bytes/author metadata, relative links, whitespace, invented/public-only
content and clean-source build prerequisites were checked before publication.
No artifact bytes, receipts, credentials or local report paths are committed.

Intermediate runs
are diagnostic evidence only: the first caught a missing bootstrap import path
under isolated Python and was fixed; another crossed a schema edit and is not a
qualification result. No partial/failed run is counted as a pass.

The new suite uses newly authored plain-text/JSON Git subjects and invented
producer/controller fact factories. No target gate, producer/controller executable,
actual privacy/product/reviewer operation or live model is invoked. Source mode
builds a temporary synthetic-identity ZIP; artifact mode must use the separately
built actual candidate. Internal deterministic clock/interruption cases test the
source store directly, with no production clock override. These cases establish
parser/local-state behavior, not real enforcement or natural consumer fit.

Missing evidence: Linux execution; real producer provenance, consumed-input
mechanism and controller enforcement; authorized independent live review route;
consumer command fit and actual adoption. Required unsupported obligations remain
incomplete. No real gate deadline/window fit or policy waiver is asserted.
