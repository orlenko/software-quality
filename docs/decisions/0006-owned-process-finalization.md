# Owned-process identity and failure finalization corrections

Status: independently critiqued design; corrective implementation under local
qualification, 2026-11-02. Baseline
is `60a706165934b7730e04f76b928469de2f1b427e`; accepted policy 0.1 and prior rules
remain binding. Source-main integration of that exact tree was cancelled after
aggregate review found released process-group identity and late interruption
failure-precedence defects. This work proposes a new reviewed candidate, never a
substitute main update or silent patch of frozen artifacts.

## Problem, acceptance and smaller alternative

Legacy execute and metadata polling reap a helper leader before a shared cleanup
function signals its numeric PGID. A scheduling pause can allow ID reuse and an
unrelated group kill. Separately, a late importer KeyboardInterrupt outside its
handler returns exit 2 after this invocation already persisted validated failure.
The smaller alternative is to keep these routes held from new adoption and leave
main untouched. The correction must preserve identity ownership through the last
possible signal and validated same-context failure through every handled clock,
checkpoint/save/cancellation/CLI finalization path. Unknown capability, ownership,
context or evidence stays incomplete; a nonzero unbound receipt is never failure.

## Runtime, package and compatibility choices

Keep existing Python 3.11+/stdlib/Git on supported Linux/macOS POSIX; no dependency,
provider, containment platform or service is added. Use the OS non-reaping
`waitid(P_PID, WEXITED|WNOHANG|WNOWAIT)` observation rather than Popen.poll/wait/
communicate in signal-capable lifetimes. Unsupported API/signal policy refuses
execution; unexpected ownership loss refuses every signal and reports cleanup
incomplete. This is trusted-local process supervision, not hostile-code containment.

Approved patch identities: core/package 0.1.1, external/package 0.2.1, adapter 0.1.1.
Config/report structures 1/2, agent protocols 1/2 and policy 0.1 stay unchanged. Engine
identity constants follow the explicit patch versions; old pins/states remain on
old frozen tool routes, never migrated or rewritten. New artifact/source/digest
approval and fresh matching plan contexts are required. Any actual structural or
policy incompatibility is a block, not an inferred waiver.

The v1 builder enumerates the current quality Python/JSON tree, including new
external modules. Its new 0.1.1 ZIP is an explicitly new expanded inventory; review
and qualify that actual closure and entrypoint. The external 0.2.1 builder continues
its explicit import-only whitelist without process/runner/legacy CLI. Both archives
share one clean reviewed runtime source commit. Then record those known source/
digest identities in adapter compatibility data and qualify a separately built
adapter 0.1.1 source/bundle. That later adapter source may differ only in deliberately
recorded adapter metadata/docs; it must not relabel either runtime archive.

The trusted source bootstrap pair defaults explicitly to 0.1.1 or 0.2.1, respectively.
Their protocols/arguments and strict accepted-base selection remain. The protocol 1
frontend consumes the shared owned-process helper, so its actual bundle must carry
that exact helper closure; protocol 2 stays explicit import-only. Old 0.1/0.2 source,
bootstrap objects, all old work refs and three old artifact bytes/digests remain
intact. Use distinct ignored versioned filenames; no release/tag/hosted artifact,
consumer pin/install or main integration is authorized.

## One owned process mechanism

Add one owned lifetime primitive in quality_trust.py, already carried by both
trusted bootstrap pairs and the adapter bundle. The execution module imports it;
no caller-specific ownership engine is added. The external package has no target
dispatch entrypoint, but its shared trust utility is execution-capable when used
by an explicitly authorized bootstrap. It creates its
Popen with a new session/group and retains the actual direct-child object. It owns
these states: unreaped/signaling permitted, signal capability ended, reaped, or
ownership unknown. Only the primitive observes or reaps its child; callers never
poll, wait, communicate or fall back to numeric signals themselves.

