"""diamond.receipts.v0 — Diamond lifecycle vocabularies over logline.receipt.v0.

These are not new object types. Every diamond receipt is a plain canon
receipt with a constrained vocabulary: fixed `did` per kind, status
"executed", bare 64-hex `this`, and a pinned AUX schema.

KINDS mirrors LogLine-Foundation/conformance/vocabularies/
diamond.receipts.v0.json — the single source of truth. The test suite
cross-checks the two, so they cannot drift.
"""
from __future__ import annotations

from logline_kernel.diamonds import vocabulary

VOCABULARY_VERSION = "diamond.receipts.v0"
STATUS = "executed"

KINDS = {
    "custody": {
        "did": "accepted_custody",
        "this": "hex64",
        "required_aux": {"custody_policy_hash": "hex64"},
        "optional_aux": {"diamond_id": "hex64", "location": "string", "terms_hash": "hex64"},
    },
    "compilation": {
        "did": "compiled_diamond",
        "this": "hex64",
        "required_aux": {
            "compiler_hash": "hex64",
            "process_contract_hash": "hex64",
            "payload_digest": "hex64",
            "source_merkle_root": "hex64",
        },
        "optional_aux": {"container_profile": "string"},
    },
    "evaluation": {
        "did": "measured_effect",
        "this": "hex64",
        "required_aux": {
            "baseline_score": "number",
            "trained_score": "number",
            "improvement_delta": "number",
            "target_tasks": "string",
            "evaluator": "string",
        },
        "optional_aux": {"benchmark_hash": "hex64"},
    },
    "privacy": {
        "did": "bounded_leakage",
        "this": "hex64",
        "required_aux": {"privacy_mode": "enum:dp|empirical"},
        "conditional_aux": {
            "privacy_mode": {
                "dp": {"epsilon": "number"},
                "empirical": {"attack_suite": "string", "attack_budget": "string"},
            }
        },
        "optional_aux": {
            "memorization_score": "number",
            "membership_inference_risk": "number",
            "canary_recovery_score": "number",
        },
    },
    "access": {
        "did": "granted_access",
        "this": "hex64",
        "required_aux": {
            "grantee": "string",
            "mode": "enum:query|train|eval|attest|transfer",
            "rights_policy_hash": "hex64",
        },
        "optional_aux": {"limits": "object", "expires": "string"},
    },
    "supersession": {
        "did": "superseded_claim",
        "this": "hex64",
        "required_aux": {"diamond_id": "hex64", "reason": "string"},
        "optional_aux": {"successor_receipt_id": "hex64"},
    },
}

DID_TO_KIND = {spec["did"]: kind for kind, spec in KINDS.items()}


def emit_diamond_receipt(
    kind: str,
    who: str,
    this: str,
    aux: dict,
    when: str | None = None,
    confirmed_by: str = "",
) -> dict:
    """Emit a conformant diamond receipt of the given kind.

    Raises ValueError if the result would violate the vocabulary — a
    diamond receipt is never emitted half-conformant.
    """
    return vocabulary.emit(kind, KINDS, STATUS, who, this, aux, when, confirmed_by)


def diamond_receipt_problems(receipt) -> list[str]:
    """Full vocabulary conformance check. Empty list means conformant.

    Layer 1: the receipt must be a conformant logline.receipt.v0.
    Layer 2: it must satisfy its kind's vocabulary.
    """
    return vocabulary.vocabulary_problems(receipt, KINDS, STATUS)


def is_active_claim(receipt: dict, ledger_receipts) -> bool:
    """Resolution rule: a claim receipt is active only while no conformant
    supersession receipt points at its id."""
    target = receipt.get("id")
    for other in ledger_receipts:
        if (
            other.get("did") == KINDS["supersession"]["did"]
            and other.get("this") == target
            and not diamond_receipt_problems(other)
        ):
            return False
    return True
