"""Portable-claim classifier and sealed-binary verification for Diamond shells.

Implements:
    LogLine-Foundation/conformance/portable-claims.v0.md   (the classifier)
    LogLine-Foundation/conformance/hash-profiles/sealed-binary.v0.md
        (payload digest, Merkle source commitments, diamond_id binding)

Field-aware by design (identity-registers.v0): register checks apply only
to identity-bearing fields; vocabulary fields are never register-checked.
"""
from __future__ import annotations

import hashlib
import re

from logline_kernel.core.hashing import content_hash

_HEX64 = re.compile(r"^[0-9a-f]{64}$")

# ------------------------------------------------------- claim classification

CONTENT_ADDRESSED = "content-addressed"
RECEIPT_BACKED = "receipt-backed"
RIGHTS_SCOPED = "rights-scoped"
STRUCTURAL = "structural"
UNVERIFIED = "unverified"

# Top-level fields of a sealed-binary.v0 manifest, each in exactly one bin.
SHELL_BINS = {
    "payload": CONTENT_ADDRESSED,
    "source_commitments": CONTENT_ADDRESSED,
    "process_contract_hash": CONTENT_ADDRESSED,
    "compiler_hash": CONTENT_ADDRESSED,
    "receipts": RECEIPT_BACKED,
    "rights_policy_hash": RIGHTS_SCOPED,
    "custody_policy_hash": RIGHTS_SCOPED,
    "seal_version": STRUCTURAL,
    "kind": STRUCTURAL,
    "json_canonicalization": STRUCTURAL,
    "unverified": UNVERIFIED,
}

# Identity-bearing fields (register check: bare 64-hex). Everything else in
# the manifest is structural vocabulary and is never register-checked.
_TOP_LEVEL_IDENTITY = (
    "process_contract_hash",
    "compiler_hash",
    "rights_policy_hash",
    "custody_policy_hash",
)

_PAYLOAD_STRUCTURAL = {"algorithm", "length", "container_profile"}
_COMMITMENTS_STRUCTURAL = {"algorithm", "leaf_count"}


def classify_shell(manifest) -> tuple[dict, list[str]]:
    """Classify every top-level field of a Diamond shell into its bin.

    Returns (classification, problems). Any unclassifiable field is a
    problem: portable claims must be content-addressed, receipt-backed,
    rights-scoped, or explicitly unverified.
    """
    if not isinstance(manifest, dict):
        return {}, ["manifest is not a JSON object"]

    classification: dict = {}
    problems: list[str] = []

    for field in manifest:
        bin_ = SHELL_BINS.get(field)
        if bin_ is None:
            problems.append(
                f"unclassifiable portable claim: {field!r} "
                "(not content-addressed, receipt-backed, rights-scoped, "
                "structural, or under 'unverified')"
            )
        else:
            classification[field] = bin_

    for field in _TOP_LEVEL_IDENTITY:
        value = manifest.get(field)
        if value is not None and (not isinstance(value, str) or not _HEX64.match(value)):
            problems.append(
                f"identity-bearing field {field!r} must be a bare 64-hex hash"
            )

    payload = manifest.get("payload")
    if not isinstance(payload, dict):
        problems.append("missing or invalid 'payload' object")
    else:
        digest = payload.get("digest")
        if not isinstance(digest, str) or not _HEX64.match(digest):
            problems.append("payload.digest must be a bare 64-hex digest")
        if not isinstance(payload.get("length"), int) or isinstance(payload.get("length"), bool):
            problems.append("payload.length (byte count) is required")
        for key in payload:
            if key != "digest" and key not in _PAYLOAD_STRUCTURAL:
                problems.append(f"unclassifiable payload field: {key!r}")

    commitments = manifest.get("source_commitments")
    if commitments is not None:
        if not isinstance(commitments, dict):
            problems.append("source_commitments must be an object")
        else:
            root = commitments.get("merkle_root")
            if not isinstance(root, str) or not _HEX64.match(root):
                problems.append("source_commitments.merkle_root must be a bare 64-hex digest")
            for key in commitments:
                if key != "merkle_root" and key not in _COMMITMENTS_STRUCTURAL:
                    problems.append(f"unclassifiable source_commitments field: {key!r}")

    receipts = manifest.get("receipts")
    if receipts is None:
        problems.append("missing 'receipts' array (may be empty for identity-only shells)")
    elif not isinstance(receipts, list):
        problems.append("receipts must be an array of receipt ids")
    else:
        for i, rid in enumerate(receipts):
            if not isinstance(rid, str) or not _HEX64.match(rid):
                problems.append(f"receipts[{i}] must be a bare 64-hex receipt id")

    unverified = manifest.get("unverified")
    if unverified is not None and not isinstance(unverified, dict):
        problems.append("'unverified' must be an object (the quarantine for free claims)")

    return classification, problems


