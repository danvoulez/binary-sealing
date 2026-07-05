"""Diamond Sealer v0 — final state transition from candidate to sealed Diamond.

Core law:
    Sealing is not truth.
    Sealing is a custody/state transition over a bounded projection artifact.
    The sealer must not reinterpret the projection, erase doubt, or alter lineage.

Input:
    diamond_manifest.json with state="candidate"

Output:
    sealed diamond_manifest.json
    vault_receipt.json
    index.md
    receipt events

Dependency-free: stdlib only.

NOTE:
    The default signer here is hash-only and not cryptographic.
    Production should replace it with an external Ed25519 signer.
"""
from __future__ import annotations

import os
import json
import copy
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional, Protocol

# ---------------------------------------------------------------------------
# Canonical hashing
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

def content_hash(obj: Any, prefix: str = "") -> str:
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return f"{prefix}{digest}" if prefix else digest

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def write_json(path: str, data: dict) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_segment(s: str) -> str:
    out = "".join(c if c.isalnum() or c in "._@+=-" else "_" for c in s.strip())
    return out[:180] or "unknown"

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "diamond_sealer") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "diamond_sealer") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Authority and signer
# ---------------------------------------------------------------------------

DIAMOND_KINDS = {
    "D.DATA",
    "D.EMB",
    "D.TRAJ",
    "D.AUD",
    "D.PROJ",
}

@dataclass
class SealingAuthority:
    authority_id: str
    name: str
    role: str
    allowed_diamond_kinds: list[str] = field(default_factory=lambda: sorted(DIAMOND_KINDS))
    authority_level: str = "final_sealing_authority"
    public_key_ref: Optional[str] = None
    policy_ref: Optional[str] = None
    constraints: list[str] = field(default_factory=list)

    def body(self) -> dict:
        return asdict(self)

    @property
    def authority_hash(self) -> str:
        return content_hash(self.body(), "authority:")

    def can_seal(self, diamond_kind: str) -> bool:
        return (
            self.authority_level == "final_sealing_authority"
            and diamond_kind in self.allowed_diamond_kinds
        )

class SealSigner(Protocol):
    def sign(self, payload: dict, authority: SealingAuthority) -> dict:
        ...

