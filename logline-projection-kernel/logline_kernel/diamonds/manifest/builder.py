"""Diamond Manifest Builder v0 — build Diamond candidate manifests.

Core law:
    A Diamond is not raw truth.
    A Diamond is a sealed/candidate projection artifact whose boundary,
    provenance, doubt, custody, rights, and revocation path remain explicit.

This builder does NOT perform final sealing.
It only creates a Diamond candidate manifest from a sealable projection.

Input:
    projection.json
    sealability_report.json
    sealability_context dict
    optional artifact descriptors

Output:
    diamond_manifest.json
    index.md
    receipt events

Dependency-free: stdlib only.
"""
from __future__ import annotations

import os
import json
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

def sha256_file(path: str, prefix: str = "sha256:") -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return f"{prefix}{h.hexdigest()}"

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
    def emit(self, kind: str, payload: dict, actor: str = "diamond_manifest_builder") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "diamond_manifest_builder") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Manifest types
# ---------------------------------------------------------------------------

DIAMOND_KINDS = {
    "D.DATA",   # preserved data artifact
    "D.EMB",    # embedding/vector artifact
    "D.TRAJ",   # trajectory/process artifact
    "D.AUD",    # audit/evidence artifact
    "D.PROJ",   # sealed projection artifact
}

@dataclass
class DiamondArtifact:
    role: str
    path: str
    media_type: str = "application/octet-stream"
    description: str = ""
    sha256: Optional[str] = None
    bytes: Optional[int] = None

    def materialize(self) -> dict:
        size = self.bytes
        digest = self.sha256

        if os.path.exists(self.path):
            if size is None:
                size = os.path.getsize(self.path)
            if digest is None:
                digest = sha256_file(self.path)

        return {
            "role": self.role,
            "path": self.path,
            "media_type": self.media_type,
            "description": self.description,
            "sha256": digest,
            "bytes": size,
        }

@dataclass
class DiamondManifest:
    kind: str
    manifest_version: str
    diamond_kind: str
    state: str

    projection_hash: str
    source_boundary_hash: str
    sealability_report_hash: str
    sealability_context_hash: str

    title: str
    purpose: str
    created_by: str
    created_at: str

    lineage: dict
    boundary: dict
    doubt: dict
    rights: dict
    constraints: list
    custody_policy: dict
    revocation: dict
    receipts: dict
    scorecard: dict
    artifacts: list[dict]

    policy: dict = field(default_factory=dict)
    signatures: list[dict] = field(default_factory=list)
    aux: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    def identity_body(self) -> dict:
        """Fields that define the candidate identity.

        Signatures are excluded because the later Diamond Sealer may add them.
        State is included because candidate/sealed/revoked must not hash the same.
        """
        d = self.body()
        d.pop("signatures", None)
        return d

    @property
    def manifest_hash(self) -> str:
        return content_hash(self.identity_body(), "diamond-manifest:")

    @property
    def diamond_candidate_id(self) -> str:
        return content_hash(
            {
                "state": self.state,
                "diamond_kind": self.diamond_kind,
                "projection_hash": self.projection_hash,
                "source_boundary_hash": self.source_boundary_hash,
                "sealability_report_hash": self.sealability_report_hash,
                "sealability_context_hash": self.sealability_context_hash,
            },
            "diamond-candidate:",
        )

    def to_dict(self) -> dict:
        d = self.body()
        d["manifest_hash"] = self.manifest_hash
        d["diamond_candidate_id"] = self.diamond_candidate_id
        return d

@dataclass
class DiamondBuildResult:
    diamond_candidate_id: str
    manifest_hash: str
    manifest_path: str
    index_path: str
    diamond_kind: str
    state: str
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class DiamondManifestBuildError(Exception):
    pass

