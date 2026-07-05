"""Diamond Access Gate v0 — receipted access for sealed Diamonds.

Core law:
    No Diamond is read, exported, copied, shown, anchored, or redeemed
    without an access receipt.

    Access is not truth.
    Access is not revocation.
    Access is not mutation.
    Access is a controlled, receipted view over a sealed Diamond artifact.

Input:
    sealed diamond_manifest.json
    AccessRequest

Output:
    access_receipt.json
    access_package.json
    index.md
    receipt events

Dependency-free: stdlib only.
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
    def emit(self, kind: str, payload: dict, actor: str = "diamond_access_gate") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "diamond_access_gate") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Manifest verification helpers
# ---------------------------------------------------------------------------

COMPUTED_MANIFEST_FIELDS = {
    "manifest_hash",
    "diamond_candidate_id",
    "diamond_id",
    "sealed_manifest_hash",
}

def manifest_identity_body(manifest: dict) -> dict:
    """Body used for manifest_hash verification.

    Signatures and computed IDs are excluded because the sealer attaches them
    after identity computation.
    """
    d = copy.deepcopy(manifest)

    for key in COMPUTED_MANIFEST_FIELDS:
        d.pop(key, None)

    d.pop("signatures", None)

    return d

def expected_manifest_hash(manifest: dict) -> str:
    return content_hash(manifest_identity_body(manifest), "diamond-manifest:")

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
# Access vocabulary
# ---------------------------------------------------------------------------

ACCESS_MODES = {
    "inspect",          # view identity, boundary, doubt, constraints
    "read_manifest",    # read full sealed manifest
    "anchor",           # use as safe agent anchor
    "read_artifacts",   # access artifact paths declared in manifest
    "export_manifest",  # copy/serve manifest outward
    "export_package",   # copy/serve manifest + selected artifacts
    "redeem",           # use Diamond for a downstream process
}

SENSITIVE_MODES = {
    "export_manifest",
    "export_package",
    "redeem",
}

@dataclass
class AccessActor:
    actor_id: str
    roles: list[str] = field(default_factory=list)
    authority_refs: list[str] = field(default_factory=list)

    def body(self) -> dict:
        return asdict(self)

@dataclass
class AccessRequest:
    actor: AccessActor
    mode: str
    purpose: str
    reason: str
    requested_artifact_roles: list[str] = field(default_factory=list)
    export_target: Optional[str] = None
    scope: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    @property
    def request_hash(self) -> str:
        return content_hash(self.body(), "access-request:")

@dataclass
class AccessDecision:
    request_hash: str
    diamond_id: str
    mode: str
    allowed: bool
    decision: str
    blockers: list[str]
    warnings: list[str]
    granted_artifacts: list[dict]
    allowed_meanings: list[str]
    forbidden_meanings: list[str]

    def body(self) -> dict:
        return asdict(self)

    @property
    def decision_hash(self) -> str:
        return content_hash(self.body(), "access-decision:")

    def to_dict(self) -> dict:
        d = self.body()
        d["decision_hash"] = self.decision_hash
        return d

@dataclass
class AccessResult:
    diamond_id: str
    request_hash: str
    decision_hash: str
    allowed: bool
    mode: str
    receipt_hash: str
    receipt_path: str
    package_path: str
    index_path: str
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Access Gate
# ---------------------------------------------------------------------------

class DiamondAccessError(Exception):
    pass

class DiamondAccessGate:
    def __init__(
        self,
        nas_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.nas_root = nas_root
        self.receipts = receipts or NullReceipts()

    def request_access(
        self,
        sealed_manifest_path: str,
        request: AccessRequest,
        actor: str = "diamond_access_gate",
    ) -> AccessResult:
        """Evaluate and receipt one access request.

        Even denied requests produce receipts.
        """
        manifest = read_json(sealed_manifest_path)

        self.receipts.emit(
            "diamond.access_requested",
            {
                "request_hash": request.request_hash,
                "actor_id": request.actor.actor_id,
                "mode": request.mode,
                "sealed_manifest_path": sealed_manifest_path,
            },
            actor=actor,
        )

        verification_blockers = self._verify_sealed_manifest(manifest)
        policy_decision = self._decide_access(
            manifest=manifest,
            request=request,
            verification_blockers=verification_blockers,
        )

        out_dir = os.path.join(
            self.nas_root,
            "Minivault",
            "40_receipts",
            "diamond_access",
            safe_segment(manifest.get("diamond_id", "unknown_diamond")),
            safe_segment(request.request_hash),
        )

        receipt_path = os.path.join(out_dir, "access_receipt.json")
        package_path = os.path.join(out_dir, "access_package.json")
        index_path = os.path.join(out_dir, "index.md")

        receipt = self._build_access_receipt(
            manifest=manifest,
            manifest_path=sealed_manifest_path,
            request=request,
            decision=policy_decision,
        )

        package = self._build_access_package(
            manifest=manifest,
            manifest_path=sealed_manifest_path,
            request=request,
            decision=policy_decision,
            receipt=receipt,
        )

        write_json(receipt_path, receipt)
        write_json(package_path, package)
        write_text(index_path, self._render_index_md(package, receipt))

        event_kind = "diamond.access_granted" if policy_decision.allowed else "diamond.access_denied"

        self.receipts.emit(
            event_kind,
            {
                "diamond_id": manifest.get("diamond_id"),
                "request_hash": request.request_hash,
                "decision_hash": policy_decision.decision_hash,
                "receipt_hash": receipt["receipt_hash"],
                "mode": request.mode,
                "allowed": policy_decision.allowed,
                "blockers": policy_decision.blockers,
            },
            actor=actor,
        )

        return AccessResult(
            diamond_id=manifest.get("diamond_id", ""),
            request_hash=request.request_hash,
            decision_hash=policy_decision.decision_hash,
            allowed=policy_decision.allowed,
            mode=request.mode,
            receipt_hash=receipt["receipt_hash"],
            receipt_path=receipt_path,
            package_path=package_path,
            index_path=index_path,
            next_actions=package["next_actions"],
        )

    # ---------------------------------------------------------------------
    # Verification
    # ---------------------------------------------------------------------

    def _verify_sealed_manifest(self, manifest: dict) -> list[str]:
        blockers: list[str] = []

        if manifest.get("kind") != "diamond.manifest.v0":
            blockers.append(f"wrong_manifest_kind:{manifest.get('kind')}")

        if manifest.get("state") != "sealed":
            blockers.append(f"manifest_not_sealed:{manifest.get('state')}")

        actual_manifest_hash = manifest.get("manifest_hash")
        expected_hash = expected_manifest_hash(manifest)

        if actual_manifest_hash != expected_hash:
            blockers.append(
                f"manifest_hash_mismatch:{actual_manifest_hash}!={expected_hash}"
            )

        actual_diamond_id = manifest.get("diamond_id")
        expected_id = expected_diamond_id(manifest)

        if actual_diamond_id != expected_id:
            blockers.append(
                f"diamond_id_mismatch:{actual_diamond_id}!={expected_id}"
            )

        if not manifest.get("signatures"):
            blockers.append("missing_seal_signature")

        if not manifest.get("receipts", {}).get("configured"):
            blockers.append("receipt_policy_missing")

        if not manifest.get("revocation", {}).get("exists"):
            blockers.append("revocation_path_missing")

        if manifest.get("revoked_at") or manifest.get("state") == "revoked":
            blockers.append("diamond_revoked")

        return blockers

    # ---------------------------------------------------------------------
    # Policy decision
    # ---------------------------------------------------------------------

    def _decide_access(
        self,
        manifest: dict,
        request: AccessRequest,
        verification_blockers: list[str],
    ) -> AccessDecision:
        blockers = list(verification_blockers)
        warnings: list[str] = []

        if request.mode not in ACCESS_MODES:
            blockers.append(f"invalid_access_mode:{request.mode}")

        access_policy = manifest.get("policy", {}).get("access_policy", {})
        default_policy = access_policy.get("default", "private")

        allowed_modes = access_policy.get("allowed_modes")
        if allowed_modes and request.mode not in allowed_modes:
            blockers.append(f"mode_not_allowed_by_policy:{request.mode}")

        denied_modes = access_policy.get("denied_modes", [])
        if request.mode in denied_modes:
            blockers.append(f"mode_explicitly_denied:{request.mode}")

        allowed_actors = access_policy.get("allowed_actors")
        if allowed_actors and request.actor.actor_id not in allowed_actors:
            blockers.append(f"actor_not_allowed:{request.actor.actor_id}")

        denied_actors = access_policy.get("denied_actors", [])
        if request.actor.actor_id in denied_actors:
            blockers.append(f"actor_explicitly_denied:{request.actor.actor_id}")

        allowed_roles = set(access_policy.get("allowed_roles", []))
        actor_roles = set(request.actor.roles)

        if allowed_roles and not actor_roles.intersection(allowed_roles):
            blockers.append(
                f"missing_allowed_role:{sorted(allowed_roles)}"
            )

        allowed_purposes = access_policy.get("allowed_purposes")
        if allowed_purposes and request.purpose not in allowed_purposes:
            blockers.append(f"purpose_not_allowed:{request.purpose}")

        if default_policy == "private":
            if not self._private_access_granted(manifest, request, access_policy):
                blockers.append("private_policy_requires_owner_custodian_or_explicit_grant")

        if request.mode in SENSITIVE_MODES:
            if not request.reason.strip():
                blockers.append("sensitive_access_requires_reason")

            if request.mode in {"export_manifest", "export_package"}:
                if not request.export_target:
                    blockers.append("export_requires_target")

        granted_artifacts = self._granted_artifacts(manifest, request, blockers)

        if request.mode in {"read_artifacts", "export_package"}:
            if request.requested_artifact_roles and not granted_artifacts:
                blockers.append("no_requested_artifacts_granted")

        if access_policy.get("requires_receipt", True) is not True:
            warnings.append("policy_does_not_require_receipt_but_gate_will_emit_one")

        if manifest.get("policy", {}).get("truth_policy", {}).get("is_truth") is True:
            warnings.append("manifest_truth_policy_claims_truth_unexpectedly")

        allowed = len(blockers) == 0

        decision = "granted" if allowed else "denied"

        return AccessDecision(
            request_hash=request.request_hash,
            diamond_id=manifest.get("diamond_id", ""),
            mode=request.mode,
            allowed=allowed,
            decision=decision,
            blockers=blockers,
            warnings=warnings,
            granted_artifacts=granted_artifacts if allowed else [],
            allowed_meanings=self._allowed_meanings(request.mode, allowed),
            forbidden_meanings=self._forbidden_meanings(request.mode, allowed),
        )

    def _private_access_granted(
        self,
        manifest: dict,
        request: AccessRequest,
        access_policy: dict,
    ) -> bool:
        if request.actor.actor_id == manifest.get("sealed_by"):
            return True

        if {"owner", "custodian", "admin"}.intersection(set(request.actor.roles)):
            return True

        if request.actor.actor_id in access_policy.get("allowed_actors", []):
            return True

        if set(request.actor.roles).intersection(set(access_policy.get("allowed_roles", []))):
            return True

        return False

    def _granted_artifacts(
        self,
        manifest: dict,
        request: AccessRequest,
        blockers: list[str],
    ) -> list[dict]:
        if blockers:
            return []

        artifacts = manifest.get("artifacts", [])
        requested = set(request.requested_artifact_roles)

        if request.mode not in {"read_artifacts", "export_package"}:
            return []

        if not requested:
            return artifacts

        return [
            a for a in artifacts
            if a.get("role") in requested
        ]

    def _allowed_meanings(self, mode: str, allowed: bool) -> list[str]:
        if not allowed:
            return [
                "may_record_denied_attempt",
                "may_request_review",
                "may_revise_access_request",
            ]

        base = [
            "may_use_only_for_declared_purpose",
            "may_reference_diamond_id",
            "may_reference_source_boundary_hash",
            "may_reference_doubt_summary",
            "may_continue_only_inside_granted_scope",
        ]

        if mode == "anchor":
            base.extend([
                "may_use_as_safe_agent_anchor",
                "may_load_boundary_before_reasoning",
            ])

        if mode in {"export_manifest", "export_package"}:
            base.extend([
                "may_export_only_to_declared_target",
                "may_export_only_granted_artifacts",
            ])

        return base

    def _forbidden_meanings(self, mode: str, allowed: bool) -> list[str]:
        out = [
            "must_not_treat_diamond_as_raw_truth",
            "must_not_ignore_doubt_summary",
            "must_not_expand_beyond_source_boundary",
            "must_not_mutate_manifest",
            "must_not_bypass_receipts",
        ]

        if not allowed:
            out.extend([
                "must_not_read_manifest_payload",
                "must_not_export",
                "must_not_anchor",
                "must_not_redeem",
            ])

        if mode in {"export_manifest", "export_package"}:
            out.extend([
                "must_not_export_to_unrecorded_target",
                "must_not_strip_constraints",
                "must_not_strip_revocation_policy",
            ])

        return out

    # ---------------------------------------------------------------------
    # Receipt / package
    # ---------------------------------------------------------------------

    def _build_access_receipt(
        self,
        manifest: dict,
        manifest_path: str,
        request: AccessRequest,
        decision: AccessDecision,
    ) -> dict:
        receipt = {
            "kind": "diamond.access_receipt.v0",
            "diamond_id": manifest.get("diamond_id"),
            "diamond_kind": manifest.get("diamond_kind"),
            "manifest_hash": manifest.get("manifest_hash"),
            "source_boundary_hash": manifest.get("source_boundary_hash"),
            "request": request.body(),
            "request_hash": request.request_hash,
            "decision": decision.to_dict(),
            "decision_hash": decision.decision_hash,
            "manifest_path": manifest_path,
            "accessed_at": utc_now(),
            "warning": (
                "This receipt records access. Access does not convert the Diamond "
                "into raw truth and does not erase doubt."
            ),
        }

        receipt["receipt_hash"] = content_hash(receipt, "access-receipt:")
        return receipt

    def _build_access_package(
        self,
        manifest: dict,
        manifest_path: str,
        request: AccessRequest,
        decision: AccessDecision,
        receipt: dict,
    ) -> dict:
        if not decision.allowed:
            return {
                "kind": "diamond.access_package.v0",
                "state": "denied",
                "diamond_id": manifest.get("diamond_id"),
                "request_hash": request.request_hash,
                "decision_hash": decision.decision_hash,
                "receipt_hash": receipt["receipt_hash"],
                "blockers": decision.blockers,
                "warnings": decision.warnings,
                "granted": {},
                "allowed_meanings": decision.allowed_meanings,
                "forbidden_meanings": decision.forbidden_meanings,
                "next_actions": [
                    "review_denial",
                    "revise_access_request",
                    "request_human_approval",
                    "do_not_access_diamond",
                ],
            }

        granted = {
            "mode": request.mode,
            "diamond_id": manifest.get("diamond_id"),
            "diamond_kind": manifest.get("diamond_kind"),
            "manifest_hash": manifest.get("manifest_hash"),
            "source_boundary_hash": manifest.get("source_boundary_hash"),
            "doubt_summary": manifest.get("doubt", {}).get("doubt_summary", {}),
            "constraints": manifest.get("constraints", []),
            "revocation": manifest.get("revocation", {}),
        }

        if request.mode in {"inspect", "anchor"}:
            granted["boundary"] = manifest.get("boundary", {})
            granted["lineage"] = manifest.get("lineage", {})
            granted["manifest_path"] = manifest_path

        if request.mode == "read_manifest":
            granted["manifest_path"] = manifest_path

        if request.mode in {"read_artifacts", "export_package"}:
            granted["artifacts"] = decision.granted_artifacts

        if request.mode in {"export_manifest", "export_package"}:
            granted["export_target"] = request.export_target

        if request.mode == "redeem":
            granted["redeem_scope"] = request.scope

        return {
            "kind": "diamond.access_package.v0",
            "state": "granted",
            "diamond_id": manifest.get("diamond_id"),
            "request_hash": request.request_hash,
            "decision_hash": decision.decision_hash,
            "receipt_hash": receipt["receipt_hash"],
            "warnings": decision.warnings,
            "granted": granted,
            "allowed_meanings": decision.allowed_meanings,
            "forbidden_meanings": decision.forbidden_meanings,
            "next_actions": self._next_actions_for(request.mode),
        }

    def _next_actions_for(self, mode: str) -> list[str]:
        if mode == "anchor":
            return [
                "load_boundary",
                "read_doubt_summary",
                "continue_inside_anchor",
                "declare_uncertainty_if_boundary_insufficient",
            ]

        if mode == "inspect":
            return [
                "inspect_identity",
                "inspect_boundary",
                "inspect_constraints",
                "do_not_treat_as_truth",
            ]

        if mode == "read_manifest":
            return [
                "read_manifest",
                "preserve_constraints",
                "preserve_doubt_summary",
                "do_not_mutate",
            ]

        if mode == "read_artifacts":
            return [
                "read_only_granted_artifacts",
                "verify_artifact_hashes",
                "preserve_receipt",
            ]

        if mode in {"export_manifest", "export_package"}:
            return [
                "export_only_to_declared_target",
                "include_constraints",
                "include_revocation_policy",
                "include_access_receipt",
            ]

        if mode == "redeem":
            return [
                "redeem_inside_declared_scope",
                "emit_downstream_receipt",
                "preserve_diamond_boundary",
            ]

        return ["inspect_receipt"]

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(self, package: dict, receipt: dict) -> str:
        decision = receipt["decision"]

        lines = [
            "---",
            "kind: diamond_access",
            f"state: {package['state']}",
            f"diamond_id: {package['diamond_id']}",
            f"request_hash: {package['request_hash']}",
            f"decision_hash: {package['decision_hash']}",
            f"receipt_hash: {package['receipt_hash']}",
            f"mode: {decision['mode']}",
            f"allowed: {str(decision['allowed']).lower()}",
            "---",
            "",
            "# Diamond Access",
            "",
            "> No Diamond is read, exported, copied, shown, anchored, or redeemed without an access receipt.",
            "",
            "## Decision",
            "",
            f"- State: `{package['state']}`",
            f"- Mode: `{decision['mode']}`",
            f"- Allowed: `{str(decision['allowed']).lower()}`",
            f"- Receipt: `{package['receipt_hash']}`",
            "",
        ]

        if decision["blockers"]:
            lines += [
                "## Blockers",
                "",
                *[f"- {b}" for b in decision["blockers"]],
                "",
            ]

        if decision["warnings"]:
            lines += [
                "## Warnings",
                "",
                *[f"- {w}" for w in decision["warnings"]],
                "",
            ]

        lines += [
            "## Allowed meanings",
            "",
            *[f"- {m}" for m in package["allowed_meanings"]],
            "",
            "## Forbidden meanings",
            "",
            *[f"- {m}" for m in package["forbidden_meanings"]],
            "",
            "## Next actions",
            "",
            *[f"- {a}" for a in package["next_actions"]],
            "",
        ]

        return "\n".join(lines)
