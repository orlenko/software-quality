# Bounded source review through a tool-free reviewer

Status: accepted for implementation after independent design critique. This is a separate source-only
controller candidate, not a release, consumer install or accepted attestation.

Problem: recorded-v1 validates externally supplied reviewer evidence but cannot
enforce a native coding agent's tools. A broad read-only shell still reads host
files. An instructed reviewer persona does not implement the required boundary.

Smallest alternative: keep manual reviews incomplete. Instead, use the installed
OpenAI Responses API as a **text-only inference transport**, sending `tools: []`.
A small trusted Python parent handles a bounded JSON conversation:
`source-read`, `diff-read`, or `finish`. Only the parent reads immutable Git blobs;
it never interprets model text as code, commands, paths on disk or network URLs.
No SDK, credential provisioning, dependency or new generic sandbox is proposed.

Consultant owns new `reviewers/source_review.py`, its dedicated tests and docs on
an isolated branch. Stagerman retains source integration. Existing core, schema,
recorded-v1 importer, artifact bytes and consumer configurations remain unchanged.

The caller explicitly selects public-source disclosure, exact base/head commits,
approved relative regular-file paths, context JSON from its trusted review
process, an explicit model, and accepted-base rubric paths.
All changed paths must be included. The parent resolves immutable regular Git
blobs only, rejects symlinks/submodules/binary/oversize data and path traversal,
and derives per-file diffs in memory. It does not export or execute the target.
Source context is checked against actual commits/trees. Optional full recorded-v1
context is additionally checked against accepted base config/lock bytes and pins;
a bootstrap source-only witness carries `review_context: null`, never invented
config hashes. Rubrics always come from explicitly approved base blobs.

Each model turn is a fresh HTTPS request to the fixed Responses endpoint, with
`tools: []`, `store: false`, bounded output and no previous response/session.
There is no CLI, shell, plugin, MCP server, browser, hook or target-code runtime.
The parent attaches only explicitly approved immutable source and rubric text;
all model JSON requests are data. An existing API key is read from the environment
only for the transport's authorization header and never enters prompts, target
code, witnesses or diagnostics. No model fallback, environment proxy, redirect,
automatic retry or arbitrary endpoint is supported. This provider connection is
explicit inference disclosure, not reviewer-tool network access. A provider tool
call, unknown action, invalid output, HTTP failure, timeout, byte/turn limit or
source mismatch produces incomplete evidence and never a positive review.
The trusted controller/interpreter/OS and provider authentication remain the
trust base; this does not sandbox a malicious controller or administrator.

Output is a context-bound controller witness and findings, **not** an automatic
`independent: true` or recorded-v1 pass. It binds controller identity, actual fresh
response/model metadata, source/rubric payload and transcript digests, sent empty
tools and dispatched read operations. The owner's external trusted process must
still approve the reviewer identity, actual independence, provenance and exact
context before translating/importing a recorded-v1 response. No synthetic fixture
or historical review can supply that authorization.

Checks: invented Git repositories; dirty/ignored files never disclosed; traversal,
symlink/gitlink/binary/oversize refusals; full changed-path coverage; stale context;
malformed/extra actions; unavailable tools; final without required source/diff
reads; timeout/HTTP error; exact HTTPS endpoint/auth/payload/empty-tools assertions
against a fake standard-library connection with invented credentials. These
tests establish controller dispatch/protocol behavior, not provider availability,
review accuracy or a live authenticated review. No live provider, private source,
consumer tests or account mutation in these checks. A real provider run requires
its own explicit public-source/model/account approval; building this PR does not
activate it. The installed-CLI alternative was rejected because disabling tools
does not independently remove managed hooks/settings and their capabilities.

Independent critique: `reviewer_controller_design` reviewed the revised written
proposal before code. Accepted all six findings: allow honestly labelled bootstrap
source context; bind rubric authority to base blobs; fixed tool-free transport;
cover deletions/additions/mode changes and refuse uncovered changed paths; keep
identity/independence/API approval external; bound source/transcript/actions/time.
The smaller direct HTTPS route replaces the CLI idea. No finding was waived.
This native advisory review is not itself an enforced controller witness.
