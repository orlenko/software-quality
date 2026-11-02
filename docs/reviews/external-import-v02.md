# Import-only candidate qualification

Scope: work-branch engine/package `0.2.0`, schema2, protocol2, unchanged policy
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
Policy0.1 is retained because externally attested synthetic candidate facts are
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
   require completion within the observed deadline plus declared1ms precision.
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

On macOS/Darwin27.2.0, Python3.14.7, the final reviewed source suite
`python3 -I -S tools/test_external.py` passed36 tests in55.303s on the staged
reviewed tree above. The four relevant v1-default source regressions also passed
in2.406s: complete reviewed check, interrupted report/lock release, artifact
identity refusal and strict JSON. Subsequent production edits only tightened a
new external-only path helper; v1 default calls do not use it. Old artifact suites
were not rerun. Actual new-package qualification is pending below. Intermediate runs
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
