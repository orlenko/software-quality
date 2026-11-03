# Source review controller candidate checks

This evidence covers the source-only controller candidate, not an artifact build,
consumer adoption, live provider run or independent-attestation qualification.

Independent design critique preceded code. Its findings and accepted changes are
recorded in [decision 0008](../decisions/0008-source-review-controller.md).
The initial CLI alternative was removed; the candidate uses one fixed text-only
HTTPS transport and a bounded immutable-source request dispatcher.

Offline checks use invented source repositories and credentials plus a fake
standard-library HTTPS connection. No live key is read or provider invoked:

```sh
python3 -I -S -c 'import sys, unittest; sys.path.insert(0,"."); unittest.main(module="tests.test_source_review", verbosity=1)'
```

Observed result after both fixes: **19 tests passed** on CPython 3.11, no skipped
tests. The preceding 18-test revision also passed on CPython 3.11 and 3.14;
that observation is not a claim that the final revision was rerun on both.
These cover bootstrap/null context, real base config/lock/context matching,
dirty/ignored/untracked exclusion, approved base rubric authority, path traversal,
links/gitlinks/binary/oversize refusal, additions/deletions/mode changes, uncovered
changes, unsupported action refusal, required inspection and action limits,
invalid findings, duplicate/extra provider output, tool calls/refusals/model
mismatches, fixed HTTPS host/path/empty-tools/nonstored requests, no environment
endpoint/proxy routing, sanitized transport errors and explicit CLI API approval.

The independent adversarial review identified a concrete coverage defect:
repository-local `diff.ignoreSubmodules=all` could hide an omitted changed gitlink
from `git diff --quiet`. A new regression reproduced it and failed before the fix
(`Invalid` was not raised). The coverage command now explicitly uses
`--ignore-submodules=none`; the regression and the full dedicated suite pass.

The reviewer also identified reuse of a view's read history across fresh review
conversations: a second invocation could claim inspection using the first one's
reads. Each `review` now starts a fresh read list; a regression checks that the
first witness retains its two reads while a second finish-only conversation is
incomplete with none. The normal CLI already constructed a fresh view per run;
the fix also protects the reusable function.

Independent finished-code review and re-review completed before push, with no
remaining confirmed blockers. The submodule finding was a BLOCKER and the reused
read-history finding a SHOULD-FIX; both were fixed and re-reviewed. The reviewer
traced path selection, immutable blobs, base rubric/context binding, dispatch,
HTTPS routing, authentication handling and completion; independent in-memory
probes confirmed that shell/network actions and function/custom/web-search output
cannot dispatch. The 19 filesystem-fixture tests above were author-observed;
the reviewer did not independently rerun them or invoke live inference.
This native bootstrap code review is evaluated against the repository's prior
rules; it is not a witness produced by the new controller.

Existing core/adapter versions, source identities and all artifact bytes remain
unchanged. No existing receipt is rebound to this code. A live authenticated
public-source/model/account run, owner approval of identity/independence and
provenance, integration/release and any consumer acceptance remain separate.
