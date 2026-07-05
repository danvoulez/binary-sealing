# diamond.receipts.v0

Receipt vocabularies for the Diamond lifecycle. **These are not new object
types.** Every diamond receipt is a plain `logline.receipt.v0` — nine slots,
tuple/content hashes, `id == content_hash` — with a constrained vocabulary:
a fixed `did` verb per kind, `status = "executed"`, `this` as a bare 64-hex
semantic address, and a pinned AUX schema.

One canon shape, six vocabularies. Six separate schemas would be six chances
to drift; a vocabulary over the one canon receipt cannot drift from it,
and every valid diamond receipt vector is automatically also a valid
receipt vector.

Machine-readable form: [`diamond.receipts.v0.json`](./diamond.receipts.v0.json)
— the single source of truth. Implementations embed a copy and MUST
cross-check it against this file in their test suites.

## Common rules

```text
status        = "executed"                 (the receipt records an event)
this          = bare 64-hex semantic address (identity-registers.v0, register 1)
confirmed_by  = evidence pivot, free string
when          = ISO-8601 recommended
AUX           = pinned per kind below; extra AUX fields are allowed
                (they are ordinary canon AUX) but never replace required ones
```

Kind detection is by `did`. A `did` outside the six verbs below is simply
not a diamond receipt; a `did` in the vocabulary with missing or mistyped
required AUX is a **vocabulary violation** even when the receipt is
hash-conformant.

## The six kinds

| kind | did | this | required AUX |
|---|---|---|---|
| custody | `accepted_custody` | source Merkle root | `custody_policy_hash` |
| compilation | `compiled_diamond` | payload digest | `compiler_hash`, `process_contract_hash`, `payload_digest`, `source_merkle_root` |
| evaluation | `measured_effect` | payload digest | `baseline_score`, `trained_score`, `improvement_delta` (numbers), `target_tasks`, `evaluator` |
| privacy | `bounded_leakage` | payload digest | `privacy_mode` ∈ `dp` \| `empirical`, plus conditional fields below |
| access | `granted_access` | diamond_id | `grantee`, `mode` ∈ `query`\|`train`\|`eval`\|`attest`\|`transfer`, `rights_policy_hash` |
| supersession | `superseded_claim` | **id of the superseded receipt** | `diamond_id`, `reason` |

### The binding order (cycle rule)

Building the first real sealer surfaced this immediately, so it is now
law. `diamond_id = content_hash(manifest)`, and the manifest embeds the
ids of its pre-sealing receipts. Therefore an embedded receipt **cannot
address the diamond_id** — it would have to contain the hash of a
manifest that contains it. The addressing rule:

```text
receipts embedded IN the manifest address what existed BEFORE sealing:
  custody      -> source Merkle root
  compilation  -> payload digest  (the compiled artifact)
  evaluation   -> payload digest  (what was measured)
  privacy      -> payload digest  (what was attacked)

receipts ABOUT the sealed shell address the diamond_id and live
ONLY in the ledger, after sealing:
  access       -> diamond_id
  supersession -> id of the superseded receipt
```

This is not a workaround; it is the correct semantics. Evaluation and
privacy measure the *artifact* — the same payload digest sealed into the
manifest — not the wrapper. The manifest then binds artifact, sources,
policies, and claims into one content address.

### Privacy conditionals

```text
privacy_mode = "dp"        -> epsilon (number) REQUIRED
privacy_mode = "empirical" -> attack_suite, attack_budget REQUIRED
```

This encodes the doctrine from `sealed-binary.v0`: only differential
privacy yields a formal bound; an empirical claim is scoped to the attack
suite that ran and carries the epistemic status of "no known extraction."

## Supersession — designed first, on purpose

The supersession receipt is what keeps ε honest. Without it, "leakage below
ε under suite A" quietly hardens into an absolute the moment the Diamond
changes hands. With it, a broken claim is not retroactive falsification —
it is recorded evolution: the ledger states exactly what was known when.

```text
who   = the authority superseding the claim
this  = id of the receipt whose claim is being closed
aux.diamond_id            = the Diamond concerned
aux.reason                = why (e.g. "extraction attack published 2027-03")
aux.successor_receipt_id  = optional replacement claim
```

Resolution rule: a claim receipt is **active** only while no conformant
supersession receipt points at its `id`. Resolvers MUST check for
supersession before treating an evaluation or privacy claim as current.
Authority validation (who may supersede whose claims) is a policy/process
concern above this vocabulary and is deliberately not encoded at v0.

## Conformance

A diamond receipt MUST:

1. pass full `logline.receipt.v0` conformance (shape + all hash checks);
2. carry `status = "executed"`;
3. carry a bare 64-hex `this` (no prefixes — identity-registers.v0);
4. satisfy its kind's required AUX fields with the declared types,
   including conditional requirements.

Vectors live in `vectors/diamond-receipts/valid` and
`vectors/diamond-receipts/invalid`. Invalid vectors are deliberately
hash-correct receipts that fail only at the vocabulary layer, proving the
two layers are distinct.
