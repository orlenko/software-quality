# Toolkit self-adoption: inspection only

This repository's real [config](../.quality/config.json) and [lock](../.quality/lock.json)
adopt the approved core0.1.2 R2 identity for pinned inspection. Target execution is
disabled and authentic recorded-v1 review is unavailable. This is partial setup,
not full verified adoption, release approval or permission to merge arbitrary code.
Existing [AGENTS rules](../AGENTS.md) and stronger manual gates still apply.
The [decision](decisions/0009-toolkit-self-adoption.md) records design and critique.

| Component | Approved identity |
| --- | --- |
| Publisher / policy / schema / protocol | `orlenko/software-quality` / `0.1` / `1` / `1` |
| Core archive source R2 | `db120201d3f38d1c6e444bc4d1ca9586c3d8eee0` |
| Core archive SHA-256 | `7b87b9c23fbaf43941729f8bb2b0e1969fbf6872b02d8dbd23e074714bc526b0` |
| R2 `quality_launch.py` SHA-256 | `14d77ae4dd7a9fa69197f970fc7c98a716b65c1e7486ceb668b7b8f7a621aaf6` |
| R2 `quality_trust.py` SHA-256 | `4c3ebc346b1428e1d226180ecbb05a249c90de48ae25cdc8438b89bb901f6c2e` |

Approve those source/byte identities through the owner route before loading.
Copy the existing archive without rebuilding; extract the exact bootstrap blobs
from R2. Keep the pair together outside the target. Current main, this adoption
head and the separately built A2 bundle are different identities. A2 is optional
and unnecessary for the documented explicit invocation; no adapter is installed
or registered by this setup.

Use an inspected, explicitly approved POSIX Python interpreter with `-I -S` and
the unmodified capability guard. The previously observed native runtime was
Darwin arm64/CPython3.14.7; that is not evidence for every host/version. No global
runtime provisioning or unsafe reaper is allowed. Bootstrap/cache/state/evidence
must be new owned private outside-target locations, separate from each other.
Store local paths, install receipt and raw reports privately, outside public Git.

The following environment values are explicit operator inputs, not inferred
authorization or head-side bootstrap selection. `QUALITY_BASE` is an independently
accepted full setup commit and `QUALITY_HEAD` the exact inspected full target.
Review the initial setup delta against0124 before accepting that bootstrap base.
Using the same accepted base/head demonstrates metadata only, never change review.

```sh
"$QUALITY_PYTHON" -I -S "$QUALITY_BOOTSTRAP/quality_launch.py" install \
  --artifact "$QUALITY_CORE_ARCHIVE" \
  --source db120201d3f38d1c6e444bc4d1ca9586c3d8eee0 \
  --sha256 7b87b9c23fbaf43941729f8bb2b0e1969fbf6872b02d8dbd23e074714bc526b0 \
  --cache "$QUALITY_CACHE"

"$QUALITY_PYTHON" -I -S "$QUALITY_BOOTSTRAP/quality_launch.py" doctor \
  --repo "$QUALITY_REPOSITORY" --identity orlenko/software-quality \
  --base "$QUALITY_BASE" --head "$QUALITY_HEAD" \
  --cache "$QUALITY_CACHE" --state "$QUALITY_STATE"

"$QUALITY_PYTHON" -I -S "$QUALITY_BOOTSTRAP/quality_launch.py" check \
  --repo "$QUALITY_REPOSITORY" --identity orlenko/software-quality \
  --base "$QUALITY_BASE" --head "$QUALITY_HEAD" \
  --cache "$QUALITY_CACHE" --state "$QUALITY_STATE"
```

Neither invocation enables execution or supplies a review response. Expected
exit is2/incomplete. Pin and source inspection can pass while required check,
snapshot/output and review stages remain incomplete. A check command returning
incomplete is meaningful evidence of the disabled setup, not a full test pass.
No synthetic reviewer response may fill the gap. The named reviewer identity and
enforced boundary in config describe a required contract awaiting authentic owner
approval; they do not assert an available/independent/enforced reviewer exists.
Native setup design/finished reviews are separate advisory bootstrap evidence.

| Existing obligation | Mapping and current gap |
| --- | --- |
| Full source suite | Required `python3 -I -S tools/test.py`, full discovery including controller offline tests; no match/skip/subset flags.600s maximum and bounded logs. Unexecuted here. |
| Package/pin qualification | Existing immutable R2/A2 receipts stay bound to their original sources. Runtime/package changes need their own reviewed builds and actual-byte qualification, not a rebuild from this adoption head. |
| Independent design and adversarial review | Existing manual rules remain binding. Required recorded-v1 route stays incomplete until authentic identity, independence, provenance, permissions and exact context are approved. |
| Index/privacy/publication | Inspect the real repository index and actual staged content/metadata. A `.git`-free snapshot cannot satisfy index-based gates; no fabricated index or private-skip pass. |
| Documentation/product behavior | Check links and factual status plus affected observable CLI/workflow behavior. Generic suite results do not replace required product evidence. |
| Integration/release | One integrator; preserve others' work and bind reviews/checks to actual integrated source. Source/config integration does not publish a release or establish full adoption. |

The configured future suite creates/removes invented disposable Git subjects,
fixture archives and helper processes, with fake inference only. It is disabled:
there is no blanket command/import trust approval. Before future execution,
inspect the exact interpreter, dependencies, target scripts/imports and declared
effects; accept a known-source owner route or require real containment for unknown
provenance. Exports/worktrees do not provide that containment. Snapshot/index and
600s limits cannot be bypassed by splitting required full gates into passing subsets.

Required reviewer and target-execution gaps remain incomplete even after useful
source/config integration. The standalone source-review controller is not activated
by this lock; live API/model/account/spend and reviewer identity/context qualification
require their own approval/evidence. No private media/credentials, provider calls,
global registration, deployment or app restart are part of this setup.

Initial actual installation and metadata results will be recorded separately from
the design expectations, with sanitized source/config/lock/report identities only.
Raw report bodies and outside paths stay private. The initial setup and any final
documentation leaf require independent affected review before normal integration;
final metadata must identify the actual integrated commit and clean checkout.
