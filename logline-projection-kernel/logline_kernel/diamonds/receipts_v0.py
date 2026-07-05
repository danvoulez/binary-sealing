"""diamond.receipts.v0 — Diamond lifecycle vocabularies over logline.receipt.v0.

These are not new object types. Every diamond receipt is a plain canon
receipt with a constrained vocabulary: fixed `did` per kind, status
"executed", bare 64-hex `this`, and a pinned AUX schema.

KINDS mirrors LogLine-Foundation/conformance/vocabularies/
diamond.receipts.v0.json — the single source of truth. The test suite
cross-checks the two, so they cannot drift.
"""
from __future__ import annotations

import re

from logline_kernel.core import receipt_v0

VOCABULARY_VERSION = "diamond.receipts.v0"
STATUS = "executed"

_HEX64 = re.compile(r"^[0-9a-f]{64}$")

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


def _type_problems(field: str, value, type_spec: str) -> list[str]:
    if type_spec == "hex64":
        if not isinstance(value, str) or not _HEX64.match(value):
            return [f"aux field {field!r} must be a bare 64-hex hash"]
    elif type_spec == "string":
        if not isinstance(value, str):
            return [f"aux field {field!r} must be a string"]
    elif type_spec == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return [f"aux field {field!r} must be a number"]
    elif type_spec == "object":
        if not isinstance(value, dict):
            return [f"aux field {field!r} must be an object"]
    elif type_spec.startswith("enum:"):
        allowed = type_spec[len("enum:"):].split("|")
        if value not in allowed:
            return [f"aux field {field!r} must be one of {allowed}"]
    else:
        return [f"unknown type spec {type_spec!r} for field {field!r}"]
    return []


def _aux_problems(kind: str, receipt: dict) -> list[str]:
    spec = KINDS[kind]
    problems: list[str] = []

    required = dict(spec["required_aux"])
    conditional = spec.get("conditional_aux", {})
    for switch_field, branches in conditional.items():
        switch_value = receipt.get(switch_field)
        branch = branches.get(switch_value)
        if branch:
            required.update(branch)

    for field, type_spec in required.items():
        if field not in receipt:
            problems.append(f"{kind}: missing required aux field {field!r}")
        else:
            problems.extend(_type_problems(field, receipt[field], type_spec))

    for field, type_spec in spec.get("optional_aux", {}).items():
        if field in receipt:
            problems.extend(_type_problems(field, receipt[field], type_spec))

    return problems


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
    if kind not in KINDS:
        raise ValueError(f"unknown diamond receipt kind: {kind}")
    receipt = receipt_v0.emit(
        who=who,
        did=KINDS[kind]["did"],
        this=this,
        when=when,
        confirmed_by=confirmed_by,
        status=STATUS,
        aux=aux,
    )
    problems = diamond_receipt_problems(receipt)
    if problems:
        raise ValueError(f"non-conformant {kind} receipt: {problems}")
    return receipt


def diamond_receipt_problems(receipt) -> list[str]:
    """Full vocabulary conformance check. Empty list means conformant.

    Layer 1: the receipt must be a conformant logline.receipt.v0.
    Layer 2: it must satisfy its kind's vocabulary.
    """
    problems = [f"receipt: {p}" for p in receipt_v0.receipt_problems(receipt)]
    if problems:
        return problems

    kind = DID_TO_KIND.get(receipt["did"])
    if kind is None:
        return [f"did {receipt['did']!r} is not a diamond receipt verb"]

    if receipt["status"] != STATUS:
        problems.append(f"{kind}: status must be {STATUS!r}, got {receipt['status']!r}")
    if not _HEX64.match(receipt["this"]):
        problems.append(
            f"{kind}: this must be a bare 64-hex semantic address (identity-registers.v0)"
        )
    problems.extend(_aux_problems(kind, receipt))
    return problems


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
