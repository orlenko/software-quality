# One real-executed external fixture

Status: design for independent critique, 2026-11-02. The importer milestone remains
complete. This task qualifies one owned invented subject and one harmless gate;
it does not integrate branches, change frozen tooling or qualify a consumer.

## Problem, acceptance and smaller alternative

Synthetic JSON establishes parser behavior but cannot demonstrate a producer's
actual consumed inputs or a controller's actual deadline/cleanup observations.
The smaller alternative is to retain that synthetic-only/incomplete status. This
increment will run exactly one newly authored canonical gate on invented data,
with natural pass, natural nonzero failure, deadline termination and controller
interruption cases. It succeeds when honestly measured producer/controller bytes
are independently owner-approved and imported through the exact frozen artifact,
owned children are accounted for and cleaned up, and limitations are explicit.
An honest case the frozen importer cannot represent is a concrete block, not
permission to patch it or manufacture an observation.

Frozen engine/package 0.2.0 source is
`70a054bcbc77605d1d4f7c5a2fdc2af30c33705a`, ZIP SHA256
`958a5261f752e523eec74a75ffa3719b1536f966a67db3a482d5e5bd6e9b1cd4`.
Use bootstrap `quality_external_launch.py` SHA256
`e70106e7c7d6027f4b9901eb8e7559ea40e00ef994fa49bf532d7c05ee5b876f`
and `quality_trust.py` SHA256
`8799e4706394735e3dc2dc700fa05c09fe05ab5455cf5b1c0b3f2d7b15487a63`
from that source. There is no working-head, schema, policy, pin or adapter change.

## Single fixture and responsibilities

New owned files: one gate under `fixtures/external-gate/`, one bounded fixture
harness under `tools/`, a small profile describing its mechanism/controls, and
this design/qualification documentation. No dependencies beyond existing isolated
Python 3.11+, Git and stdlib/POSIX. No fixture/controller code, including setup or
self-checks, runs before independent adversarial static review and exact-source
owner approval. Syntax/AST/JSON inspection does not evaluate it. Reviewer identity
confirmation uses non-mutating object/file reads; retain the prior reviewer's
historical Git metadata write in its existing record.

The gate reads one invented JSON input, validates its bounded fields, sums a tiny
integer list and compares its expected sum. It emits a measured intake receipt and
completed stage list; success exits 0 and mismatch naturally exits 7. A declared
blocking input sleeps for a small fixed finite interval before computation, solely
to exercise external supervision. Gate source remains identical across cases;
committed input selects expected result/blocking. It launches no children, reads
only its own script/input and approved runtime facts, and uses no service/network.
These are reviewed procedural properties, not OS path/network/read-only isolation.

The fixture owner creates a new private disposable root outside the toolkit and
all existing targets. Its peer directories contain approved frozen bytes, copied
approved harness/profile/gate, and each case's subject, cache, state, handoff,
producer captured frames/output and controller observations. Raw evidence stays there,
ignored/outside Git. Never write to a consumer, user configuration, private source,
credentials or unrelated process. No global install or application operation.
Normal scoped commits/pushes contain only deliberately authored public code and
sanitized generic results; no raw local paths/transcripts/logs enter the repository.

The setup role creates one plain invented Git subject with four case commits of the reviewed
gate, case input, schema 2 registry and frozen lock; uses invented Git identity and
neutralized environment/hooks/configuration; installs the approved ZIP into that
case's disposable cache and runs the frozen outside-target doctor. For each case it selects only that owner-approved commit in this disposable
subject before doctor, then saves the actual issued handoff unchanged. The owner then inspects the resulting source,
head/profile/command identities and records exact-head trust approval before any
gate execution. Doctor/import never dispatch the gate.

The producer is a separate process using the reviewed harness's producer role.
It measures start after receiving the issued handoff, inspects accepted base/head
and current metadata through frozen owned Git/subject helpers, reads the exact gate/input blobs from the observed commit into one bounded
serialized frame, and launches the reviewed loader with an isolated interpreter
and literal arguments. The child hashes the actual captured source/input, verifies
the approved gate hash, compiles those exact bytes and invokes the gate function
on captured input. Its measured compiled origin is logical `git:<H>:gate.py`; no
first-party filesystem import or installed-module provenance is claimed.
The gate actually parses captured input and reports intake before its deliberate
blocking point; the loader reports captured bytes and runtime/origin facts. The producer matches
those facts to the committed blobs, tree and approved runtime profile; it observes
the actual child wait result, completed stage IDs, source stability and end clocks.
Unknown/missing facts remain unknown/incomplete rather than being copied from the
expected profile. No claimed whole coverage on a terminated/partial operation.

The controller is a separate parent process, running the controller role of the
same reviewed harness under the fixture owner's authority. It starts observation
before producer launch, sets an actual finite wall/monotonic deadline and launches
the producer in a new owned session/process group. The gate inherits that group.
The controller observes its real child lifecycle and owns timeout/cancellation,
SIGTERM/SIGKILL escalation and bounded waits. It records actual deadline, termination,
wait and cleanup facts independently of the producer's result construction.

