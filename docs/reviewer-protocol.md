# Recorded independent reviewer protocol v1

This is a trusted external attestation interface, not a reviewer launcher or
permission sandbox. [README](../README.md) explains the plan/review/check sequence.
All policy comes from accepted base, including stronger local routes. Obtain the
response and expected digest through the owner's trusted review process, outside
target control. Valid JSON or a digest alone cannot authenticate a PR attachment.

The [envelope](../quality/schemas/review.json) contains `schema_version: 1`,
`protocol: recorded-v1`, the exact `context` emitted by `doctor`, and `reviews`.
Copy every repository/base/head/tree/config/lock/artifact/toolkit/policy/schema
identity exactly. Each [record](../quality/schemas/review-record.json) contains:

- `route_id` and `reviewer_id`: exact identities from accepted configuration.
- `independent: true`: an external assertion, not inferred from a name.
- `boundary`: actual attested read-only/enforced path/tool/network/disclosure scope,
  matching accepted authorization. Paths are `tracked-source`, tools are only
  source/diff inspection; private media is outside this scope.
- `findings`: unique IDs, severity `blocker` or `improvement`, disposition `open`
  or `resolved`, location, reachable scenario, consequence, recommendation, and a
  nonempty resolution for resolved findings.
- `summary`: explanation that never overrides findings or completeness.

Each existing required route needs a record. The route must actually enforce its
permissions; if unavailable, omit/invalidate it and retain incomplete evidence.
The runner labels accepted records `evidence_kind: external-attestation`, separately
from mechanically observed command results. It cannot prove identity/independence
from strings; where required, accepted configuration rejects equal identity strings
and the owner establishes actual independence. No provider fallback, upload, media
viewer or private-artifact access is authorized by this format.

The operator passes the outside-target/toolkit response and approved digest. The
runner opens once without following a final symlink, bounds the bytes, and hashes
and parses the same bytes. Invalid common context makes the envelope unbound and
incomplete. Each route is then validated independently: missing/stale/invalid or
duplicate records are incomplete, unknown extras add incomplete evidence, and a
valid open blocker still causes failure. Duplicates never choose the last result.
Resolved blockers need recorded disposition evidence; the external reviewer remains
responsible for validating it against the bound target.

No attestation signing, provider authentication, automatic adjudication, quality
inference or blocker waiver is implemented. Existing owner/adjudicator and accepted
rubric remain authoritative.
