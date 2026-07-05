"""seal_binary — the first real sealer: bytes in, sealed-binary.v0 shell out.

Builds actual Diamond shells against the published profile:
    LogLine-Foundation/conformance/hash-profiles/sealed-binary.v0.md
    LogLine-Foundation/conformance/portable-claims.v0.md

Discipline: a shell is never returned half-conformant. Every seal
self-verifies through the classifier and the binary-layer checks before
anything leaves this module — the sealer obeys the same law it produces
evidence for.

The binding order (cycle rule): receipts embedded in a manifest address
what existed BEFORE sealing — the source set (custody: Merkle root) and
the compiled artifact (compilation/evaluation/privacy: payload digest).
They cannot address the diamond_id, because the diamond_id is the hash of
the manifest that embeds them. Receipts about the sealed shell (access,
supersession) address diamond_id and live only in the ledger, after
sealing.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from logline_kernel.core.hashing import content_hash
from logline_kernel.diamonds import receipts_v0, shell_v0

SEAL_VERSION = "sealed-binary.v0"
DEFAULT_KIND = "compiled_training_diamond.v1"
DEFAULT_CONTAINER = "raw.bytes.v0"


class SealError(Exception):
    pass


@dataclass
class SealResult:
    manifest: dict
    diamond_id: str
    payload_digest: str
    source_merkle_root: str | None
    receipts: list = field(default_factory=list)  # receipts emitted during sealing
    portable: bool = False


def source_digest(data: bytes) -> str:
    """Digest of one raw source. The source bytes never enter the manifest."""
    return hashlib.sha256(data).hexdigest()


def build_manifest(
    payload: bytes,
    source_digests: list[str] | None = None,
    *,
    kind: str = DEFAULT_KIND,
    container_profile: str = DEFAULT_CONTAINER,
    process_contract_hash: str | None = None,
    compiler_hash: str | None = None,
    rights_policy_hash: str | None = None,
    custody_policy_hash: str | None = None,
    receipts: list[str] | None = None,
    unverified: dict | None = None,
) -> dict:
    """Pure manifest construction. No verification — see seal()."""
    manifest: dict = {
        "seal_version": SEAL_VERSION,
        "kind": kind,
        "payload": {
            "digest": shell_v0.payload_digest(payload),
            "algorithm": "sha256",
            "length": len(payload),
            "container_profile": container_profile,
        },
    }
    if source_digests:
        manifest["source_commitments"] = {
            "merkle_root": shell_v0.merkle_root(source_digests),
            "algorithm": "sha256",
            "leaf_count": len(set(source_digests)),
        }
    if process_contract_hash is not None:
        manifest["process_contract_hash"] = process_contract_hash
    if compiler_hash is not None:
        manifest["compiler_hash"] = compiler_hash
    if rights_policy_hash is not None:
        manifest["rights_policy_hash"] = rights_policy_hash
    if custody_policy_hash is not None:
        manifest["custody_policy_hash"] = custody_policy_hash
    manifest["receipts"] = list(receipts or [])
    if unverified is not None:
        manifest["unverified"] = unverified
    manifest["json_canonicalization"] = "jcs-rfc8785"
    return manifest


def seal(
    payload: bytes,
    source_digests: list[str] | None = None,
    **manifest_kwargs,
) -> SealResult:
    """Build and self-verify a shell. Raises SealError on any problem.

    The returned shell may be an identity object (empty receipts) — check
    `.portable` before presenting it as a travelling Diamond.
    """
    manifest = build_manifest(payload, source_digests, **manifest_kwargs)
    diamond_id = content_hash(manifest)

    problems = shell_v0.verify_sealed_binary(
        manifest, payload, source_digests, diamond_id)
    if problems:
        raise SealError(f"refusing to seal non-conformant shell: {problems}")

    portable, _ = shell_v0.is_portable(manifest)
    return SealResult(
        manifest=manifest,
        diamond_id=diamond_id,
        payload_digest=manifest["payload"]["digest"],
        source_merkle_root=(manifest.get("source_commitments") or {}).get("merkle_root"),
        receipts=[],
        portable=portable,
    )


def seal_portable(
    payload: bytes,
    sources: list[bytes],
    *,
    who: str,
    compiler_hash: str,
    process_contract_hash: str,
    rights_policy_hash: str,
    custody_policy_hash: str | None = None,
    extra_receipt_ids: list[str] | None = None,
    unverified: dict | None = None,
    when: str | None = None,
    **manifest_kwargs,
) -> SealResult:
    """The golden path: consume sources, emit the pre-sealing receipts,
    seal a PORTABLE shell.

    Emits (per the binding order):
      custody receipt      — this = source Merkle root
      compilation receipt  — this = payload digest
    embeds their ids in the manifest, then seals. Access receipts and any
    supersession come later, address the diamond_id, and live in the
    ledger — never inside the manifest.
    """
    if not sources:
        raise SealError("seal_portable requires at least one source: "
                        "a Diamond with no committed sources has no provenance")

    digests = [source_digest(s) for s in sources]
    merkle = shell_v0.merkle_root(digests)
    p_digest = shell_v0.payload_digest(payload)

    custody = receipts_v0.emit_diamond_receipt(
        "custody", who=who, this=merkle, when=when,
        aux={"custody_policy_hash": custody_policy_hash or rights_policy_hash},
    )
    compilation = receipts_v0.emit_diamond_receipt(
        "compilation", who=who, this=p_digest, when=when,
        aux={
            "compiler_hash": compiler_hash,
            "process_contract_hash": process_contract_hash,
            "payload_digest": p_digest,
            "source_merkle_root": merkle,
        },
    )

    receipt_ids = [custody["id"], compilation["id"], *(extra_receipt_ids or [])]
    result = seal(
        payload,
        digests,
        compiler_hash=compiler_hash,
        process_contract_hash=process_contract_hash,
        rights_policy_hash=rights_policy_hash,
        custody_policy_hash=custody_policy_hash,
        receipts=receipt_ids,
        unverified=unverified,
        **manifest_kwargs,
    )
    result.receipts = [custody, compilation]
    if not result.portable:
        raise SealError("seal_portable produced a non-portable shell (bug)")
    return result