A non-reaping observation validates the direct-child identity and derives exit
status from waitid result, retaining natural result independently from cleanup.
Do not assign Popen.returncode from WNOWAIT: the later real wait must still reap.
Popen.returncode already set, ECHILD or another ownership inconsistency ends signal
authority immediately. Missing/unsupported observation cannot be converted into
permission merely because the numeric PID exists. Verify required OS API/flags and non-autoreaping signal policy, plus a bounded
known-benign interpreter probe establishing usable WNOWAIT before target/helper
work. The probe is owned, launches no target code and is naturally reaped without
using an unproved numeric signaling capability. If it cannot finish/establish the
capability, refuse target execution and retain honest cleanup uncertainty. Capability
failure after launch remains explicit cleanup uncertainty; no broad process search,
unrelated kill, retry or OS-containment claim follows.

All group termination happens only while this unreaped identity is established.
Natural exit still allows cleanup of owned same-group descendants while the leader
reserves identity. A dead/empty group may produce platform permission errors; retain
those actual observations rather than treating EPERM as empty. End signaling
capability before the first potentially reaping wait, even if wait itself raises
or is interrupted. After that, only non-signaling liveness/group observations are
permitted; an apparent reused group is uncertainty, never a target for another
signal or fallback kill. Cleanup passes only with the recorded owned wait and
supported empty-group evidence; lost ownership/capability remains incomplete.

Refactor legacy execute, metadata polling and bootstrap/core-relay forwarding to
this single primitive, preserving
bounded selectors/output, finite deadlines, known natural code and separate cleanup
status. Include normal exit, timeout, output limit, SIGINT/SIGTERM/KeyboardInterrupt,
exceptions and finally paths. An interrupted cleanup may resume non-signaling wait/
reporting only after signal authority ends. Do not use process.kill/send_signal
fallbacks that may poll/reap implicitly. CLI signal handlers only record cancellation requests; they do not signal or
raise from a possibly reaping interval. The shared utility acts on requests at
bounded observation points while it retains authority. Keep handlers active through
CLI formatting/handoff; retain KeyboardInterrupt recovery for direct/fault-injected
paths. Fixed helper command/env/path/disclosure
permissions remain as previously accepted; this patch does not authorize new effects.

## Same-context failure evidence through finalization

Use one internal per-invocation evidence holder shared by import orchestration and
CLI handling. It is not a user-supplied hook or an alternate policy engine. Establish
it only after strict plan/state validation and agreement of the caller's immutable
repository/base/head/artifact/source identity with that plan. Observable source/
clock/cleanup incompleteness may coexist with a known failure for that requested
context; mismatched immutable request, corrupt state or unbound raw exit cannot.

The holder retains only schema-checked, mechanism/context-bound natural failure
facts already validated by the owned model. Update knowledge before a later
independent parse/clock/save action can interrupt; track successful atomic persistence
separately from knowledge. A final clock/checkpoint/save exception or handled
cancellation cannot erase the known result. Reports keep failure precedence plus
explicit interrupted/clock/persistence gaps. If a write cannot complete, do not claim
the returned in-memory report was durably committed; preserve the last complete atomic ledger
and say persistence is unconfirmed. Distinguish pre-replace failure from a visible
replacement with unconfirmed directory fsync; never roll back a possibly published
file or claim an interrupted temporary cleanup left it unchanged. Never overwrite corrupt state with defaults.

Wrap the entire post-validation lifetime, including final_clock/checkpoint and CLI
handoff/formatting, in this recovery contract. CLI may return failure only from this
validated invocation state; otherwise handled cancellation remains incomplete. A
best-effort interrupted save does not invent new timestamps, consume an uncommitted
receipt or promote a positive report. Repeated/hard termination may leave only the
last atomic record; no claim can override SIGKILL or guarantee delivery after process
exit. Single handled cancellation during working/finalizing known evidence must
produce fail/exit 1 for known bound failure and incomplete/exit 2 without it.

## Checks and independent gates

Before code: independent critique and recorded dispositions. Before integration:
independent adversarial source/fix review against prior accepted rules; fix/re-review
valid blockers and track any deferred nonblocking matter. Use newly authored owned
synthetic inputs and safe temporary outputs only. No old real fixture reruns for
renewed receipts and no unaffected historical suite repetitions for counts.

Meaningful affected checks:

- Fake OS/child observations deterministically model leader exit, reaping, PID/PGID
  reuse, lost ownership, unavailable APIs, interrupted wait and every final signal.
  Assert zero signals after release or uncertainty; never force unsafe real reuse.