class HashOnlySigner:
    """Non-cryptographic v0 signer.

    This is useful for testing the pipeline.
    Replace with Ed25519 or another real signature mechanism for production.
    """

    def sign(self, payload: dict, authority: SealingAuthority) -> dict:
        payload_hash = content_hash(payload, "seal-payload:")
        pseudo_signature = content_hash(
            {
                "payload_hash": payload_hash,
                "authority_hash": authority.authority_hash,
            },
            "hash-seal:",
        )

        return {
            "kind": "diamond.seal_proof.v0",
            "signature_type": "hash_only_not_cryptographic",
            "warning": "This v0 proof is not a cryptographic signature.",
            "authority_id": authority.authority_id,
            "authority_hash": authority.authority_hash,
            "public_key_ref": authority.public_key_ref,
            "payload_hash": payload_hash,
            "signature": pseudo_signature,
            "signed_at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------

COMPUTED_MANIFEST_FIELDS = {
    "manifest_hash",
    "diamond_candidate_id",
    "diamond_id",
    "sealed_manifest_hash",
}

def manifest_identity_body(manifest: dict) -> dict:
    """Return manifest body used for manifest_hash.

    Signatures are excluded so signatures can be attached after identity is
    computed. Computed IDs are also excluded.
    """
    d = copy.deepcopy(manifest)

    for key in COMPUTED_MANIFEST_FIELDS:
        d.pop(key, None)

    d.pop("signatures", None)

    return d

def expected_manifest_hash(manifest: dict) -> str:
    return content_hash(manifest_identity_body(manifest), "diamond-manifest:")

def expected_candidate_id(manifest: dict) -> str:
    return content_hash(
        {
            "state": manifest.get("state"),
            "diamond_kind": manifest.get("diamond_kind"),
            "projection_hash": manifest.get("projection_hash"),
            "source_boundary_hash": manifest.get("source_boundary_hash"),
            "sealability_report_hash": manifest.get("sealability_report_hash"),
            "sealability_context_hash": manifest.get("sealability_context_hash"),
        },
        "diamond-candidate:",
    )

def expected_diamond_id(sealed_manifest: dict) -> str:
    return content_hash(
        {
            "state": "sealed",
            "diamond_kind": sealed_manifest.get("diamond_kind"),
            "sealed_manifest_hash": sealed_manifest.get("manifest_hash"),
            "candidate_manifest_hash": sealed_manifest.get("candidate_manifest_hash"),
            "projection_hash": sealed_manifest.get("projection_hash"),
            "source_boundary_hash": sealed_manifest.get("source_boundary_hash"),
        },
        "diamond:",
    )

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class DiamondSealResult:
    diamond_id: str
    diamond_kind: str
    sealed_manifest_hash: str
    candidate_manifest_hash: str
    sealed_manifest_path: str
    candidate_snapshot_path: str
    vault_receipt_path: str
    index_path: str
    sealed_at: str
    sealed_by: str
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Sealer
# ---------------------------------------------------------------------------

class DiamondSealError(Exception):
    pass

class DiamondSealer:
    def __init__(
        self,
        nas_root: str,
        receipts: Optional[ReceiptSink] = None,
        signer: Optional[SealSigner] = None,
    ):
        self.nas_root = nas_root
        self.receipts = receipts or NullReceipts()
        self.signer = signer or HashOnlySigner()

    def seal_candidate(
        self,
        candidate_manifest_path: str,
        authority: SealingAuthority,
        actor: str = "diamond_sealer",
        seal_note: str = "",
    ) -> DiamondSealResult:
        candidate = read_json(candidate_manifest_path)

        self.receipts.emit(
            "diamond.seal_started",
            {
                "candidate_manifest_path": candidate_manifest_path,
                "authority_id": authority.authority_id,
                "authority_hash": authority.authority_hash,
            },
            actor=actor,
        )

        self._verify_candidate(candidate, authority)

        candidate_manifest_hash = candidate["manifest_hash"]
        sealed_at = utc_now()

        sealed = copy.deepcopy(candidate)

        # State transition. Do not alter projection, boundary, lineage, doubt,
        # scorecard, rights, custody, revocation, or artifacts.
        sealed["state"] = "sealed"
        sealed["candidate_manifest_hash"] = candidate_manifest_hash
        sealed["sealed_at"] = sealed_at
        sealed["sealed_by"] = authority.authority_id
        sealed["sealing_authority_hash"] = authority.authority_hash
        sealed["seal_note"] = seal_note
        sealed["signatures"] = []

        sealed_manifest_hash = expected_manifest_hash(sealed)
        sealed["manifest_hash"] = sealed_manifest_hash

        diamond_id = expected_diamond_id(sealed)
        sealed["diamond_id"] = diamond_id

        seal_payload = {
            "kind": "diamond.seal_payload.v0",
            "diamond_id": diamond_id,
            "diamond_kind": sealed["diamond_kind"],
            "candidate_manifest_hash": candidate_manifest_hash,
            "sealed_manifest_hash": sealed_manifest_hash,
            "projection_hash": sealed["projection_hash"],
            "source_boundary_hash": sealed["source_boundary_hash"],
            "sealability_report_hash": sealed["sealability_report_hash"],
            "authority_id": authority.authority_id,
            "authority_hash": authority.authority_hash,
            "sealed_at": sealed_at,
            "statement": (
                "This authority seals the candidate as a bounded Diamond artifact. "
                "Sealing does not erase doubt and does not convert projection into raw truth."
            ),
        }

        proof = self.signer.sign(seal_payload, authority)
        proof["payload"] = seal_payload
        sealed["signatures"].append(proof)

        self._verify_sealed_manifest(sealed)

        out_dir = os.path.join(
            self.nas_root,
            "Minivault",
            "30_diamonds",
            "sealed",
            safe_segment(diamond_id),
        )

        sealed_manifest_path = os.path.join(out_dir, "diamond_manifest.json")
        candidate_snapshot_path = os.path.join(out_dir, "candidate_manifest.snapshot.json")
        vault_receipt_path = os.path.join(out_dir, "vault_receipt.json")
        index_path = os.path.join(out_dir, "index.md")

        vault_receipt = self._vault_receipt(
            sealed=sealed,
            authority=authority,
            sealed_manifest_path=sealed_manifest_path,
            candidate_snapshot_path=candidate_snapshot_path,
            sealed_at=sealed_at,
        )

        write_json(sealed_manifest_path, sealed)
        write_json(candidate_snapshot_path, candidate)
        write_json(vault_receipt_path, vault_receipt)
        write_text(index_path, self._render_index_md(sealed, vault_receipt))

        result = DiamondSealResult(
            diamond_id=diamond_id,
            diamond_kind=sealed["diamond_kind"],
            sealed_manifest_hash=sealed_manifest_hash,
            candidate_manifest_hash=candidate_manifest_hash,
            sealed_manifest_path=sealed_manifest_path,
            candidate_snapshot_path=candidate_snapshot_path,
            vault_receipt_path=vault_receipt_path,
            index_path=index_path,
            sealed_at=sealed_at,
            sealed_by=authority.authority_id,
            next_actions=[
                "serve_only_through_access_gate",
                "emit_access_receipts_on_read",
                "preserve_candidate_snapshot",
                "preserve_source_boundary",
                "preserve_doubt_summary",
                "allow_revocation_or_supersession_only_by_policy",
            ],
        )

        self.receipts.emit(
            "diamond.sealed",
            result.to_dict(),
            actor=actor,
        )

        return result

    # ---------------------------------------------------------------------
    # Verification
    # ---------------------------------------------------------------------

    def _verify_candidate(
        self,
        candidate: dict,
        authority: SealingAuthority,
    ) -> None:
        if candidate.get("kind") != "diamond.manifest.v0":
            raise DiamondSealError(f"wrong_manifest_kind:{candidate.get('kind')}")

        if candidate.get("state") != "candidate":
            raise DiamondSealError(f"manifest_not_candidate:{candidate.get('state')}")

        diamond_kind = candidate.get("diamond_kind")
        if diamond_kind not in DIAMOND_KINDS:
            raise DiamondSealError(f"invalid_diamond_kind:{diamond_kind}")

        if not authority.can_seal(diamond_kind):
            raise DiamondSealError(
                f"authority_cannot_seal:{authority.authority_id}:{diamond_kind}"
            )

        actual_hash = candidate.get("manifest_hash")
        expected_hash = expected_manifest_hash(candidate)

        if actual_hash != expected_hash:
            raise DiamondSealError(
                f"candidate_manifest_hash_mismatch:{actual_hash}!={expected_hash}"
            )

        actual_candidate_id = candidate.get("diamond_candidate_id")
        expected_id = expected_candidate_id(candidate)

        if actual_candidate_id != expected_id:
            raise DiamondSealError(
                f"candidate_id_mismatch:{actual_candidate_id}!={expected_id}"
            )

        required_sections = [
            "projection_hash",
            "source_boundary_hash",
            "sealability_report_hash",
            "sealability_context_hash",
            "lineage",
            "boundary",
            "doubt",
            "rights",
            "constraints",
            "custody_policy",
            "revocation",
            "receipts",
            "scorecard",
            "artifacts",
        ]

        missing = [key for key in required_sections if key not in candidate]
        if missing:
            raise DiamondSealError(f"candidate_missing_sections:{missing}")

        if not candidate.get("revocation", {}).get("exists"):
            raise DiamondSealError("candidate_missing_revocation_path")

        if not candidate.get("receipts", {}).get("configured"):
            raise DiamondSealError("candidate_missing_receipt_policy")

        if not candidate.get("custody_policy", {}).get("exists"):
            raise DiamondSealError("candidate_missing_custody_policy")

        if not candidate.get("scorecard", {}).get("exists"):
            raise DiamondSealError("candidate_missing_scorecard")

    def _verify_sealed_manifest(self, sealed: dict) -> None:
        if sealed.get("state") != "sealed":
            raise DiamondSealError("sealed_manifest_state_not_sealed")

        actual_hash = sealed.get("manifest_hash")
        expected_hash = expected_manifest_hash(sealed)

        if actual_hash != expected_hash:
            raise DiamondSealError(
                f"sealed_manifest_hash_mismatch:{actual_hash}!={expected_hash}"
            )

        actual_diamond_id = sealed.get("diamond_id")
        expected_id = expected_diamond_id(sealed)

        if actual_diamond_id != expected_id:
            raise DiamondSealError(
                f"diamond_id_mismatch:{actual_diamond_id}!={expected_id}"
            )

        if not sealed.get("signatures"):
            raise DiamondSealError("sealed_manifest_missing_signature")

        proof = sealed["signatures"][0]
        payload = proof.get("payload", {})
        payload_hash = content_hash(payload, "seal-payload:")

        if proof.get("payload_hash") != payload_hash:
            raise DiamondSealError("seal_payload_hash_mismatch")

        if payload.get("diamond_id") != sealed.get("diamond_id"):
            raise DiamondSealError("seal_payload_diamond_id_mismatch")

        if payload.get("sealed_manifest_hash") != sealed.get("manifest_hash"):
            raise DiamondSealError("seal_payload_manifest_hash_mismatch")

    # ---------------------------------------------------------------------
    # Receipt / rendering
    # ---------------------------------------------------------------------

    def _vault_receipt(
        self,
        sealed: dict,
        authority: SealingAuthority,
        sealed_manifest_path: str,
        candidate_snapshot_path: str,
        sealed_at: str,
    ) -> dict:
        receipt = {
            "kind": "diamond.vault_receipt.v0",
            "diamond_id": sealed["diamond_id"],
            "diamond_kind": sealed["diamond_kind"],
            "state": "sealed",
            "sealed_manifest_hash": sealed["manifest_hash"],
            "candidate_manifest_hash": sealed["candidate_manifest_hash"],
            "projection_hash": sealed["projection_hash"],
            "source_boundary_hash": sealed["source_boundary_hash"],
            "authority_id": authority.authority_id,
            "authority_hash": authority.authority_hash,
            "sealed_at": sealed_at,
            "paths": {
                "sealed_manifest": sealed_manifest_path,
                "candidate_snapshot": candidate_snapshot_path,
            },
            "access_policy": sealed.get("policy", {}).get("access_policy", {}),
            "revocation": sealed.get("revocation", {}),
            "warning": "Vault receipt records custody. It does not turn the Diamond into raw truth.",
        }

        receipt["receipt_hash"] = content_hash(receipt, "vault-receipt:")
        return receipt

    def _render_index_md(self, sealed: dict, receipt: dict) -> str:
        lines = [
            "---",
            "kind: sealed_diamond",
            f"diamond_id: {sealed['diamond_id']}",
            f"manifest_hash: {sealed['manifest_hash']}",
            f"diamond_kind: {sealed['diamond_kind']}",
            f"state: {sealed['state']}",
            f"projection_hash: {sealed['projection_hash']}",
            f"source_boundary_hash: {sealed['source_boundary_hash']}",
            f"sealed_at: {sealed['sealed_at']}",
            f"sealed_by: {sealed['sealed_by']}",
            "---",
            "",
            f"# Sealed Diamond — {sealed.get('title', sealed['diamond_id'])}",
            "",
            "> This is a sealed Diamond artifact. It is bounded, evidenced, and receipted; it is not raw truth.",
            "",
            "## Identity",
            "",
            f"- Diamond ID: `{sealed['diamond_id']}`",
            f"- Manifest hash: `{sealed['manifest_hash']}`",
            f"- Candidate manifest hash: `{sealed['candidate_manifest_hash']}`",
            f"- Kind: `{sealed['diamond_kind']}`",
            f"- State: `{sealed['state']}`",
            "",
            "## Boundary",
            "",
            f"- Projection: `{sealed['projection_hash']}`",
            f"- Source boundary: `{sealed['source_boundary_hash']}`",
            f"- Sealability report: `{sealed['sealability_report_hash']}`",
            "",
            "## Doubt summary",
            "",
            "```json",
            json.dumps(
                sealed.get("doubt", {}).get("doubt_summary", {}),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Seal proof",
            "",
            "```json",
            json.dumps(
                sealed.get("signatures", []),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Vault receipt",
            "",
            f"- Receipt hash: `{receipt['receipt_hash']}`",
            f"- Sealed manifest: `{receipt['paths']['sealed_manifest']}`",
            f"- Candidate snapshot: `{receipt['paths']['candidate_snapshot']}`",
            "",
            "## Constraints",
            "",
            *[f"- {c}" for c in sealed.get("constraints", [])],
            "",
        ]

        return "\n".join(lines)