class DiamondManifestBuilder:
    def __init__(
        self,
        nas_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.nas_root = nas_root
        self.receipts = receipts or NullReceipts()

    def build_candidate(
        self,
        projection_path: str,
        sealability_report_path: str,
        sealability_context: dict,
        diamond_kind: str = "D.PROJ",
        title: Optional[str] = None,
        purpose: Optional[str] = None,
        created_by: str = "diamond_manifest_builder",
        artifacts: Optional[list[DiamondArtifact]] = None,
        aux: Optional[dict] = None,
    ) -> DiamondBuildResult:
        if diamond_kind not in DIAMOND_KINDS:
            raise DiamondManifestBuildError(f"invalid_diamond_kind:{diamond_kind}")

        projection = read_json(projection_path)
        report = read_json(sealability_report_path)

        self._assert_projection_matches_report(projection, report)
        self._assert_report_sealable(report)

        context_hash = content_hash(sealability_context, "seal-context:")
        report_context_hash = report.get("context_hash")

        if report_context_hash and report_context_hash != context_hash:
            raise DiamondManifestBuildError(
                f"sealability_context_hash_mismatch:{report_context_hash}!={context_hash}"
            )

        materialized_artifacts = [
            a.materialize() for a in (artifacts or [])
        ]

        # Always include the projection and sealability report as internal artifacts.
        materialized_artifacts.append(
            DiamondArtifact(
                role="projection",
                path=projection_path,
                media_type="application/json",
                description="Projection used to build this Diamond candidate.",
            ).materialize()
        )

        materialized_artifacts.append(
            DiamondArtifact(
                role="sealability_report",
                path=sealability_report_path,
                media_type="application/json",
                description="Sealability report authorizing candidate construction.",
            ).materialize()
        )

        manifest = DiamondManifest(
            kind="diamond.manifest.v0",
            manifest_version="0.1.0",
            diamond_kind=diamond_kind,
            state="candidate",

            projection_hash=projection["projection_hash"],
            source_boundary_hash=projection["source_boundary_hash"],
            sealability_report_hash=report["report_hash"],
            sealability_context_hash=context_hash,

            title=title or self._default_title(projection, diamond_kind),
            purpose=purpose or projection.get("purpose", "Diamond candidate derived from projection."),
            created_by=created_by,
            created_at=utc_now(),

            lineage=self._lineage(projection, report),
            boundary=self._boundary(projection),
            doubt=self._doubt(projection),
            rights=sealability_context.get("rights", {}),
            constraints=self._constraints(sealability_context),
            custody_policy=sealability_context.get("custody_policy", {}),
            revocation=sealability_context.get("revocation", {}),
            receipts=sealability_context.get("receipts", {}),
            scorecard=sealability_context.get("scorecard", {}),
            artifacts=materialized_artifacts,
            policy=self._policy(sealability_context, projection, report),
            signatures=[],
            aux=aux or {},
        )

        manifest_dict = manifest.to_dict()

        out_dir = os.path.join(
            self.nas_root,
            "Minivault",
            "30_diamonds",
            "candidates",
            safe_segment(manifest.diamond_candidate_id),
        )

        manifest_path = os.path.join(out_dir, "diamond_manifest.json")
        index_path = os.path.join(out_dir, "index.md")

        write_json(manifest_path, manifest_dict)
        write_text(index_path, self._render_index_md(manifest_dict))

        result = DiamondBuildResult(
            diamond_candidate_id=manifest.diamond_candidate_id,
            manifest_hash=manifest.manifest_hash,
            manifest_path=manifest_path,
            index_path=index_path,
            diamond_kind=diamond_kind,
            state="candidate",
            next_actions=[
                "request_final_sealing_authority",
                "verify_manifest_hash",
                "attach_signature",
                "emit_diamond_sealed_or_denied_receipt",
                "do_not_treat_candidate_as_sealed",
            ],
        )

        self.receipts.emit(
            "diamond.candidate_manifest_built",
            result.to_dict(),
            actor=created_by,
        )

        return result

    # ---------------------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------------------

    def _assert_projection_matches_report(self, projection: dict, report: dict) -> None:
        if projection.get("projection_hash") != report.get("projection_hash"):
            raise DiamondManifestBuildError(
                "projection_hash_mismatch_between_projection_and_report"
            )

        if projection.get("source_boundary_hash") != report.get("source_boundary_hash"):
            raise DiamondManifestBuildError(
                "source_boundary_hash_mismatch_between_projection_and_report"
            )

    def _assert_report_sealable(self, report: dict) -> None:
        if report.get("kind") != "sealability.report.v0":
            raise DiamondManifestBuildError(f"wrong_report_kind:{report.get('kind')}")

        if report.get("report_status") != "sealable" or report.get("sealable") is not True:
            raise DiamondManifestBuildError("sealability_report_not_sealable")

        if report.get("blockers"):
            raise DiamondManifestBuildError(f"sealability_blockers_present:{report.get('blockers')}")

    # ---------------------------------------------------------------------
    # Manifest sections
    # ---------------------------------------------------------------------

    def _default_title(self, projection: dict, diamond_kind: str) -> str:
        lens_id = projection.get("lens_id", "unknown_lens")
        return f"{diamond_kind} candidate from {lens_id}"

    def _lineage(self, projection: dict, report: dict) -> dict:
        return {
            "projection_hash": projection.get("projection_hash"),
            "source_boundary_hash": projection.get("source_boundary_hash"),
            "lens_id": projection.get("lens_id"),
            "lens_hash": projection.get("lens_hash"),
            "sealability_report_hash": report.get("report_hash"),
            "selection_trace": projection.get("selection_trace", []),
            "source_records": projection.get("source_records", []),
            "excluded_records": projection.get("excluded_records", []),
        }

    def _boundary(self, projection: dict) -> dict:
        return {
            "source_boundary_hash": projection.get("source_boundary_hash"),
            "included": projection.get("source_records", []),
            "excluded": projection.get("excluded_records", []),
            "scope": projection.get("scope", {}),
            "warning": "This Diamond candidate is only valid inside this source boundary.",
        }

    def _doubt(self, projection: dict) -> dict:
        return {
            "doubt_map": projection.get("doubt_map", {}),
            "doubt_summary": projection.get("doubt_summary", {}),
            "policy_blockers": projection.get("policy_blockers", []),
            "warning": "Doubt is preserved; it is not erased by candidacy.",
        }

    def _constraints(self, context: dict) -> list:
        rights = context.get("rights", {})
        constraints = []

        if isinstance(rights.get("constraints"), list):
            constraints.extend(rights["constraints"])

        if isinstance(context.get("constraints"), list):
            constraints.extend(context["constraints"])

        # Always attach these base constraints.
        constraints.extend([
            "candidate_is_not_final_seal",
            "must_preserve_source_boundary",
            "must_preserve_doubt_summary",
            "must_emit_receipts_on_access_or_state_change",
            "must_support_revocation_or_supersession",
        ])

        # Deduplicate while preserving order.
        out = []
        seen = set()
        for c in constraints:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def _policy(self, context: dict, projection: dict, report: dict) -> dict:
        return {
            "state_policy": {
                "current": "candidate",
                "may_transition_to": ["sealed", "denied", "revoked", "superseded"],
                "requires_for_sealed": [
                    "final_sealing_authority",
                    "signature",
                    "vault_receipt",
                ],
            },
            "access_policy": context.get("access_policy", {
                "default": "private",
                "requires_receipt": True,
                "allowed_roles": ["operator", "owner", "custodian", "admin"],
                "allowed_modes": ["read", "anchor", "export_package", "inspect"],
            }),
            "effect_policy": {
                "external_effects_allowed": False,
                "reason": "Diamond candidate cannot itself authorize external effects.",
            },
            "truth_policy": {
                "is_truth": False,
                "statement": "This is a candidate manifest for a bounded projection artifact, not raw truth.",
            },
            "sealability": {
                "report_hash": report.get("report_hash"),
                "score": report.get("score"),
                "warnings": report.get("warnings", []),
            },
            "projection_warning": projection.get("meta", {}).get(
                "warning",
                "Projection is not truth.",
            ),
        }

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(self, manifest: dict) -> str:
        lines = [
            "---",
            "kind: diamond_candidate",
            f"diamond_candidate_id: {manifest['diamond_candidate_id']}",
            f"manifest_hash: {manifest['manifest_hash']}",
            f"diamond_kind: {manifest['diamond_kind']}",
            f"state: {manifest['state']}",
            f"projection_hash: {manifest['projection_hash']}",
            f"source_boundary_hash: {manifest['source_boundary_hash']}",
            f"created_at: {manifest['created_at']}",
            "---",
            "",
            f"# Diamond Candidate — {manifest['title']}",
            "",
            "> This is a Diamond candidate, not a final sealed Diamond.",
            "",
            "## Identity",
            "",
            f"- Candidate ID: `{manifest['diamond_candidate_id']}`",
            f"- Manifest hash: `{manifest['manifest_hash']}`",
            f"- Kind: `{manifest['diamond_kind']}`",
            f"- State: `{manifest['state']}`",
            "",
            "## Projection lineage",
            "",
            f"- Projection: `{manifest['projection_hash']}`",
            f"- Boundary: `{manifest['source_boundary_hash']}`",
            f"- Sealability report: `{manifest['sealability_report_hash']}`",
            f"- Sealability context: `{manifest['sealability_context_hash']}`",
            "",
            "## Doubt summary",
            "",
            "```json",
            json.dumps(
                manifest.get("doubt", {}).get("doubt_summary", {}),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Constraints",
            "",
            *[f"- {c}" for c in manifest.get("constraints", [])],
            "",
            "## Artifacts",
            "",
        ]

        for artifact in manifest.get("artifacts", []):
            lines.append(
                f"- `{artifact['role']}` — `{artifact['path']}` — "
                f"{artifact.get('media_type')} — `{artifact.get('sha256')}`"
            )

        lines += [
            "",
            "## Next required authority",
            "",
            "- final sealing authority",
            "- manifest hash verification",
            "- signature attachment",
            "- vault receipt",
            "",
        ]

        return "\n".join(lines)
