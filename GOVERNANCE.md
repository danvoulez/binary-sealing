# Governance of this repository

This repo is a **crossing workspace**: several artifacts from different
moments of the LogLine program live side by side. This file states which
governs which, so the hierarchy is explicit instead of implied.

## The hierarchy

```text
canon defines · conformance proves · engine implements · governance evolves
```

| artifact | role | authority |
|---|---|---|
| `LogLine-Foundation/canon/` | **The current, official canon.** | Governs everything below. |
| `LogLine-Foundation/conformance/` | Proof machinery: schemas, vectors, hash profiles, reference verifier. | Source of truth for conformance. Engines import these vectors; they never fork them. |
| `logline-projection-kernel/` | An **engine**. Originally built against the 0.2.0-draft canon; its canon-facing layer (Act identity, Receipts, Envelopes, JCS hashing) is now aligned to `logline.receipt.v0` and tested directly against the Foundation vectors. | Subordinate to the Foundation. Where kernel behavior and canon disagree, the canon wins and the kernel is wrong. |
| `Crossing 3 Things.md`, `10_FORMAL_FOUNDATIONS_OF_LOGLINE 2.md`, `who, did, this…md` | Source material: the formal foundations text and the conversations that produced the Diamond/binary-sealing direction. | Input to canon evolution, not law. |

## Kernel alignment status

Aligned to the current canon:

- **JCS hashing** (`core/hashing.py`) — conformant RFC 8785, verified against
  the Foundation worked example and vectors.
- **Receipts** (`core/receipt_v0.py`, `core/receipts.py`) — canon
  `logline.receipt.v0`: nine slots, tuple/content hashes,
  `id == content_hash`, AUX as free top-level fields, legacy
  result/evidence/transport forbidden.
- **Envelopes** (`core/receipt_v0.py`) — transport wrapper with
  `envelope_hash`, computed at boundaries, never stored on resting receipts.
- **Act identity** (`acts/act.py`) — bare 64-hex content-hash ids, canon
  content body (slots + top-level AUX), `tuple_hash` exposed.
- **Conformance coupling** (`tests/test_receipt_v0.py`) — the kernel's test
  suite loads `LogLine-Foundation/conformance/vectors/` directly. Drift now
  fails CI instead of accumulating silently.
- **Diamond receipt vocabularies** (`diamonds/receipts_v0.py`) — the six
  lifecycle receipts (custody, compilation, evaluation, privacy, access,
  supersession) as vocabulary profiles over `logline.receipt.v0`, mirroring
  `conformance/vocabularies/diamond.receipts.v0.json`; the test suite
  cross-checks the two so they cannot drift. Includes the supersession
  resolution rule (`is_active_claim`).

Known **not yet aligned** (engine-internal, pending):

- Prefixed internal references (`lens:`, `seal-context:`, `anchor-package:`,
  `diamond-manifest:` …) across the engines and diamond modules. Per
  `conformance/identity-registers.v0.md` these are **register-4
  (engine-local) identifiers and legitimately so** — they do not need to
  become canon objects. The pending work is only the boundary rule: none of
  them may appear inside a canon object (receipt, manifest, canon vector),
  and any that needs to travel must be re-issued as a bare content hash.
- The flux engine's internal `Act` duplicate (`engines/flux/engine.py`)
  still hashes an old body shape with a `proc:` prefix; it reads canon-flat
  records but does not yet emit canon identities.
- Kernel-local schemas (`schemas/*.json`) predate the Foundation schemas and
  have not been reconciled with them.

## Rule of evolution

Superseded designs are not deleted; they are governed. Anything in the
kernel that contradicts the Foundation is a **superseded engine behavior**:
it keeps working until replaced, but no new code may depend on it, and every
alignment lands with conformance tests wired to the Foundation vectors.
