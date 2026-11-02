# Bootstrap implementation evidence

Status: reviewed and locally tested source/artifact candidate. No published
release or consumer adoption. Prepared 2026-11-02.

Accepted rules: AGENTS.md, HANDOFF.md and candidate design/standard at
`c2cd0500e9a4c4d2beb8b28f3fcc67a4d947c585`. This separately recorded bootstrap
review governs the first implementation; the new runner does not approve itself.
The implementor is sole integrator. Independent native reviewers inspect public
newly authored files read-only, without target execution, private inputs or a
separate provider CLI/upload.

The [decision](../decisions/0001-minimal-runner.md) records problem, alternatives,
responsibilities, effects, failure handling and tests. An independent native design
reviewer supplied four required corrections, all accepted, and a supplemental
multi-route critique. Initial decision/dispositions were committed at `d3e622b`.

The separate independent native `code_review` reviewer performed adversarial
source review against the accepted bootstrap. Four blockers were fixed and
re-reviewed: inspection-time Git filters (including included configuration and
submodules); malformed extra review arrays erasing blockers; mutable/colliding
exports; and lost failure precedence during output limits, timeout or handled
interruption. Fresh per-check snapshots, before/after bytes/mode checks, separate
command/output/snapshot stages, and incremental review-blocker preservation are
covered by regressions. Final re-review found no remaining blockers or deferred
findings. No target code/private inputs/other repositories/provider CLI were used
by the reviewer. This is source review, not observed test or package evidence.

Final reviewed Git blob identities:

| File | Blob |
| --- | --- |
| `quality_trust.py` | `8e530268bb51ec0e3efed14f061911bb43e2cc85` |
| `quality/schema.py` | `410fa59a69e65f60cca21c160b00146eff60d8b9` |
| `quality/runner.py` | `8fb16423951bf63bfa1bde57a349be9e5e53228e` |
| `quality/process.py` | `a5f482043a11e459670cd15b80eaaed4deb63176` |
| `quality_launch.py` | `ffb1c4a00ef22cd97c3dd0d26f9cb71544b64d07` |
| `tools/build.py` | `10abb2a4d1e6099ebc8ba43fa1e7a9aa5ea5a55e` |
| `adapters/quality.py` | `dd8bd572dc1e79d83fb4b26b37cb4dc771bcefb1` |

Integrator-observed source checks on macOS, Python 3.14.7:

- `python3 -I -S tools/test.py`: 39 tests passed on the final reviewed code above.
  All repositories/data/reviewer responses were invented disposable fixtures.
- Python syntax parsing and example config/lock schema validation passed.
- Manual relative-link check: 26 local documentation links resolved at that point.
- Git whitespace checks passed. Targeted path/invite/key-pattern search found no
  matches; this is not a comprehensive secret scanner. Actual staged content and
  author metadata are inspected before publication; private inputs/logs are absent.

Artifact source: `74b9b498058b11a3d99409e2d1166cbf9d171e9e`, source tree
`49bfca43cc80183d5733796888a2c7b184a016bd`. The source commit contains the reviewed
blobs above and the 39-test suite; its working tree was clean before/after build
and package checks. Version `0.1.0`, policy `0.1`, schema `1`.

Integrator-observed package checks:

- `python3 -I -S tools/build.py --output dist/software-quality.pyz` succeeded from
  that clean source commit. SHA-256:
  `9403401102f01d87991fb2de5405eff4b7012480c955e858b8bb0a0fa2bee6a2`.
- A separate build to `dist/repeat.pyz` produced identical bytes/digest. The
  validated manifest includes source, 16 payload files, policy, schemas and license.
- `python3 -I -S tools/test.py --artifact dist/software-quality.pyz`: all 39 tests
  passed against that actual artifact. Fixtures explicitly installed it into fresh
  private caches, locked its real source/digest at accepted base, and used the
  outside-target trusted launcher. Tests demonstrated offline complete-check plus
  attestation pass, unknown provenance/missing review incomplete, definite failure
  precedence, head-side pin bypass refusal, cached tamper/symlink refusal and
  protocol-compatible thin-adapter delegation. This is synthetic pinned-install
  evidence, not observed consumer adoption or a live independent-review trial.

The follow-up evidence/contract commit changes documentation only; runtime, schemas,
tests, trusted bootstrap and packaged policy bytes stay identical to artifact
source. Integration uses the documented manual gate: inspect actual staged bytes
and metadata, confirm reviewed blobs and unchanged code/policy, validate links/status,
confirm no concurrent base movement, then fast-forward and push the reviewed source.
Source integration is separate from release publication and consumer installation.

Linux and other Python versions have not been exercised here. Raw private run logs
remain outside tracked content. There is no live-model accuracy claim. See the
[pilot contract](../pilot-contract-v01.md) for supported use and deliberate gaps.
