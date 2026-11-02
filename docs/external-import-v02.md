# External gate import candidate

Engine/package `0.2.0`, config/report schema `2`, launcher/adapter protocol `2`,
policy `0.1` unchanged. This is the bounded slice in
[decision 0004](decisions/0004-external-import-slice.md), qualified with invented
records only. No real producer/controller, enforced environment, Linux run,
consumer install/adoption, release or hosted artifact publication is established.
The existing v1 execution entry and old published source references/artifacts are
separate. No old600-second execution cap changed.

## Trust and supported subject

Use an owner-approved Python 3.11+ POSIX interpreter, Git, outside-target
`quality_external_launch.py` and `quality_trust.py`. Approve their exact bytes,
source identity and artifact digest through an already authenticated owner route.
A digest delivered beside arbitrary bytes cannot authenticate itself. No network,
package dependency, automatic install or hosted fallback is used.

The accepted **base** `.quality/config.json` is a strict schema2 registry of one
whole canonical gate, producer, observer/profile/mechanism, source/coverage/
environment identities, consumed-input mechanism, effects, required controls,
selected refs and ceilings. See [the schema](../quality/schemas/external-config.json)
and [invented factories](../tests/external_support.py). They are examples of
validator inputs, not a provisioned producer or consumer configuration. The base
lock uses the existing six lock fields with `schema_version: 2`, `version: 0.2.0`,
`policy_version: 0.1`, publisher `orlenko/software-quality`, and separately approved
full source/artifact identities. Head-side policy, lock and launcher are data.

The subject is one immutable committed first-party tree. Current HEAD, clean
checkout, staged-entry digest and configured local refs must match the issued
context. Samples are freshness observations; they cannot detect change-and-restore
or establish actual consumed inputs. The registered producer mechanism must bind
consumed bytes, environment and first-party import origin to the full context.
`immutable-tree`, `serialized-inputs` and `instrumented-inputs` are accepted
mechanism categories with separately approved digest identities, not implemented
execution backends. No actual-index privacy, private-input/product check or
independent reviewer is inferred. Record every such required unsupported obligation
in `unsupported_obligations`; each remains incomplete. Mapping completeness is an
owner responsibility, never established by generic gate success.

Owner `--trusted-head FULL_HEAD` is an explicit assertion for that exact head,
permitted only by the registry's trust rule. It cannot remove any registered
control. Unknown/untrusted reported provenance or absent owner designation requires
containment too. Always-contained registries require containment and reject owner
trust designation. Effects cannot exceed the registry. No control is performed by
this importer.

## Explicit offline commands

Place the trusted bootstrap pair outside the target and keep cache, private state
and input files outside the target. State must also be separate from cache/toolkit;
inputs must be outside all those roots, including lexical paths and resolved
aliases. Parent (`..`) components are refused by this bounded interface. Paths below are invented placeholders. Replace identities only with
independently approved values. Neither shell variables nor placeholder values
supply trust.

```sh
python3 -I -S /approved/toolkit/quality_external_launch.py --adapter-protocol 2 install \
  --artifact /approved/artifacts/software-quality-external.pyz \
  --source FULL_TOOLKIT_COMMIT --sha256 APPROVED_ARTIFACT_SHA256 \
  --cache /owner/quality-cache

python3 -I -S /approved/toolkit/quality_external_launch.py --adapter-protocol 2 doctor \
  --repo /owner/subject --identity example/invented \
  --base FULL_ACCEPTED_BASE --head FULL_TARGET_HEAD --trusted-head FULL_TARGET_HEAD \
  --cache /owner/quality-cache --state /owner/quality-state

python3 -I -S /approved/toolkit/quality_external_launch.py --adapter-protocol 2 import \
  --repo /owner/subject --identity example/invented \
  --base FULL_ACCEPTED_BASE --head FULL_TARGET_HEAD --trusted-head FULL_TARGET_HEAD \
  --cache /owner/quality-cache --state /owner/quality-state --plan ISSUED_PLAN_ID \
  --evidence /approved/evidence/producer.json --evidence-sha256 APPROVED_RECEIPT_SHA256 \
  --approved-producer APPROVED_PRODUCER_ID \
  --observations /approved/evidence/controller.json --observations-sha256 APPROVED_OBSERVER_SHA256 \
  --approved-observer APPROVED_OBSERVER_ID
```

`adapters/quality_external.py` in the same approved source checkout is a thin
protocol2 delegation entry for these explicit arguments. There is no discovery,
skill registration or PR/provider call. Omit trusted designation only when the
required containment route is available; omission never grants execution.

`doctor` exits2/incomplete and durably writes a non-importable challenge record,
then samples issuance and atomically marks it issued before exposing
its random challenge/context. It does not dispatch or execute anything. Give those
identities to the already approved external route; do not fabricate or launch a
producer to fill missing evidence. `import` checks exact input bytes against the
operator-approved digest and actor. Approval flags are assertions from the caller's
trusted channel, not signatures or self-authentication. Missing approval is
incomplete.

