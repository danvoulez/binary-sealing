"""Diamond Revocation / Supersession Gate v0.

Core law:
    Do not mutate sealed Diamonds in place.
    Revocation and supersession are state events over a sealed Diamond.
    A revoked Diamond is still historical evidence.
    A superseded Diamond is no longer the current safe anchor.

Input:
    sealed diamond_manifest.json
    StateChangeRequest
    StateChangeAuthority
    optional successor sealed diamond_manifest.json

Output:
    diamond.state_event.v0
    current_state.json
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
    def emit(self, kind: str, payload: dict, actor: str = "diamond_state_gate") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "diamond_state_gate") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Manifest verification
# ---------------------------------------------------------------------------

COMPUTED_MANIFEST_FIELDS = {
    "manifest_hash",
    "diamond_candidate_id",
    "diamond_id",
    "sealed_manifest_hash",
}

def manifest_identity_body(manifest: dict) -> dict:
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

def verify_sealed_manifest(manifest: dict) -> list[str]:
    problems: list[str] = []

    if manifest.get("kind") != "diamond.manifest.v0":
        problems.append(f"wrong_manifest_kind:{manifest.get('kind')}")

    if manifest.get("state") != "sealed":
        problems.append(f"manifest_not_sealed:{manifest.get('state')}")

    actual_hash = manifest.get("manifest_hash")
    expected_hash = expected_manifest_hash(manifest)

    if actual_hash != expected_hash:
        problems.append(f"manifest_hash_mismatch:{actual_hash}!={expected_hash}")

    actual_id = manifest.get("diamond_id")
    expected_id = expected_diamond_id(manifest)

    if actual_id != expected_id:
        problems.append(f"diamond_id_mismatch:{actual_id}!={expected_id}")

    if not manifest.get("signatures"):
        problems.append("missing_seal_signature")

    if not manifest.get("revocation", {}).get("exists"):
        problems.append("revocation_path_missing")

    if not manifest.get("receipts", {}).get("configured"):
        problems.append("receipt_policy_missing")

    return problems

# ---------------------------------------------------------------------------
# Authority and request
# ---------------------------------------------------------------------------

STATE_MODES = {
    "revoke",
    "supersede",
    "mark_historical",
    "affirm_current",
}

CURRENT_STATES = {
    "active",
    "revoked",
    "superseded",
    "historical",
}

TERMINAL_STATES = {
    "revoked",
}

@dataclass
class StateChangeAuthority:
    authority_id: str
    name: str
    role: str
    allowed_modes: list[str] = field(default_factory=lambda: sorted(STATE_MODES))
    authority_level: str = "diamond_state_authority"
    public_key_ref: Optional[str] = None
    policy_ref: Optional[str] = None

    def body(self) -> dict:
        return asdict(self)

    @property
    def authority_hash(self) -> str:
        return content_hash(self.body(), "state-authority:")

    def can_perform(self, mode: str) -> bool:
        return (
            self.authority_level == "diamond_state_authority"
            and mode in self.allowed_modes
        )

@dataclass
class StateChangeRequest:
    mode: str
    reason: str
    evidence_refs: list[str] = field(default_factory=list)

    # Required for supersession.
    successor_manifest_path: Optional[str] = None
    successor_diamond_id: Optional[str] = None

    # Optional process metadata.
    effective_at: Optional[str] = None
    note: str = ""
    scope: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    @property
    def request_hash(self) -> str:
        return content_hash(self.body(), "diamond-state-request:")

@dataclass
class DiamondStateResult:
    diamond_id: str
    previous_state: str
    new_state: str
    mode: str
    state_event_hash: str
    state_event_path: str
    current_state_path: str
    index_path: str
    receipt_hash: str
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# State event
# ---------------------------------------------------------------------------

@dataclass
class DiamondStateEvent:
    kind: str
    diamond_id: str
    diamond_kind: str
    sealed_manifest_hash: str
    source_boundary_hash: str

    previous_state: str
    new_state: str
    mode: str

    request_hash: str
    reason: str
    evidence_refs: list[str]

    authority_id: str
    authority_hash: str

    successor_diamond_id: Optional[str]
    successor_manifest_hash: Optional[str]

    created_at: str
    effective_at: str

    warnings: list[str]
    constraints: list[str]
    note: str = ""

    def body(self) -> dict:
        return asdict(self)

    @property
    def state_event_hash(self) -> str:
        return content_hash(self.body(), "diamond-state-event:")

    def to_dict(self) -> dict:
        d = self.body()
        d["state_event_hash"] = self.state_event_hash
        return d

# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class DiamondStateResolver:
    """Reads current state overlays.

    Default state is active when no state overlay exists.
    """

    def __init__(self, nas_root: str):
        self.nas_root = nas_root

    def current_state_path(self, diamond_id: str) -> str:
        return os.path.join(
            self.nas_root,
            "Minivault",
            "30_diamonds",
            "state_index",
            safe_segment(diamond_id),
            "current_state.json",
        )

    def current_state(self, diamond_id: str) -> dict:
        path = self.current_state_path(diamond_id)

        if not os.path.exists(path):
            return {
                "kind": "diamond.current_state.v0",
                "diamond_id": diamond_id,
                "current_state": "active",
                "last_event_hash": None,
                "successor_diamond_id": None,
                "updated_at": None,
                "state_hash": content_hash(
                    {
                        "diamond_id": diamond_id,
                        "current_state": "active",
                        "last_event_hash": None,
                    },
                    "diamond-current-state:",
                ),
            }

        return read_json(path)

# ---------------------------------------------------------------------------
# State Gate
# ---------------------------------------------------------------------------

class DiamondStateError(Exception):
    pass

class DiamondStateGate:
    def __init__(
        self,
        nas_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.nas_root = nas_root
        self.receipts = receipts or NullReceipts()
        self.resolver = DiamondStateResolver(nas_root)

    def change_state(
        self,
        sealed_manifest_path: str,
        request: StateChangeRequest,
        authority: StateChangeAuthority,
        actor: str = "diamond_state_gate",
    ) -> DiamondStateResult:
        manifest = read_json(sealed_manifest_path)

        self.receipts.emit(
            "diamond.state_change_requested",
            {
                "sealed_manifest_path": sealed_manifest_path,
                "request_hash": request.request_hash,
                "mode": request.mode,
                "authority_id": authority.authority_id,
                "authority_hash": authority.authority_hash,
            },
            actor=actor,
        )

        self._validate_request(request)
        self._validate_authority(request, authority)
        self._validate_manifest(manifest)

        diamond_id = manifest["diamond_id"]
        previous = self.resolver.current_state(diamond_id)
        previous_state = previous["current_state"]

        self._validate_transition(previous_state, request.mode)

        successor = None
        if request.mode == "supersede":
            successor = self._load_and_validate_successor(request, diamond_id)

        new_state = self._new_state_for_mode(request.mode)
        effective_at = request.effective_at or utc_now()

        state_event = DiamondStateEvent(
            kind="diamond.state_event.v0",
            diamond_id=diamond_id,
            diamond_kind=manifest["diamond_kind"],
            sealed_manifest_hash=manifest["manifest_hash"],
            source_boundary_hash=manifest["source_boundary_hash"],

            previous_state=previous_state,
            new_state=new_state,
            mode=request.mode,

            request_hash=request.request_hash,
            reason=request.reason,
            evidence_refs=request.evidence_refs,

            authority_id=authority.authority_id,
            authority_hash=authority.authority_hash,

            successor_diamond_id=successor.get("diamond_id") if successor else request.successor_diamond_id,
            successor_manifest_hash=successor.get("manifest_hash") if successor else None,

            created_at=utc_now(),
            effective_at=effective_at,

            warnings=self._warnings_for(request.mode),
            constraints=self._constraints_for(request.mode),
            note=request.note,
        )

        event_dict = state_event.to_dict()

        out_dir = os.path.join(
            self.nas_root,
            "Minivault",
            "40_receipts",
            "diamond_state",
            safe_segment(diamond_id),
            safe_segment(state_event.state_event_hash),
        )

        state_event_path = os.path.join(out_dir, "state_event.json")
        index_path = os.path.join(out_dir, "index.md")

        current_state = self._build_current_state(
            diamond_id=diamond_id,
            manifest=manifest,
            state_event=state_event,
        )

        current_state_path = self.resolver.current_state_path(diamond_id)

        receipt = self._build_receipt(
            manifest=manifest,
            state_event=state_event,
            sealed_manifest_path=sealed_manifest_path,
            current_state_path=current_state_path,
        )

        receipt_path = os.path.join(out_dir, "state_receipt.json")

        write_json(state_event_path, event_dict)
        write_json(receipt_path, receipt)
        write_json(current_state_path, current_state)
        write_text(index_path, self._render_index_md(event_dict, current_state, receipt))

        result = DiamondStateResult(
            diamond_id=diamond_id,
            previous_state=previous_state,
            new_state=new_state,
            mode=request.mode,
            state_event_hash=state_event.state_event_hash,
            state_event_path=state_event_path,
            current_state_path=current_state_path,
            index_path=index_path,
            receipt_hash=receipt["receipt_hash"],
            next_actions=self._next_actions(new_state),
        )

        self.receipts.emit(
            "diamond.state_changed",
            result.to_dict(),
            actor=actor,
        )

        return result

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------

    def _validate_request(self, request: StateChangeRequest) -> None:
        if request.mode not in STATE_MODES:
            raise DiamondStateError(f"invalid_state_mode:{request.mode}")

        if not request.reason.strip():
            raise DiamondStateError("state_change_requires_reason")

        if request.mode in {"revoke", "supersede"} and not request.evidence_refs:
            raise DiamondStateError(f"{request.mode}_requires_evidence_refs")

        if request.mode == "supersede":
            if not request.successor_manifest_path and not request.successor_diamond_id:
                raise DiamondStateError("supersession_requires_successor")

    def _validate_authority(
        self,
        request: StateChangeRequest,
        authority: StateChangeAuthority,
    ) -> None:
        if not authority.can_perform(request.mode):
            raise DiamondStateError(
                f"authority_cannot_perform:{authority.authority_id}:{request.mode}"
            )

    def _validate_manifest(self, manifest: dict) -> None:
        problems = verify_sealed_manifest(manifest)
        if problems:
            raise DiamondStateError(f"sealed_manifest_invalid:{problems}")

    def _validate_transition(self, previous_state: str, mode: str) -> None:
        if previous_state in TERMINAL_STATES:
            raise DiamondStateError(f"terminal_state_cannot_transition:{previous_state}")

        if mode == "affirm_current" and previous_state != "active":
            raise DiamondStateError(f"cannot_affirm_non_active:{previous_state}")

        if mode == "supersede" and previous_state == "superseded":
            raise DiamondStateError("already_superseded")

    def _load_and_validate_successor(
        self,
        request: StateChangeRequest,
        current_diamond_id: str,
    ) -> Optional[dict]:
        if not request.successor_manifest_path:
            return None

        successor = read_json(request.successor_manifest_path)
        problems = verify_sealed_manifest(successor)

        if problems:
            raise DiamondStateError(f"successor_manifest_invalid:{problems}")

        if successor["diamond_id"] == current_diamond_id:
            raise DiamondStateError("diamond_cannot_supersede_itself")

        if request.successor_diamond_id and request.successor_diamond_id != successor["diamond_id"]:
            raise DiamondStateError(
                f"successor_id_mismatch:{request.successor_diamond_id}!={successor['diamond_id']}"
            )

        successor_state = self.resolver.current_state(successor["diamond_id"])
        if successor_state["current_state"] in {"revoked", "superseded"}:
            raise DiamondStateError(
                f"successor_not_current:{successor['diamond_id']}:{successor_state['current_state']}"
            )

        return successor

    # ---------------------------------------------------------------------
    # State construction
    # ---------------------------------------------------------------------

    def _new_state_for_mode(self, mode: str) -> str:
        if mode == "revoke":
            return "revoked"

        if mode == "supersede":
            return "superseded"

        if mode == "mark_historical":
            return "historical"

        if mode == "affirm_current":
            return "active"

        raise DiamondStateError(f"invalid_state_mode:{mode}")

    def _warnings_for(self, mode: str) -> list[str]:
        base = [
            "state event does not mutate sealed manifest",
            "historical evidence must remain readable with receipt",
        ]

        if mode == "revoke":
            base.append("revoked diamond must not be used as current anchor")

        if mode == "supersede":
            base.append("superseded diamond must redirect current-anchor use to successor")

        if mode == "mark_historical":
            base.append("historical diamond may be cited as history, not current state")

        return base

    def _constraints_for(self, mode: str) -> list[str]:
        base = [
            "preserve_original_sealed_manifest",
            "preserve_state_event",
            "preserve_access_receipts",
            "access_gate_must_consult_current_state",
        ]

        if mode == "revoke":
            base.extend([
                "deny_anchor_access_unless_historical_review",
                "deny_export_unless_authorized_audit",
            ])

        if mode == "supersede":
            base.extend([
                "redirect_current_anchor_to_successor",
                "allow_historical_access_with_warning",
            ])

        return base

    def _build_current_state(
        self,
        diamond_id: str,
        manifest: dict,
        state_event: DiamondStateEvent,
    ) -> dict:
        data = {
            "kind": "diamond.current_state.v0",
            "diamond_id": diamond_id,
            "diamond_kind": manifest["diamond_kind"],
            "current_state": state_event.new_state,
            "last_event_hash": state_event.state_event_hash,
            "last_mode": state_event.mode,
            "successor_diamond_id": state_event.successor_diamond_id,
            "successor_manifest_hash": state_event.successor_manifest_hash,
            "source_boundary_hash": manifest["source_boundary_hash"],
            "sealed_manifest_hash": manifest["manifest_hash"],
            "updated_at": utc_now(),
            "warning": "Current state is an overlay. The sealed manifest is immutable historical evidence.",
        }

        data["state_hash"] = content_hash(data, "diamond-current-state:")
        return data

    def _build_receipt(
        self,
        manifest: dict,
        state_event: DiamondStateEvent,
        sealed_manifest_path: str,
        current_state_path: str,
    ) -> dict:
        receipt = {
            "kind": "diamond.state_receipt.v0",
            "diamond_id": manifest["diamond_id"],
            "diamond_kind": manifest["diamond_kind"],
            "sealed_manifest_hash": manifest["manifest_hash"],
            "source_boundary_hash": manifest["source_boundary_hash"],
            "state_event_hash": state_event.state_event_hash,
            "previous_state": state_event.previous_state,
            "new_state": state_event.new_state,
            "mode": state_event.mode,
            "authority_id": state_event.authority_id,
            "authority_hash": state_event.authority_hash,
            "successor_diamond_id": state_event.successor_diamond_id,
            "sealed_manifest_path": sealed_manifest_path,
            "current_state_path": current_state_path,
            "created_at": utc_now(),
            "warning": "State receipt records revocation/supersession. It does not delete history.",
        }

        receipt["receipt_hash"] = content_hash(receipt, "diamond-state-receipt:")
        return receipt

    def _next_actions(self, new_state: str) -> list[str]:
        if new_state == "revoked":
            return [
                "deny_current_anchor_access",
                "allow_historical_audit_access_only",
                "notify_dependent_anchors",
                "build_replacement_projection_if_needed",
            ]

        if new_state == "superseded":
            return [
                "redirect_current_anchor_to_successor",
                "allow_historical_access_with_warning",
                "update_cerebro_current_index",
                "notify_dependent_anchors",
            ]

        if new_state == "historical":
            return [
                "allow_historical_access_with_warning",
                "do_not_use_as_current_anchor",
                "update_cerebro_current_index",
            ]

        return [
            "remain_current",
            "access_gate_must_still_emit_receipts",
        ]

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(
        self,
        event: dict,
        current_state: dict,
        receipt: dict,
    ) -> str:
        lines = [
            "---",
            "kind: diamond_state_event",
            f"diamond_id: {event['diamond_id']}",
            f"state_event_hash: {event['state_event_hash']}",
            f"previous_state: {event['previous_state']}",
            f"new_state: {event['new_state']}",
            f"mode: {event['mode']}",
            f"authority_id: {event['authority_id']}",
            f"created_at: {event['created_at']}",
            "---",
            "",
            f"# Diamond State Event — {event['mode']}",
            "",
            "> Revocation and supersession do not mutate the sealed Diamond. They create a state overlay.",
            "",
            "## State transition",
            "",
            f"- Diamond: `{event['diamond_id']}`",
            f"- Previous state: `{event['previous_state']}`",
            f"- New state: `{event['new_state']}`",
            f"- Event hash: `{event['state_event_hash']}`",
            f"- Receipt hash: `{receipt['receipt_hash']}`",
            "",
            "## Reason",
            "",
            event["reason"],
            "",
            "## Evidence refs",
            "",
        ]

        if event["evidence_refs"]:
            lines.extend([f"- `{e}`" for e in event["evidence_refs"]])
        else:
            lines.append("- None")

        if event.get("successor_diamond_id"):
            lines += [
                "",
                "## Successor",
                "",
                f"- Successor Diamond: `{event['successor_diamond_id']}`",
                f"- Successor manifest hash: `{event.get('successor_manifest_hash')}`",
            ]

        lines += [
            "",
            "## Constraints",
            "",
            *[f"- {c}" for c in event["constraints"]],
            "",
            "## Current state pointer",
            "",
            "```json",
            json.dumps(current_state, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
        ]

        return "\n".join(lines)