## Mechanism, identity and evidence channels

Registry canonical identity is the exact gate source hash; whole coverage identifies
its complete fixed parse/sum/compare stage list. An serialized-inputs mechanism
profile binds the reviewed harness/gate bytes, captured Git blobs, actual intake hashes,
logical compiled origin and exact runtime/environment observation. Endpoint stability
is supporting evidence only; consumed data and origin need actual gate observations.
Runtime facts include the approved existing interpreter identity, isolated/no-site
flags, version and explicit child environment; no editable imports/dependencies.
The approved registry environment digest is independently established as an expected runtime/environment specification at setup and
must match actually observed gate facts. A missing intake cannot be reconstructed
from expected values after timeout/interruption.

Each case has a real immutable head and a separately issued challenge. The producer
uses the exact observed context before/after; no restamping a result onto a later
plan. Source/profile identities and commands are durably approved before execution.
Producer and controller evidence are separate, bounded files and raw channels;
the owner separately inspects/approves their measured bytes and SHA256 values via
the existing trusted orchestration session before invoking the frozen importer.
The producer does not approve or generate controller observations. Controller IDs,
shared ownership and JSON are not authentication or enforced independence. This
route is trusted reviewed fixture code under owner control, not a hostile-producer
or independent reviewer security boundary.

Registry permits exact owner-designated trusted-local fixture heads. Required
controls are only deadline and cleanup, actually supplied by process supervision.
Do not register/claim containment, filesystem/read-only/path/tool/network/disclosure,
privacy or reviewer independence enforcement that is absent. Such consumer axes
are outside this fixture's adopted one-gate obligation and remain unqualified; a
separate unsupported-required case may show incomplete, without pretending to run
that obligation. No policy waiver or consumer completeness claim follows.

## Clocks, budget, cancellation and failure

Use the frozen same-host/boot wall+monotonic clock primitive. Start strictly after
issuance with the supported 1 ms precision margin. Controller observation brackets
producer start/finish and cleanup on both clocks, ending only after a measured
precision margin. Default budget 3 seconds, cleanup grace 1 second, import window 60
seconds; case inputs block at most 10 seconds as a last finite fallback. Deadline
starts before producer launch, never gets extended on progress or import, and is
actually enforced by the controller's monotonic wait loop. No long consumer gate
fit is inferred. Clock relationships outside the frozen model remain incomplete.

Only signal the producer group created by this controller. While its direct child
is unreaped, its leader ID cannot be reused; never signal a group after reaping its
leader. The reviewed producer handles termination by accounting for/reaping its
own gate, writing only genuinely measured partial/result facts and exiting. The
controller escalates while it still owns the unreaped leader, then reaps it and
checks for remaining group members without signaling a possibly reused identity.
Unexpected death or uncertain group identity/cleanup is a concrete incomplete/block,
not permission to kill an unrelated process. No broad process search or app restart.

For controller interruption, an owner-approved direct-parent driver sends a real
SIGINT to its recorded unreaped controller child after READY follows actual gate
intake. A missing READY/premature exit stops without signaling a stale PID. Its handler requests
cancellation; normal bounded cleanup still runs and writes honest observations.
No hard-kill resilience or OS containment is claimed. Root cancellation uses the
same finite cleanup, and any remaining owned child is an explicit block.

Expected natural complete success can pass this narrow adopted fixture registry;
natural mismatch fails. Timeout and controller interruption are terminated/incomplete,
with actual partial coverage/cleanup facts. Missing output/intake or an unrepresentable
controller record is incomplete/block. Never fabricate measured completion times,
consumed facts, whole coverage or enforced controls to satisfy the parser.

## Verification and critique

Before execution: independent design critique/dispositions, independent adversarial
static source/fix review, exact public tree/blob/profile/command identities and
durable owner approval. Then execute only approved bytes/commands, collect actual
local result/observation/log references, approve actual receipt digests and import
through frozen tooling. Check every owned PID/group is finished, verify all frozen
hashes/old refs remain unchanged, and publish sanitized measured summaries/limitations.
No unaffected old test suite is rerun for counts. Relevant fixture fixes require
re-review and new exact-source approval before another execution.

Independent inspection-only critique accepted the revised serialized-input
architecture and direct-parent SIGINT driver, with these required invariants, all
accepted: captured bytes are distinct from completed intake/stages; logical compiled
origin is not installed-module provenance; keep leaders unreaped until final signals
(including implicit Popen reaping); establish actual gate/descendant cleanup; preserve
real late termination clocks and missing facts; shared-owner role separation is not
OS independence. Profile/environment identities stay independent of eventual H;
case identity binds through actual context/intake. Static source/fix review and
owner approval still precede all execution. No architectural blocker remains.
