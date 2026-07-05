"""Generic vocabulary engine over logline.receipt.v0.

A vocabulary constrains the one canon receipt shape — fixed `did` verb per
kind, pinned status, bare 64-hex `this`, typed AUX schema with optional
conditionals — without ever defining a new object type. Both
diamond.receipts.v0 and diamond.runtime.v0 run on this engine, so the
checking logic cannot fork between them.
"""
from __future__ import annotations

import re

from logline_kernel.core import receipt_v0

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def type_problems(field: str, value, type_spec: str) -> list[str]:
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


def aux_problems(kind: str, spec: dict, receipt: dict) -> list[str]:
    problems: list[str] = []

    required = dict(spec["required_aux"])
    for switch_field, branches in spec.get("conditional_aux", {}).items():
        branch = branches.get(receipt.get(switch_field))
        if branch:
            required.update(branch)

    for field, type_spec in required.items():
        if field not in receipt:
            problems.append(f"{kind}: missing required aux field {field!r}")
        else:
            problems.extend(type_problems(field, receipt[field], type_spec))

    for field, type_spec in spec.get("optional_aux", {}).items():
        if field in receipt:
            problems.extend(type_problems(field, receipt[field], type_spec))

    return problems


def vocabulary_problems(receipt, kinds: dict, status: str) -> list[str]:
    """Layer 1: conformant logline.receipt.v0. Layer 2: kind vocabulary."""
    problems = [f"receipt: {p}" for p in receipt_v0.receipt_problems(receipt)]
    if problems:
        return problems

    did_to_kind = {spec["did"]: kind for kind, spec in kinds.items()}
    kind = did_to_kind.get(receipt["did"])
    if kind is None:
        return [f"did {receipt['did']!r} is not in this vocabulary"]

    if receipt["status"] != status:
        problems.append(f"{kind}: status must be {status!r}, got {receipt['status']!r}")
    if not _HEX64.match(receipt["this"]):
        problems.append(
            f"{kind}: this must be a bare 64-hex semantic address (identity-registers.v0)"
        )
    problems.extend(aux_problems(kind, kinds[kind], receipt))
    return problems


def emit(
    kind: str,
    kinds: dict,
    status: str,
    who: str,
    this: str,
    aux: dict,
    when: str | None = None,
    confirmed_by: str = "",
) -> dict:
    """Emit a vocabulary-conformant receipt or raise — never half-conformant."""
    if kind not in kinds:
        raise ValueError(f"unknown vocabulary kind: {kind}")
    receipt = receipt_v0.emit(
        who=who,
        did=kinds[kind]["did"],
        this=this,
        when=when,
        confirmed_by=confirmed_by,
        status=status,
        aux=aux,
    )
    problems = vocabulary_problems(receipt, kinds, status)
    if problems:
        raise ValueError(f"non-conformant {kind} receipt: {problems}")
    return receipt
