# Toolkit self-adoption: initial pinned metadata evidence

This records partial setup of canonical `orlenko/software-quality`, not full
verified adoption. Initial setup C is
`2e9e19b014b767aef64ec0ebf101247140f02054`, tree
`c7c32c72d8946cc3c7c78310a4b0e30f9e4fab0e`, based on integrated0124.
Its five-file config/lock/documentation delta received independent finished review
against0124 before the owner accepted C as bootstrap base. No blocker remained.
The prior independent [design critique](../decisions/0009-toolkit-self-adoption.md)
required this ordering and the distinction between native advisory review and
authentic recorded-v1 evidence. Both were retained. These native reviews were
observed read-only, with no target execution/imports/tests or Git writes; they
were not mechanically enforced reviewer attestations.

The exact existing approved R2 archive and both bootstrap blobs were independently
hashed before copying/loading into new private outside-target locations. Original
archive bytes and all 13 historical/interim/new archives stayed unchanged. The
approved isolated native CPython3.14.7 Darwin interpreter loaded only the R2
bootstrap, archive and standard library for installation/schema/metadata work.
Offline cache install exited0 and the digest-named cached bytes matched the
approved archive. The optional A2 adapter remains uninstalled; no command/plugin
was globally registered and no artifact was rebuilt.

| Accepted component | SHA-256 |
| --- | --- |
| Core R2 archive | `7b87b9c23fbaf43941729f8bb2b0e1969fbf6872b02d8dbd23e074714bc526b0` |
| R2 bootstrap launcher | `14d77ae4dd7a9fa69197f970fc7c98a716b65c1e7486ceb668b7b8f7a621aaf6` |
| R2 trust support | `4c3ebc346b1428e1d226180ecbb05a249c90de48ae25cdc8438b89bb901f6c2e` |
| C config bytes | `3661644281de1653bde177e1b4c11ebd72336f933d3f86091e9f8486ab231363` |
| C lock bytes | `a1b8528444c62703dab5812f2b33787da112fe4cb8b7ec1adca5562e60e7bc82` |

Approved R2 source remains `db120201d3f38d1c6e444bc4d1ca9586c3d8eee0`;
neither C nor the final adoption documentation head becomes its build source.
The actual cached R2 schema validated the config/lock without importing target
code. All 85 local Markdown link targets and two anchors at C resolved, staged
whitespace/publication checks passed, and runtime/policy/schema/package/test bytes
were unchanged. Publication used sanitized facts only; private paths and raw
stdout/reports remain outside public Git.

Actual outside-target launcher invocations used independently accepted
`base=head=C`, exact canonical identity and separated cache/state. Neither used
`--execute-trusted`, a reviewer response or an approved review digest. The R2
guarded launcher completed its benign owned capability probe and delegated to
the exact cached archive. Both invocations returned2/incomplete as expected:

| Mode | Run ID | Report SHA-256 |
| --- | --- | --- |
| doctor | `5789ce37626a43699de0868df5accac3` | `cac7fabb3dac1051ca94680bdffd9d440da18ba6a0d928dcd78b620c5d2462d7` |
| inspection-only check | `7f3fbb3e138f448cadbbe46d4ae756ce` | `eac9e9d1554243092b781958237bbe8ed519408f8e9ed6dab72b8ecb7cc25ff4` |

Both contexts match C/config/lock/R2/artifact identities. Inspection, accepted
artifact verification and clean/stable source stages passed. Doctor's required
source-suite stage is incomplete with `doctor-does-not-execute`; check's is
incomplete with `trusted-local-authorization-or-isolation-missing`. Snapshot and
output stages remain `not-run`; review remains incomplete with
`review-response-and-approved-digest-required`. No review record or target test
was supplied or executed. Empty changed paths describe metadata inspection only,
not review of0124-to-C or a representative source change.

Configured: real required full source-suite/reviewer contract and exact lock.
Installed: verified approved local R2 cache/bootstrap. Executed: schema, install,
doctor and inspection-only check. Full target execution, actual-index/full-gate
evidence, authentic reviewer identity/independence/enforcement/context and verified
adoption remain incomplete. Previous package/source-suite counts do not qualify
this adoption target. Live API/model/account use, release and all consumer rollout
outside this canonical repository remain separate.

The subsequent documentation evidence leaf changes no config/lock/runtime bytes
and receives its own affected review before normal integration. Its source and
final clean integrated metadata must be recorded separately; these C reports are
not rebound to a later head. See the [runbook](../toolkit-self-adoption.md).