def is_portable(manifest) -> tuple[bool, list[str]]:
    """A shell is portable only if classification passes AND at least one
    receipt travels with it. Identity may travel bare; claims may not."""
    _, problems = classify_shell(manifest)
    if problems:
        return False, problems
    if not manifest.get("receipts"):
        return False, [
            "shell is a valid identity object but NOT portable: "
            "receipts[] is empty (provenance must travel with the object)"
        ]
    return True, []


# ------------------------------------------------------- sealed-binary layer

def payload_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def merkle_root(source_digests: list[str]) -> str:
    """Merkle root per sealed-binary.v0: leaf = sha256(0x00 || digest bytes),
    leaves sorted ascending and deduplicated, node = sha256(0x01 || L || R),
    odd node promoted unchanged."""
    if not source_digests:
        raise ValueError("merkle_root requires at least one source digest")
    for d in source_digests:
        if not isinstance(d, str) or not _HEX64.match(d):
            raise ValueError(f"source digest must be bare 64-hex: {d!r}")
    level = sorted({
        hashlib.sha256(b"\x00" + bytes.fromhex(d)).digest()
        for d in source_digests
    })
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                nxt.append(hashlib.sha256(b"\x01" + level[i] + level[i + 1]).digest())
            else:
                nxt.append(level[i])
        level = nxt
    return level[0].hex()


def verify_sealed_binary(
    manifest: dict,
    payload: bytes | None = None,
    source_digests: list[str] | None = None,
    expected_diamond_id: str | None = None,
) -> list[str]:
    """Verify the binary layer of a shell against actual bytes.

    Only checks what it is given: payload bytes prove the digest and length,
    source digests prove the Merkle root, expected_diamond_id proves the
    manifest binding. Absent inputs are simply not checked — verification
    never pretends to cover more than it saw.
    """
    problems: list[str] = []
    _, class_problems = classify_shell(manifest)
    problems.extend(class_problems)
    if class_problems:
        return problems

    if payload is not None:
        declared = manifest["payload"]
        actual_digest = payload_digest(payload)
        if declared["digest"] != actual_digest:
            problems.append(
                f"payload digest mismatch: manifest declares {declared['digest']}, "
                f"bytes hash to {actual_digest}"
            )
        if declared["length"] != len(payload):
            problems.append(
                f"payload length mismatch: manifest declares {declared['length']}, "
                f"got {len(payload)} bytes"
            )

    if source_digests is not None and manifest.get("source_commitments"):
        declared_root = manifest["source_commitments"]["merkle_root"]
        actual_root = merkle_root(source_digests)
        if declared_root != actual_root:
            problems.append(
                f"source merkle_root mismatch: manifest declares {declared_root}, "
                f"sources produce {actual_root}"
            )
        leaf_count = manifest["source_commitments"].get("leaf_count")
        if leaf_count is not None and leaf_count != len(set(source_digests)):
            problems.append(
                f"leaf_count mismatch: manifest declares {leaf_count}, "
                f"got {len(set(source_digests))} distinct sources"
            )

    if expected_diamond_id is not None:
        actual_id = content_hash(manifest)
        if actual_id != expected_diamond_id:
            problems.append(
                f"diamond_id mismatch: expected {expected_diamond_id}, "
                f"manifest hashes to {actual_id}"
            )

    return problems
