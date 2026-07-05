# sealed-binary.v0

Hash profile for sealed binary payloads: Diamond bodies, compiled training
artifacts, adapters, deltas, feature shards, eval bundles — anything whose
substance is bytes, not JSON.

Companion to [`jcs-rfc8785`](./jcs-rfc8785.md). JCS answers "how do two
engines hash the same *logical JSON* identically?" This profile answers the
question that begins where JCS ends: "how does a *binary* artifact get a
durable content address, and what does that address prove?"

## Doctrine

JCS exists because JSON has many byte representations of one logical object.
A binary artifact has exactly **one** byte representation. So this profile
defines **no canonicalization layer for payloads**. Byte identity *is*
identity:

```text
payload_digest = sha256(exact payload bytes)
```

The inversion that matters — and the reason this profile exists — is on the
verification side:

> **A sealed binary payload is identified by byte digest and legitimated by
> process receipts. Recompute-verification is not required and not assumed.**

A JSON receipt can in principle be re-derived by anyone from the same
logical input. A compiled training artifact cannot: GPU training is
non-deterministic (atomic operations, kernel scheduling), so byte-identical
recompilation is not achievable in practice. Therefore:

- The **digest** proves you hold exactly the artifact that was sealed.
- The **receipts** (custody, compilation, evaluation, privacy) prove the
  process that produced it — this is where legitimacy lives.
- Any claim of effect (`Δ`) or leakage bound (`ε`) is a **scoped,
  supersedable claim** closed by a Receipt under evidence, authority, and
  scope — never a property of the bytes themselves.

This is the same burden separation the formal foundations already fix for
Acts: hashes prove content identity, not truth, legitimacy, or authority.

## Structure

A sealed binary object is always a **pair**: a JSON manifest and one or more
binary payloads. The manifest is the semantic address; payloads are leaves.

```text
JSON manifest   -> JCS (rfc 8785) + sha256   -> diamond_id / seal_id
binary payload  -> sha256 over exact bytes    -> payload.digest
source set      -> Merkle root over digests   -> source_commitments.merkle_root
receipts        -> content hashes (JCS)       -> receipts[]
```

The manifest MUST embed every payload digest, so the manifest hash
transitively commits to all binary content. `id == content_hash(manifest)`
remains the durable semantic address, exactly as for Acts.

## Rules

1. **Payload digest** is `sha256` over the exact distributed bytes. No
   transformation, normalization, decompression, or re-encoding before
   hashing. If the payload is compressed, the digest covers the compressed
   bytes and the manifest records the encoding.
2. **`length`** (byte count) MUST accompany every payload digest. It is a
   cheap integrity pre-check and removes length-extension ambiguity in logs.
3. **Container profiles** are declared, not assumed. The manifest names the
   payload's container in `container_profile`. Defined values:
   - `raw.bytes.v0` — opaque bytes; no inner structure asserted.
   - `safetensors.sorted.v0` — a safetensors file whose header serializes
     tensor names in lexicographic (code point) order with no insignificant
     whitespace, dtype and shape declared per tensor, little-endian data.
     This pins the *container* so it cannot smuggle nondeterminism, while
     the tensor bytes themselves are sealed as-is.
   New profiles require a canon revision, like any reserved-field change.
4. **Source commitments** use a Merkle tree so membership can later be
   proven selectively (one source, not the whole set) without disclosure:
   - source digest: `sha256(source bytes)` — the raw sources never appear.
   - leaf: `sha256(0x00 || source_digest)` (domain-separated, digest as
     32 raw bytes, not hex).
   - leaves sorted ascending as byte strings, duplicates removed.
   - node: `sha256(0x01 || left || right)`; an odd node is promoted
     unchanged to the next level.
   - `merkle_root` is the root, lowercase hex; `leaf_count` MUST be stated.
   Domain separation (0x00/0x01) prevents leaf/node confusion attacks.
5. **Algorithm agility**: `sha256` is the canon algorithm, matching Acts and
   Receipts. A manifest MAY carry an additional `blake3` digest for large
   payloads (verification speed), but `sha256` MUST be present and is the
   digest of record.
