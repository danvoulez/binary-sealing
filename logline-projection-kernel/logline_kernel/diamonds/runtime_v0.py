"""diamond.runtime.v0 — runtime lifecycle vocabularies over logline.receipt.v0.

THE HONESTY CLAUSE (from the spec, non-negotiable):
    Runtime claims are attestations, not computation-verifiable facts.
    They require receipt-backed trust anchors and may be superseded.

This module checks that runtime claims are well-formed, receipt-backed,
and chained. It cannot and does not check that they are TRUE — quote
verification and firewall enforcement live outside the canon, on trust
anchors that can fail and be superseded.

KINDS mirrors LogLine-Foundation/conformance/vocabularies/
diamond.runtime.v0.json; the test suite cross-checks the two.
"""
from __future__ import annotations

from logline_kernel.diamonds import receipts_v0, vocabulary

VOCABULARY_VERSION = "diamond.runtime.v0"
STATUS = "executed"

KINDS = {
    "attestation": {
        "did": "attested_runtime",
        "this": "hex64",
        "required_aux": {"trust_anchor": "string", "quote_digest": "hex64"},
        "optional_aux": {"expires": "string", "measurement_log_digest": "hex64"},
    },
    "invocation": {
        "did": "invoked_diamond",
        "this": "hex64",
        "required_aux": {
            "capability_receipt_id": "hex64",
            "attestation_receipt_id": "hex64",
            "mode": "enum:query|train|eval|attest",
        },
        "optional_aux": {"input_digest": "hex64", "limits": "object"},
    },
    "output": {
        "did": "released_output",
        "this": "hex64",
        "required_aux": {
            "invocation_receipt_id": "hex64",
            "output_digest": "hex64",
            "output_class": "enum:model_delta|score|answer|attestation|receipt",
            "firewall_policy_hash": "hex64",
        },
        "optional_aux": {"output_length": "number"},
    },
    "refusal": {
        "did": "refused_invocation",
        "this": "hex64",
        "required_aux": {"reason": "string"},
        "optional_aux": {
            "capability_receipt_id": "hex64",
            "attestation_receipt_id": "hex64",
        },
    },
}

DID_TO_KIND = {spec["did"]: kind for kind, spec in KINDS.items()}


def emit_runtime_receipt(
    kind: str,
    who: str,
    this: str,
    aux: dict,
    when: str | None = None,
    confirmed_by: str = "",
) -> dict:
    return vocabulary.emit(kind, KINDS, STATUS, who, this, aux, when, confirmed_by)


def runtime_receipt_problems(receipt) -> list[str]:
    return vocabulary.vocabulary_problems(receipt, KINDS, STATUS)


# ------------------------------------------------------------ chain rules

def _resolve(ledger_index: dict, receipt_id: str, expected_did: str,
             problems_fn, link_name: str) -> tuple[dict | None, list[str]]:
    target = ledger_index.get(receipt_id)
    if target is None:
        return None, [f"{link_name}: receipt {receipt_id} not found in ledger"]
    if target.get("did") != expected_did:
        return None, [
            f"{link_name}: receipt {receipt_id} has did {target.get('did')!r}, "
            f"expected {expected_did!r}"
        ]
    problems = problems_fn(target)
    if problems:
        return None, [f"{link_name}: receipt {receipt_id} is not conformant: {problems}"]
    return target, []


def verify_output_chain(output_receipt: dict, ledger) -> list[str]:
    """Verify the four chain rules for a released output.

    A passing chain means the provenance CLAIMS are well-formed, linked,
    and unsuperseded. It does not prove the runtime behaved — that rests
    on the trust anchors named in the attestation (honesty clause).
    """
    problems = runtime_receipt_problems(output_receipt)
    if problems:
        return [f"output: {p}" for p in problems]
    if DID_TO_KIND[output_receipt["did"]] != "output":
        return ["output: not an output receipt"]

    ledger_list = list(ledger)
    index = {r["id"]: r for r in ledger_list if isinstance(r, dict) and "id" in r}

    # Rule 1: links resolve to conformant receipts of the expected kind
    invocation, errs = _resolve(
        index, output_receipt["invocation_receipt_id"],
        KINDS["invocation"]["did"], runtime_receipt_problems, "invocation link")
    problems.extend(errs)
    if invocation is None:
        return problems

    attestation, errs = _resolve(
        index, invocation["attestation_receipt_id"],
        KINDS["attestation"]["did"], runtime_receipt_problems, "attestation link")
    problems.extend(errs)

    access, errs = _resolve(
        index, invocation["capability_receipt_id"],
        receipts_v0.KINDS["access"]["did"],
        receipts_v0.diamond_receipt_problems, "capability link")
    problems.extend(errs)

    # Rule 2: one Diamond through the whole chain
    if output_receipt["this"] != invocation["this"]:
        problems.append(
            f"diamond mismatch: output.this {output_receipt['this']} != "
            f"invocation.this {invocation['this']}"
        )
    if access is not None and invocation["this"] != access["this"]:
        problems.append(
            f"diamond mismatch: invocation.this {invocation['this']} != "
            f"access.this {access['this']}"
        )

    # Rule 3: invocation mode must equal the granted mode
    if access is not None and invocation["mode"] != access["mode"]:
        problems.append(
            f"mode mismatch: invocation mode {invocation['mode']!r} not granted "
            f"(access receipt grants {access['mode']!r})"
        )

    # Rule 4: attestation and capability must be active (unsuperseded)
    if attestation is not None and not receipts_v0.is_active_claim(attestation, ledger_list):
        problems.append(
            f"attestation link: receipt {attestation['id']} has been superseded "
            "(trust anchor no longer current)"
        )
    if access is not None and not receipts_v0.is_active_claim(access, ledger_list):
        problems.append(
            f"capability link: receipt {access['id']} has been superseded "
            "(grant no longer current)"
        )

    return problems
