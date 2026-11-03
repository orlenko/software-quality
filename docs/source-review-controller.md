# Source review controller candidate

`reviewers/source_review.py` addresses the tool-permission gap in native agent
reviews. It is a separate source-only candidate, outside the existing artifacts.
No consumer is installed, enabled or adopted by this code. The existing
[recorded-v1 protocol](reviewer-protocol.md) remains an external attestation route.

The model receives text with **no provider tools**. A trusted Python controller
interprets three strict JSON actions: `source-read`, `diff-read`, `finish`.
Reads select only preloaded immutable regular Git blobs from an explicit approved
list. Diffs include base/head modes and blob identities, additions and deletions.
Neither model text nor source content becomes a command, host path or URL.
The controller's fixed HTTPS inference connection is disclosed separately from
reviewer-tool network access, which is unavailable. The interpreter, controller,
its trusted helper/schema closure, Git, OS, TLS and provider are trusted components;
this is not a sandbox for a malicious controller or machine administrator.

Before a live invocation the owner must explicitly approve the exact public
source selection, base rubric, model and API account/spend. A key being present
does not grant that permission. The CLI refuses without
`--approve-public-source-api`; do not add this switch as a routine default.
There is no CLI-auth token extraction, new account, automatic provider/model
fallback, proxy/redirect support, retry, upload API, browser, shell, MCP or plugin.
API authentication uses only `OPENAI_API_KEY` for its authorization header.

Prepare a trusted request **outside the consumer and toolkit trees**, approve its
exact bytes and SHA-256 independently of target authors, and select a new output
directory outside those trees. This shape uses placeholders, not runnable pins:

```json
{
  "source": {
    "repository": "example/demo",
    "base": "FULL_BASE_COMMIT_ID",
    "head": "FULL_HEAD_COMMIT_ID",
    "base_tree": "FULL_BASE_TREE_ID",
    "head_tree": "FULL_HEAD_TREE_ID"
  },
  "review_context": null,
  "paths": ["AGENTS.md", "src/example.py"],
  "rubric_paths": ["AGENTS.md"],
  "stage": "finished",
  "model": "operator-approved-exact-model-id"
}
```

Every changed path must be included, including deletions and mode changes.
Rubric paths must be included and resolve to approved **base** blobs. Changed
instructions cannot choose their own review rules. Bootstrap rubric approval is
an owner responsibility. Git commits and trees are checked against actual objects;
dirty, ignored and untracked working-tree bytes are not read. Symlinks, gitlinks,
binary/non-UTF8 blobs and unsupported/oversize selections refuse before inference.

For an accepted consumer, replace `review_context: null` with the full exact
recorded-v1 context from the trusted review process. Also approve the base
`.quality/config.json`, `.quality/lock.json` and every referenced rubric path in
the selection. The controller validates context fields, base config/lock digests,
repository identity and artifact/toolkit/policy pins. It does not authenticate
those approvals or verify the installed artifact. A bootstrap proposal without an
accepted config instead retains a source-only witness and **null** review context.

After the separately granted live-source/model/account approval:

```sh
python3 -I -S /approved/toolkit/reviewers/source_review.py \
  --repo /approved/consumer \
  --request /approved/private/request.json \
  --request-sha256 APPROVED_REQUEST_SHA256 \
  --output /approved/private/new-review-directory \
  --approve-public-source-api
```

No target tests or imports execute. Selection limits are 256 paths, 64 KiB per
blob, 512 KiB total base/head source, 1 MiB transcript and 128 KiB per response.
At most 24 inference turns are attempted; every changed path needs a diff plus
source read, followed by a finish. The overall observation budget is 300 seconds;
HTTPS I/O has a 30-second timeout. These checks do not promise hard real-time
cancellation of OS/TLS calls. Each turn resends bounded text without a previous
response ID; this can cost more than a persisted conversation. `store: false`
requests no stored response state; it is not a claim about provider retention.
The exact returned model must match the requested identifier; aliases resolving
to a different model string refuse rather than silently changing the model.

`witness.json` begins incomplete. A successful exit means only that the bounded
source review conversation completed and its findings were recorded. An open
blocker remains in the findings; completion does not mean approval. Missing
inspection, malformed/unknown actions, any provider tool-call item, refusal,
non-completed response, model mismatch, HTTP/timeout/byte/turn error or interruption
leaves incomplete evidence. Raw HTTP bodies, keys and source transcripts are not
written into the witness or diagnostics. Keep witnesses private unless their
actual contents have received publication review.

The witness binds source, optional review context, request/controller/rubric and
transcript digests, provider response/model identifiers and actual dispatched
reads. It is **not** an authenticated reviewer identity, proof of independence,
signed record, recorded-v1 response or toolkit verdict. The owner's trusted
external process must approve identity, independence, provenance and exact
context before manually commissioning any recorded-v1 attestation. There is no
automatic converter that can turn a test fixture or this witness into a pass.

Offline verification uses invented Git repositories and a fake standard-library
HTTPS connection; it never reads a real key or invokes a provider:

```sh
python3 -I -S -c 'import sys, unittest; sys.path.insert(0,"."); unittest.main(module="tests.test_source_review", verbosity=2)'
```

Those tests establish implementation behavior, not live provider availability or
review accuracy. Live public-source qualification, source integration, release
packaging and consumer acceptance remain separate work.

Protocol references: [OpenAI text generation](https://developers.openai.com/api/docs/guides/text),
[tools](https://developers.openai.com/api/docs/guides/tools), and
[conversation state](https://developers.openai.com/api/docs/guides/conversation-state).