## Evidence and verdict

[Producer envelope](../quality/schemas/external-envelope.json) protocol is
`external-checks-v1`; this record format name is independent of launcher protocol2.
The [single supported record](../quality/schemas/external-record.json) binds
plan/challenge/context, canonical gate, invocation, phase, actual consumed input
mechanism, environment/origin, whole coverage, natural outcome, timing and effects.
Cache, conditional, cross-phase and Git-aware execution features and precommit
phase are explicitly unsupported. Omitted/unknown coverage, consumed binding,
controls and output never become a passing skipped gate. Wrong origin/environment
or unsupported phase cannot supply an attributable natural failure either.

The [controller envelope](../quality/schemas/external-observer.json) is separately
owner-approved through an existing route outside producer/target control. It binds
the registered observer/profile/mechanism and same producer invocation and context,
full wall/monotonic observation interval, concrete deadline instant, cleanup instant/state and
per-control observation. Deadline and cleanup are mandatory; all other registered
mechanical controls are equally mandatory. Producer-route or manual statements,
wrong profile/invocation, partial intervals, unavailable/unknown controls, missing
containment and cleanup uncertainty remain incomplete. The deadline instant must
be within the approved budget, and completion must not contradict it. A later conflicting observation cannot replace an
accepted unknown/unavailable control with a passing claim.

This parser cannot prove a supplied observation genuine or enforce its claimed
control. Only independent owner approval of an actual controller route can establish
that basis. Merely using different identity strings or writing plausible JSON is
insufficient. Synthetic success demonstrates validation rules only.

Clocks must share the supported same-host/boot millisecond domain. Importer reads
kernel boot metadata and its wall/monotonic clock, requires issuance before start,
ordered finish before import, matching boot and at most2000ms continuity discrepancy. Producer facts include
wall and monotonic start/finish, and original freshness must satisfy both clocks;
a within-tolerance wall rollback cannot extend the import window. Every observer
wall/monotonic pair must describe the same instant within the supported continuity
model. Start must be at least1ms after issuance to avoid timestamp ambiguity.
Observer scope conservatively includes1ms precision uncertainty and cleanup.
Future/pre-challenge/reboot/rollback relationships fail closed. Budget1–3600 seconds
and import window1–900 seconds are validation ceilings, not enforced deadlines or
claims of real gate fit. Reimport never renews original completion time.

Reports label importer observations, operator assertions, external producer facts
and external controller observations separately. Exit0/pass requires every row
complete; exit1/fail means a validated bound naturally completed nonzero result;
exit2/incomplete means missing/invalid/stale/unsupported evidence. Termination,
wrapper error or an exit code alone cannot establish natural failure. Valid natural
failure wins over missing controls/output/coverage, stale receipts, malformed extra
records and later valid conflicting input. Invalid common JSON/frame cannot be
partially salvaged. A previous durable failure survives later invalid imports.

## Local state and recovery

A half-issued challenge record is refused after interruption. The private state root uses per-target and per-plan advisory locks and one atomic,
fsynced authoritative `PLAN_ID/record.json`, schema2, with a corruption-detection
hash. The hash detects accidental corruption, not owner tampering. Original input
and the first valid natural failure are immutable separate slots. Bound failure is
checkpointed before later record/control parsing. Exact-byte retry is idempotent;
a different positive receipt never replaces or renews original evidence; conflicting
valid failure is retained. Reports are derived from stored facts. Aged positive
facts become incomplete. Replay protection covers this intact local state only;
copying/deleting/restoring the ledger defeats that local assumption.

Handled interruption attempts a final atomic record; hard kill can leave only the
last completed checkpoint. Resume with the same plan and receipt bytes, never by
rerunning a gate. Corrupt state is refused rather than reset or overwritten.
Missing package/pin/runtime prerequisites can prevent the importer from opening
the ledger; inspect its last record, and do not interpret a generic launcher exit2
as erasing stored failure. Cleanup concerns importer temporary files only; no
external process or producer artifact is managed.

## Qualification

Run the README source and actual-package commands from a clean reviewed tree.
Source mode builds a temporary ZIP from current owned files with a deliberately
synthetic source identity; `--artifact` instead exercises the actual new candidate
through install, trusted launcher, thin shim and import CLI. Internal clock/fault
injection tests exercise store recovery separately; no production override exists.
The fixtures create only newly authored text/JSON Git subjects and invented facts,
never an executable producer/controller. Relevant shared-v1-default regression
checks cover parameterized pins, strict parsing and extracted evidence helpers.
No unaffected old artifact suite is rerun merely to inflate counts.

Exact source/tree/package digest, test results and independent adversarial review
are recorded in the [qualification record](reviews/external-import-v02.md).
