"""logline.receipt.v0 — canon receipt emission, verification, and envelopes.

Implements the current LogLine-Foundation canon:
    LogLine-Foundation/canon/logline.receipt.v0
    LogLine-Foundation/conformance/schemas/logline.receipt.v0.schema.json

A Receipt is a nine-slot accountable act with three hash layers:
    tuple_hash   — sha256(JCS(pick nine slots))        pure act
    content_hash — sha256(JCS(all fields - id/hashes)) interpreted act; id == this
    envelope_hash— sha256(JCS({content, transport}))   transport wrapper ONLY

The rules here mirror the reference verifier
(LogLine-Foundation/conformance/tools/verify-receipt.mjs) one-to-one, and are
proven against the Foundation vector set in tests/test_receipt_v0.py.
"""
from __future__ import annotations

import re

from logline_kernel.core.hashing import content_hash as _hash
from logline_kernel.core.time import now_iso

RECEIPT_VERSION = "logline.receipt.v0"
JSON_CANON = "jcs-rfc8785"

SLOTS = (
    "who", "did", "this", "when",
    "confirmed_by", "if_ok", "if_doubt", "if_not", "status",
)

RESERVED_FIELDS = frozenset(SLOTS) | {
    "id", "hashes", "receipt_version", "json_canonicalization",
}

# Names that carried meaning in earlier drafts and MUST NOT appear in v0.
# transport lives only on the Envelope wrapper; result/evidence are upstream
# concerns that the receipt must not smuggle as AUX.
FORBIDDEN_LEGACY_FIELDS = ("result", "evidence", "transport")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


# ---------------------------------------------------------------- derivations

def tuple_hash(receipt: dict) -> str:
    """D42: identity of the pure act — the nine slots, nothing else."""
    return _hash({k: receipt[k] for k in SLOTS})


def receipt_content_hash(receipt: dict) -> str:
    """D43: identity of the interpreted act — everything except id/hashes."""
    return _hash({k: v for k, v in receipt.items() if k not in ("id", "hashes")})


def envelope_hash(envelope: dict) -> str:
    """D44: identity of the transported package — {content, transport}."""
    return _hash({k: v for k, v in envelope.items() if k != "envelope_hash"})


# ---------------------------------------------------------------- emission

def emit(
    who: str,
    did: str,
    this: str,
    when: str | None = None,
    confirmed_by: str = "",
    if_ok: str = "",
    if_doubt: str = "",
    if_not: str = "",
    status: str = "claimed",
    aux: dict | None = None,
) -> dict:
    """Build a complete, conformant logline.receipt.v0.

    AUX fields become free top-level fields: included in content_hash,
    excluded from tuple_hash, never shadowing reserved or legacy names.
    """
    receipt = {
        "receipt_version": RECEIPT_VERSION,
        "who": who,
        "did": did,
        "this": this,
        "when": when if when is not None else now_iso(),
        "confirmed_by": confirmed_by,
        "if_ok": if_ok,
        "if_doubt": if_doubt,
        "if_not": if_not,
        "status": status,
        "json_canonicalization": JSON_CANON,
    }
    for slot in SLOTS:
        if not isinstance(receipt[slot], str):
            raise TypeError(f"slot {slot!r} must be a string")
    if aux:
        for key in aux:
            if key in RESERVED_FIELDS:
                raise ValueError(f"aux field shadows reserved name: {key}")
            if key in FORBIDDEN_LEGACY_FIELDS:
                raise ValueError(f"aux field uses forbidden legacy name: {key}")
        receipt.update(aux)
    receipt["hashes"] = {
        "tuple_hash": tuple_hash(receipt),
        "content_hash": receipt_content_hash(receipt),
        "algorithm": "sha256",
    }
    receipt["id"] = receipt["hashes"]["content_hash"]
    return receipt


# ---------------------------------------------------------------- verification

