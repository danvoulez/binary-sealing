"""Diamond Resolver v0 — find the current safe Diamond for a task.

Core law:
    Resolver does not grant access.
    Resolver does not treat Diamonds as truth.
    Resolver must consult current-state overlays.
    Resolver must not return revoked or superseded Diamonds as current anchors.

Input:
    sealed Diamonds:
        /Minivault/30_diamonds/sealed/<diamond_id>/diamond_manifest.json

    current-state overlays:
        /Minivault/30_diamonds/state_index/<diamond_id>/current_state.json

Output:
    diamond_resolution.json
    index.md
    receipt events
    selected current Diamond candidate, or fallback instruction.

Dependency-free: stdlib only.
"""
from __future__ import annotations

import os
import re
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
    def emit(self, kind: str, payload: dict, actor: str = "diamond_resolver") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "diamond_resolver") -> dict:
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

    if not manifest.get("source_boundary_hash"):
        problems.append("missing_source_boundary_hash")

    if not manifest.get("doubt", {}).get("doubt_summary"):
        problems.append("missing_doubt_summary")

    if not manifest.get("revocation", {}).get("exists"):
        problems.append("missing_revocation_path")

    if not manifest.get("receipts", {}).get("configured"):
        problems.append("missing_receipt_policy")

    return problems

# ---------------------------------------------------------------------------
# State resolver
# ---------------------------------------------------------------------------

