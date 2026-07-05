# identity-registers.v0

Not every hash-like string is the same kind of object. The formal
foundations already separate content identity from legitimacy; this note
separates the **registers** an identifier can live in, so engines neither
under-canonize (prefixed strings leaking into canon objects) nor
over-canonize (every internal label forced to become a Receipt).

## The five registers

```text
1. canon semantic identity
   bare 64-hex content_hash; id == content_hash
   examples: receipt id, act content hash, diamond_id

2. transport identity
   envelope_hash; lives ONLY on the Envelope wrapper,
   computed at boundaries, never stored on resting objects

3. binary payload identity
   raw byte digest (sealed-binary.v0); identifies exact bytes,
   legitimated by receipts, never by recompute

4. engine-local reference
   prefixed identifier (e.g. "lens:", "seal-context:", "anchor-package:");
   valid inside one engine's own storage and logs; explicitly non-canon

5. human display label
   any prefix or formatting for reading;
   derived at render time, never stored as a semantic id
```

## The boundary rule

A register is not a naming convention. It is defined by **where the
identifier may travel**:

```text
An identifier's register is determined by the objects it may appear in.
The moment an engine-local reference appears inside a canon object
(a receipt, a manifest, a canon vector), it is in the wrong register,
and conformance MUST fail.
```

Consequences:

- Canon objects (receipts, manifests, canon vectors) contain only
  register-1/2/3 identifiers: bare 64-hex hashes and declared byte digests.
  A prefixed id inside a canon object is a conformance violation.
- Engine-local prefixed references are **legitimate** — they do not need to
  become canon Acts or Receipts. They must simply never cross the boundary.
  Nothing has to convert until it travels.
- Engine vectors (e.g. the projection kernel's `vectors/`) may contain
  prefixed ids: they are register-4 artifacts proving engine behavior, not
  canon vectors. They are governed, not condemned.
- Display prefixes (`receipt:`, `diamond:` shown to a human) are fine as
  formatting. Storing them is the violation, because stored prefixes
  eventually get compared, hashed, or shipped.

## Why this is not over-canonization

The alternative doctrine — "everything must become a receipt" — is wrong
for the same reason "every file hash is truth" is wrong. The Foundation
formalism says hashes prove content identity, while legitimacy comes from
admission, receipts, authority, evidence, and scope. Registers apply the
same discipline to identifiers themselves: an engine's working reference
has engine scope, and forcing it into canon would launder engine internals
into semantic authority.

## Conformance

- A receipt or manifest field expected to be a semantic address MUST match
  `^[0-9a-f]{64}$`. Prefixed values fail.
- Envelope hashes MUST NOT appear inside resting receipts (already enforced
  by `logline.receipt.v0`).
- Payload digests MUST be declared with their algorithm and byte length
  (`sealed-binary.v0`).
- Engines SHOULD document which of their identifiers are register-4, as the
  projection kernel does in `GOVERNANCE.md`.