6. **No hidden truth**: possession of bytes matching `payload_digest` proves
   *content identity only*. Utility (`Δ`), leakage (`ε`), rights, and custody
   are claims that MUST cite receipts. A manifest whose `receipts` array is
   empty identifies an artifact; it legitimates nothing.

## Worked example

Payload (8 bytes, hex): `0001020304050607`

```text
payload_digest = 8a851ff82ee7048ad09ec3847f1ddf44944104d2cbd17ef4e3db22c6785a0d45
length         = 8
```

Source set: the strings `source-a`, `source-b`, `source-c` (UTF-8).

```text
sha256(source-a) = 0f9f5ce47831e099e77e295ed8bb627f089efa8672ee6fbdc49eac6f0d7f5275
sha256(source-b) = 3fed13457ee26a4f5b27c42544aa57045981a075a6103aab87e0b81c032e9d01
sha256(source-c) = cac5ad9966bce7cf5e21699ea0944ccae7183c6fe78718391f6679d57023ce81

leaves (sha256(0x00 || digest), sorted):
  0e1cfa5e0e7df1f2fcc572264b45fd5c495e3c6363580e1545616304815fd131
  398a8dc709bcb81c3bf75eea8c2c11e600e2dcbc2686ea23a38134e645adbda5
  e809a2fac4fe2065a97d40fff706ac941861aaedee066c75a92cee4e85097855

merkle_root = 9469af92426bc4ce62e6a20800ab62031aac6ee0be72e2fef4a6692d6e0d75f0
```

Manifest (logical object; process/compiler/rights hashes zeroed for the
vector, `receipts` empty):

```json
{
  "seal_version": "sealed-binary.v0",
  "kind": "compiled_training_diamond.v1",
  "payload": {
    "digest": "8a851ff82ee7048ad09ec3847f1ddf44944104d2cbd17ef4e3db22c6785a0d45",
    "algorithm": "sha256",
    "length": 8,
    "container_profile": "raw.bytes.v0"
  },
  "source_commitments": {
    "merkle_root": "9469af92426bc4ce62e6a20800ab62031aac6ee0be72e2fef4a6692d6e0d75f0",
    "algorithm": "sha256",
    "leaf_count": 3
  },
  "process_contract_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "compiler_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "rights_policy_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "receipts": [],
  "json_canonicalization": "jcs-rfc8785"
}
```

JCS + sha256 of the manifest:

```text
diamond_id = 0167d3b3348a9db022a66392087cbeed2292872238cbc0a992597f3be07c620a
```

Any conformant implementation MUST reproduce all values above exactly.

## Claims: Δ and ε are Receipts, not properties

A Hidden Training Diamond makes two load-bearing claims that no digest can
carry:

```text
utility claim:   trained effect Δ on model M, task family T, vs baseline
leakage claim:   source not retrievable below ε, under attack suite A,
                 within budget B, as of evaluation date
```

Both MUST be expressed as Receipts citing the manifest's `diamond_id`, with
their own evidence, authority, and scope. The leakage claim is **scoped to
the attack suite that was run** — it has the epistemic status of "no known
extraction," not an absolute. When a new attack breaks a previously sealed
ε, the correct canon move is **supersession** of the privacy receipt, not
retroactive falsification: the ledger records exactly what was known when.

Only differential-privacy compilation yields a formal ε against future
attacks; empirical audits (canary recovery, membership inference,
reconstruction probes) bound only what was tested. A manifest SHOULD state
which kind of ε it carries: `privacy_mode: "dp" | "empirical"`.

## Conformance

- A payload digest computed over anything other than the exact distributed
  bytes is a conformance violation.
- A manifest hashed with anything other than JCS (RFC 8785) is a
  conformance violation, exactly as for Receipts.
- A Merkle root computed without the 0x00/0x01 domain separation, or over
  unsorted leaves, is a conformance violation.
- Presenting `payload_digest` possession as proof of utility, rights,
  legitimacy, or non-retrievability is a **doctrine** violation: identity
  is proven by hash; everything else is proven by Receipts.
