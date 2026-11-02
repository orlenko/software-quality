# Command adapter evidence

Status: reviewed source and locally verified bundle candidate, 2026-11-02.
No release publication, plugin/global installation, consumer access or adoption.

Accepted rules/source baseline: `e543e1a9a27d44e3ec04e862dfb184858985e260`.
The [decision](../decisions/0002-command-context.md) and independent critique
dispositions were committed at `12ca958`. The previously reviewed engine, trusted
launcher/bootstrap and artifact remain unchanged. The thin command task does not
change the runner's policy or accepted consumer pin.

The final source suite passed 59 tests on the reviewed blobs below. Tests use invented
repositories, metadata executables/auth directories and recorded reviewer responses;
they do not call live GitHub or live reviewers. They cover explicit fallback/core
argument equivalence, accepted pin preservation, wrong repository, missing route/
permission/object, ambiguous/current/fork context, moving PR/base/local branch,
post-core stale context, actual core failure precedence, safe host/auth environment,
and target-side bootstrap symlinks. This is not live-host registration evidence.

Installed skill-creator `quick_validate.py` was invoked but cannot run because
PyYAML is unavailable. No dependency was installed. Manual frontmatter/name/reference
checks are the documented alternative for these simple authored manifests; their
frontmatter/name/resource checks passed. Python/JSON syntax and 40 local Markdown
links were checked at that point. This manual alternative is not a PyYAML validator
pass or live harness test.

Independent direct workflow evaluation used only invented inputs and permitted
inspection. Ambiguous current candidates required explicit selection without a run;
explicit immutable inspection yielded incomplete command/review evidence without
target execution; wrong-repository metadata was refused without accessing that
repository. No live harness discovery/registration was exercised, no actual user UI
question was submitted, and raw evaluation notes/transcripts were not published.

The independent native code reviewer evaluated against accepted `e543e1a` rules.
Corrections were fixed and re-reviewed: preserve exact Unicode branch refs; bound
metadata output during execution and clean up the owned helper group; retain known
immutable identities on lookup failure; suppress telemetry/update requests; resolve
one complete source/bundle import root. Runtime tests caught an import collision
missed by source review; that failed interim run is not qualification evidence.
The final affected-source re-review found no remaining blocker or deferred finding.
The reviewer did not execute code, contact providers or access private inputs.

Reviewed final Git blobs:

| File | Blob |
| --- | --- |
| `adapters/quality_context.py` | `585f0ce798a85e45d155ba162c498e01d0749587` |
| `tools/package_adapters.py` | `659616664954e36ed3fb1ab5ffabe51832b1c250` |
| `tools/test.py` | `b9443a15ef263ef687f2ea12c3a9ccc441fd75c0` |
| `adapters/workflow.md` | `18d3f6a881039896a141d8971f61b06909ee8ae1` |

Clean-source adapter candidate: `5843cf3f1375c40338d0ca4338241641a4d5fee9`, tree
`c5a68283a38e940d0761db5c7a11ebeb9ce3b6f6`. Source tests ran with the reviewed
runtime/test files above, and staged bytes were checked against that working tree.
Normal author metadata and actual staged contents were inspected before pushing.
Only newly authored generic/synthetic assets are tracked; no raw evaluation notes,
private data, checkout paths, tokens or consumer mappings were published.

Observed builds:

- `python3 -I -S tools/package_adapters.py --output dist/quality-adapters.zip`.
- A separate build to `dist/quality-adapters-repeat.zip` produced identical bytes.
- Adapter `0.1.0`, protocol `1`; bundle SHA-256
  `3f7f0bb6be8ced3d1e3f47e749449fcac0ef9923d4b56162f16ce9a5ff313142`.
  Its manifest validates 11 payload files, including both skills, shared procedure,
  frontend, unchanged owned trust/process helpers, compatibility and license.
- Original runner artifact bytes still match
  `9403401102f01d87991fb2de5405eff4b7012480c955e858b8bb0a0fa2bee6a2`, source
  `74b9b498058b11a3d99409e2d1166cbf9d171e9e`. Engine/policy/schema are unchanged
  at `0.1.0`/`0.1`/`1`.

Packaged qualification: `python3 -I -S tools/test.py --artifact
dist/software-quality.pyz --adapter-bundle dist/quality-adapters.zip` passed all
59 tests. The context cases ran the actual bundled frontend and helper modules,
with its complete skill/reference layout, against fresh caches of the retained
runner artifact. This independently exercises source versus bundle imports, the
outside-target launcher, accepted pin, immutable arguments, wrong/ambiguous/moving
metadata, credentials/environment, bounded output/group cleanup, cancellation and
failure precedence. No live GitHub API, reviewer or harness registration was used.

Observed environment: macOS, Python 3.14.7. Linux/other Python versions and live
GitHub/client/harness discovery are unverified. The final follow-up changes only
documentation; adapter/helper/test payloads remain identical to the reviewed and
tested source. Final relative-link, whitespace, actual staged-content/metadata and
publication checks complete the documented manual source gate; no broad automated
secret scanner is claimed. Templates remain uninstalled and unregistered. Source
stays on the work branch: no merge or user-global/consumer installation is in scope.
Core files, launcher, original builder and original artifact are unchanged.