def receipt_problems(receipt) -> list[str]:
    """Full conformance check. Empty list means conformant.

    Mirrors verify-receipt.mjs: schema shape first, then hash recomputation.
    """
    if not isinstance(receipt, dict):
        return ["receipt is not a JSON object"]
    problems: list[str] = []

    if receipt.get("receipt_version") != RECEIPT_VERSION:
        problems.append(f"receipt_version must be {RECEIPT_VERSION!r}")
    if receipt.get("json_canonicalization") != JSON_CANON:
        problems.append(f"json_canonicalization must be {JSON_CANON!r}")

    for slot in SLOTS:
        if slot not in receipt:
            problems.append(f"missing required slot {slot!r}")
        elif not isinstance(receipt[slot], str):
            problems.append(f"slot {slot!r} must be a string")

    hashes = receipt.get("hashes")
    if not isinstance(hashes, dict):
        problems.append("missing or invalid 'hashes' object")
    else:
        if hashes.get("algorithm") != "sha256":
            problems.append("hashes.algorithm must be 'sha256'")
        for field in ("tuple_hash", "content_hash"):
            value = hashes.get(field)
            if not isinstance(value, str) or not _HEX64.match(value):
                problems.append(f"hashes.{field} must be a 64-char hex sha256")
        for key in hashes:
            if key not in ("tuple_hash", "content_hash", "algorithm"):
                problems.append(
                    f"hashes contains unexpected field {key!r} "
                    "(envelope_hash lives on the Envelope wrapper, not the receipt)"
                )

    if "id" not in receipt:
        problems.append("missing required field 'id'")
    elif not isinstance(receipt["id"], str) or not _HEX64.match(receipt["id"]):
        problems.append("id must be a 64-char lowercase hex sha256")

    for key in FORBIDDEN_LEGACY_FIELDS:
        if key in receipt:
            problems.append(f"reserved legacy field {key!r} MUST NOT appear in receipt v0")

    if problems:
        return problems  # hash recomputation needs a well-shaped receipt

    expected_tuple = tuple_hash(receipt)
    if hashes["tuple_hash"] != expected_tuple:
        problems.append(f"tuple_hash mismatch: expected {expected_tuple}")
    expected_content = receipt_content_hash(receipt)
    if hashes["content_hash"] != expected_content:
        problems.append(f"content_hash mismatch: expected {expected_content}")
    if receipt["id"] != expected_content:
        problems.append("id mismatch: must equal hashes.content_hash")
    return problems


def is_conformant(receipt) -> bool:
    return not receipt_problems(receipt)


# ---------------------------------------------------------------- envelope

def wrap_envelope(
    receipt: dict,
    sent_by: str,
    sent_to: str,
    sent_at: str | None = None,
    channel: str | None = None,
) -> dict:
    """Wrap a receipt for a transport boundary. Sender computes envelope_hash;
    receiver verifies with envelope_problems() before accepting content."""
    transport = {
        "sent_by": sent_by,
        "sent_to": sent_to,
        "sent_at": sent_at if sent_at is not None else now_iso(),
    }
    if channel is not None:
        transport["channel"] = channel
    envelope = {"content": receipt, "transport": transport}
    envelope["envelope_hash"] = envelope_hash(envelope)
    return envelope


def envelope_problems(envelope) -> list[str]:
    if not isinstance(envelope, dict):
        return ["envelope is not a JSON object"]
    problems: list[str] = []

    for key in ("content", "transport", "envelope_hash"):
        if key not in envelope:
            problems.append(f"missing required envelope field {key!r}")
    for key in envelope:
        if key not in ("content", "transport", "envelope_hash"):
            problems.append(f"envelope contains unexpected field {key!r}")
    if problems:
        return problems

    transport = envelope["transport"]
    if not isinstance(transport, dict):
        problems.append("transport must be an object")
    else:
        for field in ("sent_by", "sent_to", "sent_at"):
            if not isinstance(transport.get(field), str):
                problems.append(f"transport.{field} must be a string")

    eh = envelope["envelope_hash"]
    if not isinstance(eh, str) or not _HEX64.match(eh):
        problems.append("envelope_hash must be a 64-char hex sha256")
    else:
        expected = envelope_hash(envelope)
        if eh != expected:
            problems.append(f"envelope_hash mismatch: expected {expected}")

    problems.extend(f"content: {p}" for p in receipt_problems(envelope["content"]))
    return problems