- Owned benign children exercise natural 0/nonzero exit, same-group descendants,
  finite timeout/output limits and cancellation/exception cleanup through both
  legacy execution and metadata. No live metadata/auth/provider calls.
- After validated failure persistence inject KeyboardInterrupt in final clock/save
  and assert this invocation's report failure and CLI exit 1. Without validated same
  context assert incomplete, retaining honest interrupted/durability gaps.
- Test source helpers separately from actual new-package CLI signals/fault injection;
  no production arbitrary-code or clock-spoof hook. Every affected bootstrap/default,
  explicit version refusal, source/bundle import closure and new manifest/source/
  payload identity must be exercised appropriately. Existing unchanged evidence
  stays historical and does not discharge the new missing cases.

Bind results to exact reviewed source/tree. Build/check new actual 0.1.1/0.2.1 ZIPs
and adapter 0.1.1 bundle only from clean source, retain their payload/source/digest
identities and limitations, and verify old refs/artifacts/bootstrap objects remain
unchanged. Normal scoped work-branch commits/pushes may record deliberate generic
code/docs/results. No raw private paths/logs/account data or coordination records
are public. Return one new exact integration proposal only after qualification;
main remains at e543e1a unless a later task separately authorizes a new operation.

Independent inspection-only design critique accepted the correction after five
clarifications, all incorporated: include bootstrap forwarding and place the single
utility in shared trust; distinguish EPERM, signal attempts, owned waits and absence
proof for exited leaders/descendants; derive natural status without prematurely
setting Popen.returncode and probe usable capability; separate known facts, atomic
visibility and confirmed durability through every save phase; keep recovery and
handlers through CLI output, reporting channel failure/partial delivery honestly.
The reviewer accepted patch identity constants within unchanged schema structures
and the runtime-S/adapter-S2 sequence. Deterministic bootstrap-forwarding/reaping and
finalization-phase tests join the acceptance plan. No code, tests, imports, writes
or Git metadata mutations occurred in critique; no architectural blocker remains.

## Legacy shim correction found during aggregate audit

The final source audit found one advertised caller outside the corrected relay:
`adapters/quality.py` still used `subprocess.call`. SIGTERM could end the shim while
its bootstrap/runner continued; Ctrl-C could kill the direct bootstrap before owned
cancellation and failure handoff. The context-only bundle checks did not cover it.
The earlier new adapter candidate stays unchanged and is held from integration.

The smallest correction reuses the adjacent approved frontend's `launch` helper
and the existing shared cancellation/diagnostic utility. Keep the explicit approved
Python/launcher argv, protocol 1 and accepted pin authority. Require the same complete
source/bundle resource closure; import no target code. Install cancellation handlers
through relay cleanup and diagnostic delivery. Return 1 for an observed core failure,
otherwise 2 for interrupted/unverified relay work. The external shim already enters
its corrected bootstrap in the same process and adds no second subprocess relay.

Acceptance adds direct simple-shim source and actual-bundle checks: SIGTERM and
SIGINT for active work without a known failure and naturally completed nonzero work,
current invocation interruption evidence, exit 2/1, stopped benign owned descendants,
explicit pin/protocol refusal and missing-resource refusal. Use finite owned gates
and read-only process observations; no forced PID reuse or unrelated signals. The
runtime S archives remain byte-identical; only adapter source/tests/docs change.
Build a separately named adapter candidate from a new reviewed source commit,
verify its closure/core pins and run the affected bundle checks. Re-review fixes
before the final integration proposal; no main action follows from this correction.

The independent inspection-only amendment critique accepted reuse of the shared
relay before code. It required incomplete/exit 2 for missing closure rather than an
import traceback/exit 1, normal 0/1/2 preservation, failure precedence through
cleanup/diagnostics, no raw signaling, and actual source/bundle-layout coverage.
It accepted a new adapter source containing this correction while runtime S stays
unchanged. The earlier metadata-only S2 description applies only to the held bundle.

Source review additionally required preservation of caller-relative approved paths.
The shim resolves interpreter/launcher explicitly before delegation, refuses an
unavailable interpreter path, and supplies its original caller directory to the
shared relay. That optional relay parameter leaves the context frontend's existing
approved working directory unchanged. Relative target/cache/state/review inputs
retain their prior caller meaning. A separate-cwd fixture checks this behavior.