class DiamondStateResolver:
    """Reads state overlays.

    No overlay means active.
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
            data = {
                "kind": "diamond.current_state.v0",
                "diamond_id": diamond_id,
                "current_state": "active",
                "last_event_hash": None,
                "successor_diamond_id": None,
                "updated_at": None,
            }
            data["state_hash"] = content_hash(data, "diamond-current-state:")
            return data

        return read_json(path)

# ---------------------------------------------------------------------------
# Doubt
# ---------------------------------------------------------------------------

DOUBT_SEVERITY = {
    "known": 0,
    "safe_to_continue": 0,
    "supported": 1,
    "inferred": 2,
    "stale": 3,
    "missing": 4,
    "contested": 5,
    "policy_blocked": 6,
    "human_required": 7,
    "unsafe_to_act": 8,
}

def max_doubt_severity(doubt_summary: dict) -> int:
    if "max_severity" in doubt_summary:
        try:
            return int(doubt_summary["max_severity"])
        except (TypeError, ValueError):
            return 99

    state = doubt_summary.get("max_state", "missing")
    return DOUBT_SEVERITY.get(state, 99)

# ---------------------------------------------------------------------------
# Request / Candidate / Package
# ---------------------------------------------------------------------------

ACCESS_MODES = {
    "inspect",
    "read_manifest",
    "anchor",
    "read_artifacts",
    "export_manifest",
    "export_package",
    "redeem",
}

@dataclass
class DiamondResolveRequest:
    actor: str
    task: str
    purpose: str

    query_concepts: list[str] = field(default_factory=list)
    allowed_diamond_kinds: list[str] = field(default_factory=lambda: [
        "D.PROJ",
        "D.AUD",
        "D.TRAJ",
        "D.DATA",
        "D.EMB",
    ])

    intended_access_mode: str = "anchor"
    max_doubt_severity: int = DOUBT_SEVERITY["missing"]

    require_current: bool = True
    allow_historical: bool = False
    allow_superseded: bool = False
    allow_revoked: bool = False

    max_candidates: int = 5
    scope: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    @property
    def request_hash(self) -> str:
        return content_hash(self.body(), "diamond-resolve-request:")

@dataclass
class DiamondCandidate:
    diamond_id: str
    diamond_kind: str
    manifest_path: str
    manifest_hash: str
    projection_hash: str
    source_boundary_hash: str
    current_state: str
    successor_diamond_id: Optional[str]

    score: int
    blocked: bool
    blockers: list[str]
    warnings: list[str]
    reasons: list[str]

    concepts: list[str]
    doubt_summary: dict
    access_request_hint: dict

    def body(self) -> dict:
        return asdict(self)

    @property
    def candidate_hash(self) -> str:
        return content_hash(self.body(), "diamond-resolve-candidate:")

    def to_dict(self) -> dict:
        d = self.body()
        d["candidate_hash"] = self.candidate_hash
        return d

@dataclass
class DiamondResolutionPackage:
    request_hash: str
    resolution_state: str

    selected: Optional[dict]
    alternatives: list[dict]

    fallback: dict
    forbidden_meanings: list[str]
    safe_next_actions: list[str]

    created_at: str

    def body(self) -> dict:
        return asdict(self)

    @property
    def resolution_hash(self) -> str:
        return content_hash(self.body(), "diamond-resolution:")

    def to_dict(self) -> dict:
        d = self.body()
        d["resolution_hash"] = self.resolution_hash
        return d

@dataclass
class DiamondResolveResult:
    resolution_hash: str
    resolution_state: str
    selected_diamond_id: Optional[str]
    selected_manifest_path: Optional[str]
    resolution_path: str
    index_path: str
    alternative_count: int
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class DiamondResolveError(Exception):
    pass

class DiamondResolver:
    def __init__(
        self,
        nas_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.nas_root = nas_root
        self.receipts = receipts or NullReceipts()
        self.state_resolver = DiamondStateResolver(nas_root)

    def resolve(
        self,
        request: DiamondResolveRequest,
    ) -> DiamondResolveResult:
        if request.intended_access_mode not in ACCESS_MODES:
            raise DiamondResolveError(f"invalid_access_mode:{request.intended_access_mode}")

        self.receipts.emit(
            "diamond.resolve_started",
            {
                "request_hash": request.request_hash,
                "actor": request.actor,
                "task": request.task,
                "purpose": request.purpose,
                "query_concepts": request.query_concepts,
            },
            actor=request.actor,
        )

        manifests = self._load_sealed_manifests()

        candidates = [
            self._candidate_for_manifest(manifest, path, request)
            for manifest, path in manifests
        ]

        candidates = sorted(
            candidates,
            key=lambda c: (
                c.blocked,
                -c.score,
                c.diamond_id,
            ),
        )

        usable = [c for c in candidates if not c.blocked]

        if usable:
            selected = usable[0]
            alternatives = usable[1:request.max_candidates]
            package = self._package_success(
                request=request,
                selected=selected,
                alternatives=alternatives,
            )
        else:
            alternatives = candidates[:request.max_candidates]
            package = self._package_failure(
                request=request,
                alternatives=alternatives,
                reason="no_current_safe_diamond",
            )

        out_dir = os.path.join(
            self.nas_root,
            "Minivault",
            "40_receipts",
            "diamond_resolution",
            safe_segment(package.resolution_hash),
        )

        resolution_path = os.path.join(out_dir, "diamond_resolution.json")
        index_path = os.path.join(out_dir, "index.md")

        write_json(resolution_path, package.to_dict())
        write_text(index_path, self._render_index_md(package))

        selected_diamond_id = None
        selected_manifest_path = None

        if package.selected:
            selected_diamond_id = package.selected["diamond_id"]
            selected_manifest_path = package.selected["manifest_path"]

        result = DiamondResolveResult(
            resolution_hash=package.resolution_hash,
            resolution_state=package.resolution_state,
            selected_diamond_id=selected_diamond_id,
            selected_manifest_path=selected_manifest_path,
            resolution_path=resolution_path,
            index_path=index_path,
            alternative_count=len(package.alternatives),
            next_actions=package.safe_next_actions,
        )

        self.receipts.emit(
            "diamond.resolve_completed",
            result.to_dict(),
            actor=request.actor,
        )

        return result

    # ---------------------------------------------------------------------
    # Loading
    # ---------------------------------------------------------------------

    def _sealed_root(self) -> str:
        return os.path.join(
            self.nas_root,
            "Minivault",
            "30_diamonds",
            "sealed",
        )

    def _load_sealed_manifests(self) -> list[tuple[dict, str]]:
        root = self._sealed_root()
        if not os.path.exists(root):
            return []

        out: list[tuple[dict, str]] = []

        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name, "diamond_manifest.json")
            if not os.path.exists(path):
                continue

            try:
                out.append((read_json(path), path))
            except json.JSONDecodeError:
                continue

        return out

    # ---------------------------------------------------------------------
    # Candidate construction
    # ---------------------------------------------------------------------

    def _candidate_for_manifest(
        self,
        manifest: dict,
        path: str,
        request: DiamondResolveRequest,
    ) -> DiamondCandidate:
        blockers: list[str] = []
        warnings: list[str] = []
        reasons: list[str] = []
        score = 0

        verification_problems = verify_sealed_manifest(manifest)
        blockers.extend([f"invalid_manifest:{p}" for p in verification_problems])

        diamond_id = manifest.get("diamond_id", "")
        diamond_kind = manifest.get("diamond_kind", "")

        state = self.state_resolver.current_state(diamond_id)
        current_state = state.get("current_state", "active")
        successor_diamond_id = state.get("successor_diamond_id")

        if diamond_kind not in request.allowed_diamond_kinds:
            blockers.append(f"diamond_kind_not_allowed:{diamond_kind}")
        else:
            score += 10
            reasons.append(f"diamond_kind_allowed:{diamond_kind}")

        self._apply_state_rules(
            current_state=current_state,
            successor_diamond_id=successor_diamond_id,
            request=request,
            blockers=blockers,
            warnings=warnings,
            reasons=reasons,
        )

        concepts = self._manifest_concepts(manifest)
        concept_score, concept_reasons = self._concept_score(concepts, request)
        score += concept_score
        reasons.extend(concept_reasons)

        token_score, token_reasons = self._token_score(manifest, request)
        score += token_score
        reasons.extend(token_reasons)

        doubt_summary = manifest.get("doubt", {}).get("doubt_summary", {})
        severity = max_doubt_severity(doubt_summary)

        if severity > request.max_doubt_severity:
            blockers.append(
                f"doubt_too_high:{severity}>{request.max_doubt_severity}"
            )
        else:
            score += max(0, 20 - severity * 4)
            reasons.append(f"doubt_within_limit:{severity}")

        if manifest.get("policy", {}).get("truth_policy", {}).get("is_truth") is True:
            warnings.append("truth_policy_claims_truth_unexpectedly")
            score -= 20
        else:
            score += 5
            reasons.append("truth_policy_safe")

        if manifest.get("receipts", {}).get("configured"):
            score += 5
            reasons.append("receipts_configured")
        else:
            blockers.append("receipt_policy_missing")

        if manifest.get("revocation", {}).get("exists"):
            score += 5
            reasons.append("revocation_path_exists")
        else:
            blockers.append("revocation_path_missing")

        if manifest.get("boundary", {}).get("source_boundary_hash") or manifest.get("source_boundary_hash"):
            score += 5
            reasons.append("boundary_present")
        else:
            blockers.append("boundary_missing")

        access_request_hint = self._access_request_hint(manifest, request)

        return DiamondCandidate(
            diamond_id=diamond_id,
            diamond_kind=diamond_kind,
            manifest_path=path,
            manifest_hash=manifest.get("manifest_hash", ""),
            projection_hash=manifest.get("projection_hash", ""),
            source_boundary_hash=manifest.get("source_boundary_hash", ""),
            current_state=current_state,
            successor_diamond_id=successor_diamond_id,

            score=score,
            blocked=bool(blockers),
            blockers=blockers,
            warnings=warnings,
            reasons=reasons,

            concepts=concepts,
            doubt_summary=doubt_summary,
            access_request_hint=access_request_hint,
        )

    def _apply_state_rules(
        self,
        current_state: str,
        successor_diamond_id: Optional[str],
        request: DiamondResolveRequest,
        blockers: list[str],
        warnings: list[str],
        reasons: list[str],
    ) -> None:
        if current_state == "active":
            reasons.append("current_state_active")
            return

        if current_state == "revoked":
            if not request.allow_revoked:
                blockers.append("diamond_revoked")
            else:
                warnings.append("using_revoked_diamond_allowed_by_request")
            return

        if current_state == "superseded":
            if not request.allow_superseded:
                blockers.append(f"diamond_superseded:successor:{successor_diamond_id}")
            else:
                warnings.append(f"using_superseded_diamond:successor:{successor_diamond_id}")
            return

        if current_state == "historical":
            if not request.allow_historical:
                blockers.append("diamond_historical_not_current")
            else:
                warnings.append("using_historical_diamond_allowed_by_request")
            return

        blockers.append(f"unknown_current_state:{current_state}")

    def _manifest_concepts(self, manifest: dict) -> list[str]:
        concepts = set()

        scope = manifest.get("boundary", {}).get("scope", {})
        for c in scope.get("concepts", []):
            concepts.add(c)

        lineage = manifest.get("lineage", {})
        for c in lineage.get("concepts", []):
            concepts.add(c)

        aux = manifest.get("aux", {})
        for c in aux.get("concepts", []):
            concepts.add(c)

        # Fall back to title/purpose token concepts.
        for token in self._tokens(
            manifest.get("title", "") + " " + manifest.get("purpose", "")
        ):
            concepts.add(token)

        return sorted(concepts)

    def _concept_score(
        self,
        concepts: list[str],
        request: DiamondResolveRequest,
    ) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []

        query = set(request.query_concepts)
        available = set(concepts)

        if not query:
            return 0, ["no_query_concepts"]

        overlap = sorted(query.intersection(available))

        if overlap:
            score += 15 * len(overlap)
            reasons.append(f"concept_overlap:{','.join(overlap)}")
        else:
            score -= 10
            reasons.append("no_concept_overlap")

        return score, reasons

    def _token_score(
        self,
        manifest: dict,
        request: DiamondResolveRequest,
    ) -> tuple[int, list[str]]:
        haystack = " ".join([
            manifest.get("title", ""),
            manifest.get("purpose", ""),
            json.dumps(manifest.get("boundary", {}).get("scope", {}), ensure_ascii=False),
            json.dumps(manifest.get("constraints", []), ensure_ascii=False),
        ])

        task_tokens = self._tokens(request.task + " " + request.purpose)
        manifest_tokens = self._tokens(haystack)

        overlap = sorted(task_tokens.intersection(manifest_tokens))

        if not overlap:
            return 0, ["no_task_token_overlap"]

        return min(20, 3 * len(overlap)), [f"task_token_overlap:{','.join(overlap[:8])}"]

    def _tokens(self, text: str) -> set[str]:
        stop = {
            "the", "and", "for", "with", "from", "this", "that", "into",
            "what", "when", "where", "why", "how", "shall", "should",
            "agent", "operator", "system", "need", "needs", "safe",
            "current", "diamond", "projection",
        }
        tokens = re.findall(r"[a-zA-Z0-9_]{3,}", text.lower())
        return {t for t in tokens if t not in stop}

    def _access_request_hint(
        self,
        manifest: dict,
        request: DiamondResolveRequest,
    ) -> dict:
        return {
            "access_gate_required": True,
            "sealed_manifest_path": None,  # filled by candidate caller context
            "mode": request.intended_access_mode,
            "actor": {
                "actor_id": request.actor,
                "roles": request.scope.get("actor_roles", []),
            },
            "purpose": request.purpose,
            "reason": (
                f"Resolver selected {manifest.get('diamond_id')} for task: "
                f"{request.task}"
            ),
            "scope": {
                "resolver_request_hash": request.request_hash,
                "source_boundary_hash": manifest.get("source_boundary_hash"),
                "diamond_id": manifest.get("diamond_id"),
            },
        }

    # ---------------------------------------------------------------------
    # Packaging
    # ---------------------------------------------------------------------

    def _package_success(
        self,
        request: DiamondResolveRequest,
        selected: DiamondCandidate,
        alternatives: list[DiamondCandidate],
    ) -> DiamondResolutionPackage:
        selected_dict = selected.to_dict()
        selected_dict["access_request_hint"]["sealed_manifest_path"] = selected.manifest_path

        return DiamondResolutionPackage(
            request_hash=request.request_hash,
            resolution_state="resolved_to_current_diamond",
            selected=selected_dict,
            alternatives=[a.to_dict() for a in alternatives],
            fallback={},
            forbidden_meanings=[
                "resolver_does_not_grant_access",
                "must_call_access_gate_before_use",
                "must_not_treat_diamond_as_raw_truth",
                "must_not_ignore_doubt_summary",
                "must_not_expand_beyond_source_boundary",
                "must_not_use_revoked_or_superseded_diamonds_as_current",
            ],
            safe_next_actions=[
                "call_diamond_access_gate",
                "request_access_with_hint",
                "load_only_granted_access_package",
                "continue_inside_diamond_boundary",
                "fall_back_to_anchor_finder_if_access_denied",
            ],
            created_at=utc_now(),
        )

    def _package_failure(
        self,
        request: DiamondResolveRequest,
        alternatives: list[DiamondCandidate],
        reason: str,
    ) -> DiamondResolutionPackage:
        return DiamondResolutionPackage(
            request_hash=request.request_hash,
            resolution_state="no_current_safe_diamond",
            selected=None,
            alternatives=[a.to_dict() for a in alternatives],
            fallback={
                "reason": reason,
                "recommended_engine": "anchor_finder",
                "next_process": "build_or_find_projection_anchor",
                "allowed_fallbacks": [
                    "anchor_finder",
                    "projection_builder",
                    "sealability_test_after_review",
                ],
            },
            forbidden_meanings=[
                "must_not_improvise_diamond",
                "must_not_use_blocked_candidate",
                "must_not_ignore_revocation_or_supersession",
                "must_not_grant_access_without_access_gate",
            ],
            safe_next_actions=[
                "call_anchor_finder",
                "build_new_projection_if_needed",
                "review_alternative_candidates",
                "declare_no_current_diamond",
            ],
            created_at=utc_now(),
        )

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(self, package: DiamondResolutionPackage) -> str:
        data = package.to_dict()

        lines = [
            "---",
            "kind: diamond_resolution",
            f"resolution_hash: {data['resolution_hash']}",
            f"resolution_state: {package.resolution_state}",
            f"request_hash: {package.request_hash}",
            f"created_at: {package.created_at}",
            "---",
            "",
            "# Diamond Resolution",
            "",
            "> Resolver finds the current safe Diamond. It does not grant access.",
            "",
            "## State",
            "",
            f"- Resolution state: `{package.resolution_state}`",
            f"- Resolution hash: `{data['resolution_hash']}`",
            "",
        ]

        if package.selected:
            selected = package.selected
            lines += [
                "## Selected Diamond",
                "",
                f"- Diamond ID: `{selected['diamond_id']}`",
                f"- Kind: `{selected['diamond_kind']}`",
                f"- Current state: `{selected['current_state']}`",
                f"- Manifest hash: `{selected['manifest_hash']}`",
                f"- Projection: `{selected['projection_hash']}`",
                f"- Boundary: `{selected['source_boundary_hash']}`",
                f"- Score: `{selected['score']}`",
                f"- Manifest path: `{selected['manifest_path']}`",
                "",
                "## Required access request",
                "",
                "```json",
                json.dumps(
                    selected["access_request_hint"],
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                "```",
                "",
                "## Doubt summary",
                "",
                "```json",
                json.dumps(
                    selected["doubt_summary"],
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                "```",
                "",
            ]
        else:
            lines += [
                "## No current safe Diamond",
                "",
                "```json",
                json.dumps(
                    package.fallback,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                "```",
                "",
            ]

        lines += [
            "## Forbidden meanings",
            "",
            *[f"- {m}" for m in package.forbidden_meanings],
            "",
            "## Safe next actions",
            "",
            *[f"- {a}" for a in package.safe_next_actions],
            "",
            "## Alternatives",
            "",
        ]

        if package.alternatives:
            for alt in package.alternatives:
                lines.append(
                    f"- `{alt['diamond_id']}` — score=`{alt['score']}` — "
                    f"blocked=`{str(alt['blocked']).lower()}` — "
                    f"state=`{alt['current_state']}` — "
                    f"blockers=`{alt['blockers']}`"
                )
        else:
            lines.append("- None")

        lines.append("")
        return "\n".join(lines)
