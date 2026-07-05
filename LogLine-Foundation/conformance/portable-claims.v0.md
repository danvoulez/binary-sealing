# portable-claims.v0

The invariant that keeps a Diamond shell from becoming marketing JSON:

```text
A Diamond is portable only if every portable claim is either:
  content-addressed,
  receipt-backed,
  rights-scoped,
  or explicitly marked as unverified.
```

This note makes that invariant machine-checkable. It is **field-aware**
(see `identity-registers.v0.md`): the classifier operates on the fields a
profile declares, never on raw strings.

## The five bins

Every field of a portable shell (a `sealed-binary.v0` manifest) must fall
into exactly one bin:

```text
content-addressed   the value IS or COMMITS TO content by hash/digest
                    (payload, source_commitments, process_contract_hash,
                     compiler_hash)

receipt-backed      the value references receipts that close claims
                    (receipts[] — bare 64-hex receipt ids)

rights-scoped       the value binds use to a rights/custody policy
                    (rights_policy_hash, custody_policy_hash)

structural          profile-pinned vocabulary that shapes the object
                    itself and is covered by the manifest's own JCS hash
                    (seal_version, kind, json_canonicalization,
                     payload.algorithm, payload.length,
                     payload.container_profile,
                     source_commitments.algorithm, leaf_count)

unverified          free claims, quarantined under the top-level
                    "unverified" object. Anything may live there.
                    Nothing there may be presented as verified.
```

`structural` exists because the four claim bins classify *claims*, and
structural vocabulary is not a claim — it is part of the addressed content.
It cannot smuggle assertions: it is enumerated per profile, and anything
not enumerated is not structural.

## The failure rule

```text
A top-level field that fits no bin is an UNCLASSIFIABLE PORTABLE CLAIM,
and classification MUST fail.
```

"10x better than baseline", "enterprise-grade privacy",
"trusted by leading labs" — as top-level manifest fields these fail
classification. Inside `unverified` they are permitted and permanently
labeled as what they are.

## Portability

A shell with an empty `receipts` array is a valid **identity object** —
it names an artifact exactly (`sealed-binary.v0` already says it
"identifies an artifact; legitimates nothing"). But it is **not portable**:

```text
portable shell:
  classification passes, AND
  receipts[] references at least one receipt
  (a compilation receipt at minimum — provenance travels with the object)
```

Identity may travel bare; *claims* may not travel without receipts.

## Reference implementation

`logline-projection-kernel/logline_kernel/diamonds/shell_v0.py` implements
the classifier and the sealed-binary verification (payload digest, Merkle
root recomputation, diamond_id binding). Vectors live in
`vectors/sealed-binary/valid` and `vectors/sealed-binary/invalid`; each
vector bundles the manifest with the payload bytes (hex) and source
strings needed to verify the binary layer end to end.
