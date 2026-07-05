# diamond.runtime.v0

Receipt vocabularies for the runtime lifecycle: attestation, invocation,
output release, refusal. Like `diamond.receipts.v0`, these are vocabulary
profiles over `logline.receipt.v0` — one canon shape, no new object types.

Machine-readable form: [`diamond.runtime.v0.json`](./diamond.runtime.v0.json).

## The honesty clause — read this first

```text
Runtime claims are attestations, not computation-verifiable facts.
They require receipt-backed trust anchors and may be superseded.
```

Every other profile in this repository bottoms out in pure computation:
anyone with the bytes can recheck a JCS hash, a payload digest, a Merkle
root. Runtime claims cannot be rechecked that way. "This ran inside an
attested enclave" and "only the permitted output left" rest on:

```text
vendor attestation roots     (e.g. TEE hardware manufacturers)
quote verification services
firewall policy enforcement inside the runtime
the runtime's own correct implementation
```

These are **trust anchors, not proofs**. A conformant verifier of this
vocabulary checks that the *claims are well-formed, receipt-backed, and
chained* — it cannot and does not check that they are *true*. Anyone
presenting a passing `diamond.runtime.v0` chain as computation-verified
security is overclaiming, and the overclaim is theirs, not the canon's.

Because trust anchors fail (vulnerabilities, revoked keys, broken
firmware), **attestation receipts are first-class supersession targets**:
a `diamond.receipts.v0` supersession receipt pointing at an attestation
receipt's id closes it, and every chain built on it stops resolving as
current. Supersession is cross-vocabulary by design.

## The four kinds

| kind | did | this | required AUX |
|---|---|---|---|
| attestation | `attested_runtime` | runtime profile hash | `trust_anchor` (vocabulary string, e.g. a vendor/scheme name), `quote_digest` |
| invocation | `invoked_diamond` | diamond_id | `capability_receipt_id`, `attestation_receipt_id`, `mode` ∈ `query`\|`train`\|`eval`\|`attest` |
| output | `released_output` | diamond_id | `invocation_receipt_id`, `output_digest`, `output_class` ∈ `model_delta`\|`score`\|`answer`\|`attestation`\|`receipt`, `firewall_policy_hash` |
| refusal | `refused_invocation` | diamond_id | `reason` |

Field-aware note (`identity-registers.v0`): `trust_anchor` is a
**vocabulary string** — `"amd.sev-snp"`, `"intel.tdx"`, `"nvidia.cc"` are
names of trust anchors, not identifiers, and are never register-checked.
`quote_digest` is identity-bearing and must be a bare 64-hex digest of the
actual attestation quote, so the quote itself is content-addressed even
though its verification lives outside the canon.

Refusals emit receipts too. Zero trust means every decision is recorded,
including "no" — a runtime that only receipts its successes is editing
history.

## The chain

```text
attestation (runtime proves itself, per trust anchor)
      ▲
invocation ── capability_receipt_id ──► access receipt (diamond.receipts.v0)
      ▲       attestation_receipt_id ─► attestation receipt (above)
output ────── invocation_receipt_id ──► invocation receipt (above)
```

Chain resolution rules (all machine-checkable):

1. Every link id must resolve in the ledger to a conformant receipt of the
   expected kind.
2. `output.this == invocation.this == access_receipt.this` — one Diamond
   through the whole chain.
3. `invocation.mode` must equal the access receipt's granted `mode`
   (`transfer` grants are not invocable — custody movement is not an
   invocation).
4. The attestation receipt and the access receipt must be **active**: no
   conformant supersession receipt may point at either id.

A broken link anywhere means the output's provenance claim does not hold —
the output may exist, but nothing about its production is established.

## Conformance

Vectors live in `vectors/diamond-runtime/valid` and
`vectors/diamond-runtime/invalid`. As with `diamond.receipts.v0`, invalid
vectors are hash-conformant receipts broken only at the vocabulary layer.
Chain-level failures (dangling links, superseded attestations, mode
mismatches) are exercised in the reference implementation's test suite,
since they require a ledger, not a single object.

Reference implementation:
`logline-projection-kernel/logline_kernel/diamonds/runtime_v0.py`
(`verify_output_chain` implements the four chain rules).
