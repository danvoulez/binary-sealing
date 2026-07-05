"""Anchor Finder v0 - purple engine for lost-agent recovery.

Core law:
    An anchor is not truth.
    An anchor is a safe place to stand.
    If no safe anchor exists, the agent must declare insufficient grounding.

Input:
    Cerebro active projections:
        /Cerebro/60_projections/active/<proj_hash>/projection.json

Optional input:
    Cerebro source index:
        /Cerebro/00_index/source_index.ndjson

Output:
    anchor.json
    index.md
    receipt events
    selected anchor package with boundary, doubt, allowed meanings,
    forbidden meanings, and safe next actions.

Dependency-free: stdlib only.
"""
from __future__ import annotations

import os
import re
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

def read_ndjson(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []

    out: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:120] or "unknown"

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "anchor_finder") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "anchor_finder") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

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
# Request / Candidate / Result
# ---------------------------------------------------------------------------

@dataclass
class AnchorRequest:
    """Request for a safe anchor.

    This object describes the agent's lost state and what kind of support it
    needs. The finder does not answer the task. It only selects a safe boundary.
    """

    actor: str
    task: str
    purpose: str
    query_concepts: list[str] = field(default_factory=list)
    allowed_lens_ids: list[str] = field(default_factory=list)
    max_doubt_severity: int = DOUBT_SEVERITY["missing"]
    allow_policy_blockers: bool = False
    allow_human_review_required: bool = True
    max_candidates: int = 5
    scope: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    @property
    def request_hash(self) -> str:
        return content_hash(self.body(), "anchor-request:")

@dataclass
class AnchorCandidate:
    anchor_kind: str
    anchor_ref: str
    path: str
    projection_hash: str
    source_boundary_hash: str
    lens_id: str
    score: int
    blocked: bool
    reasons: list[str]
    blockers: list[str]
    concepts: list[str]
    doubt_summary: dict
    policy_blockers: list[str]
    safe_next_actions: list[str]

    @property
    def anchor_id(self) -> str:
        return content_hash(
            {
                "anchor_kind": self.anchor_kind,
                "anchor_ref": self.anchor_ref,
                "source_boundary_hash": self.source_boundary_hash,
                "lens_id": self.lens_id,
            },
            "anchor:",
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["anchor_id"] = self.anchor_id
        return d

@dataclass
class AnchorPackage:
    request_hash: str
    anchor_state: str
    selected_anchor: Optional[dict]
    alternatives: list[dict]
    boundary: dict
    allowed_meanings: list[str]
    forbidden_meanings: list[str]
    safe_next_actions: list[str]
    no_anchor_reason: Optional[str] = None
    created_at: str = ""

    def body(self) -> dict:
        return asdict(self)

    @property
    def package_hash(self) -> str:
        return content_hash(self.body(), "anchor-package:")

    def to_dict(self) -> dict:
        d = self.body()
        d["package_hash"] = self.package_hash
        return d

@dataclass
class AnchorFindResult:
    package_hash: str
    anchor_state: str
    anchor_path: str
    index_path: str
    selected_anchor_id: Optional[str]
    alternative_count: int
    safe_next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Anchor Finder
# ---------------------------------------------------------------------------

class AnchorFindError(Exception):
    pass

class AnchorFinder:
    def __init__(
        self,
        cerebro_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.cerebro_root = cerebro_root
        self.receipts = receipts or NullReceipts()

    def find(
        self,
        request: AnchorRequest,
    ) -> AnchorFindResult:
        self.receipts.emit(
            "anchor.find_started",
            {
                "request_hash": request.request_hash,
                "actor": request.actor,
                "task": request.task,
                "purpose": request.purpose,
            },
            actor=request.actor,
        )

        sources_by_id = self._load_source_index()
        projections = self._load_active_projections()

        candidates = [
            self._candidate_for_projection(p, path, sources_by_id, request)
            for p, path in projections
        ]

        candidates = sorted(
            candidates,
            key=lambda c: (c.blocked, -c.score, c.projection_hash),
        )

        usable = [c for c in candidates if not c.blocked]

        if usable:
            selected = usable[0]
            alternatives = usable[1:request.max_candidates]
            package = self._package_success(request, selected, alternatives)
        else:
            alternatives = candidates[:request.max_candidates]
            package = self._package_failure(
                request=request,
                alternatives=alternatives,
                reason="no_safe_anchor",
            )

        out_dir = os.path.join(
            self.cerebro_root,
            "80_agent_context",
            "anchors",
            package.package_hash,
        )

        anchor_path = os.path.join(out_dir, "anchor.json")
        index_path = os.path.join(out_dir, "index.md")

        write_json(anchor_path, package.to_dict())
        write_text(index_path, self._render_index_md(package))

        selected_anchor_id = None
        if package.selected_anchor:
            selected_anchor_id = package.selected_anchor["anchor_id"]

        result = AnchorFindResult(
            package_hash=package.package_hash,
            anchor_state=package.anchor_state,
            anchor_path=anchor_path,
            index_path=index_path,
            selected_anchor_id=selected_anchor_id,
            alternative_count=len(package.alternatives),
            safe_next_actions=package.safe_next_actions,
        )

        self.receipts.emit(
            "anchor.find_completed",
            result.to_dict(),
            actor=request.actor,
        )

        return result

    # ---------------------------------------------------------------------
    # Loading
    # ---------------------------------------------------------------------

    def _load_source_index(self) -> dict[str, dict]:
        path = os.path.join(self.cerebro_root, "00_index", "source_index.ndjson")
        rows = read_ndjson(path)
        return {
            r["source_record_id"]: r
            for r in rows
            if "source_record_id" in r
        }

    def _load_active_projections(self) -> list[tuple[dict, str]]:
        root = os.path.join(self.cerebro_root, "60_projections", "active")
        if not os.path.exists(root):
            return []

        out: list[tuple[dict, str]] = []

        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name, "projection.json")
            if os.path.exists(path):
                try:
                    out.append((read_json(path), path))
                except json.JSONDecodeError:
                    continue

        return out

    # ---------------------------------------------------------------------
    # Candidate scoring
    # ---------------------------------------------------------------------

    def _candidate_for_projection(
        self,
        projection: dict,
        path: str,
        sources_by_id: dict[str, dict],
        request: AnchorRequest,
    ) -> AnchorCandidate:
        reasons: list[str] = []
        blockers: list[str] = []
        score = 0

        projection_hash = projection.get("projection_hash", "")
        source_boundary_hash = projection.get("source_boundary_hash", "")
        lens_id = projection.get("lens_id", "")
        source_records = projection.get("source_records", [])

        concepts = self._projection_concepts(projection, sources_by_id)
        query_concepts = set(request.query_concepts)
        projection_concepts = set(concepts)

        if request.allowed_lens_ids:
            if lens_id in request.allowed_lens_ids:
                score += 20
                reasons.append(f"lens_allowed:{lens_id}")
            else:
                blockers.append(f"lens_not_allowed:{lens_id}")

        overlap = sorted(query_concepts.intersection(projection_concepts))
        if overlap:
            score += 10 * len(overlap)
            reasons.append(f"concept_overlap:{','.join(overlap)}")

        task_tokens = self._tokens(request.task + " " + request.purpose)
        concept_tokens = set()
        for concept in concepts:
            concept_tokens.update(self._tokens(concept.replace("_", " ")))

        token_overlap = sorted(task_tokens.intersection(concept_tokens))
        if token_overlap:
            score += min(15, 3 * len(token_overlap))
            reasons.append(f"task_token_overlap:{','.join(token_overlap[:8])}")

        if source_records:
            score += min(10, len(source_records))
            reasons.append(f"source_count:{len(source_records)}")
        else:
            blockers.append("empty_source_boundary")

        doubt_summary = projection.get("doubt_summary", {})
        severity = max_doubt_severity(doubt_summary)

        score -= severity * 4

        if severity > request.max_doubt_severity:
            blockers.append(
                f"doubt_too_high:{severity}>{request.max_doubt_severity}"
            )
        else:
            reasons.append(f"doubt_within_limit:{severity}")

        policy_blockers = projection.get("policy_blockers", [])

        hard_policy_blockers = [
            b for b in policy_blockers
            if not (
                request.allow_human_review_required
                and b == "human_review_required_before_anchor_or_seal"
            )
        ]

        if hard_policy_blockers and not request.allow_policy_blockers:
            blockers.extend([f"policy_blocker:{b}" for b in hard_policy_blockers])
            score -= 25 * len(hard_policy_blockers)
        elif policy_blockers:
            reasons.append("policy_blockers_present_but_allowed")

        safe_next_actions = projection.get("safe_next_actions", [])
        if "do_not_treat_as_truth" in safe_next_actions:
            score += 5
            reasons.append("contains_truth_warning")

        if "candidate_anchor" in safe_next_actions:
            score += 15
            reasons.append("projection_allows_candidate_anchor")

        if projection.get("meta", {}).get("is_projection") is True:
            score += 5
            reasons.append("projection_marker_present")
        else:
            blockers.append("missing_projection_marker")

        blocked = bool(blockers)

        return AnchorCandidate(
            anchor_kind="projection",
            anchor_ref=projection_hash,
            path=path,
            projection_hash=projection_hash,
            source_boundary_hash=source_boundary_hash,
            lens_id=lens_id,
            score=score,
            blocked=blocked,
            reasons=reasons,
            blockers=blockers,
            concepts=concepts,
            doubt_summary=doubt_summary,
            policy_blockers=policy_blockers,
            safe_next_actions=safe_next_actions,
        )

    def _projection_concepts(
        self,
        projection: dict,
        sources_by_id: dict[str, dict],
    ) -> list[str]:
        concepts = set()

        scope = projection.get("scope", {})
        for concept in scope.get("concepts", []):
            concepts.add(concept)

        for source_id in projection.get("source_records", []):
            source = sources_by_id.get(source_id, {})
            for concept in source.get("concepts", []):
                concepts.add(concept)

        return sorted(concepts)

    def _tokens(self, text: str) -> set[str]:
        stop = {
            "the", "and", "for", "with", "from", "this", "that", "into",
            "what", "when", "where", "why", "how", "shall", "should",
            "agent", "operator", "system", "need", "needs",
        }
        tokens = re.findall(r"[a-zA-Z0-9_]{3,}", text.lower())
        return {t for t in tokens if t not in stop}

    # ---------------------------------------------------------------------
    # Packaging
    # ---------------------------------------------------------------------

    def _package_success(
        self,
        request: AnchorRequest,
        selected: AnchorCandidate,
        alternatives: list[AnchorCandidate],
    ) -> AnchorPackage:
        return AnchorPackage(
            request_hash=request.request_hash,
            anchor_state="selected",
            selected_anchor=selected.to_dict(),
            alternatives=[a.to_dict() for a in alternatives],
            boundary={
                "kind": selected.anchor_kind,
                "projection_hash": selected.projection_hash,
                "source_boundary_hash": selected.source_boundary_hash,
                "lens_id": selected.lens_id,
                "path": selected.path,
                "concepts": selected.concepts,
                "doubt_summary": selected.doubt_summary,
                "policy_blockers": selected.policy_blockers,
            },
            allowed_meanings=[
                "may_use_as_context_boundary",
                "may_read_projection_sources",
                "may_continue_reasoning_inside_boundary",
                "may_quote_boundary_with_citation",
                "may_request_followup_projection",
            ],
            forbidden_meanings=[
                "must_not_treat_anchor_as_truth",
                "must_not_ignore_doubt_summary",
                "must_not_expand_beyond_source_boundary_without_new_projection",
                "must_not_seal_diamond_from_anchor_without_sealability_test",
                "must_not_perform_external_effect_from_anchor_alone",
            ],
            safe_next_actions=[
                "load_projection",
                "inspect_source_boundary",
                "read_doubt_summary",
                "continue_inside_anchor",
                "declare_uncertainty_if_boundary_insufficient",
            ],
            created_at=utc_now(),
        )

    def _package_failure(
        self,
        request: AnchorRequest,
        alternatives: list[AnchorCandidate],
        reason: str,
    ) -> AnchorPackage:
        return AnchorPackage(
            request_hash=request.request_hash,
            anchor_state="no_safe_anchor",
            selected_anchor=None,
            alternatives=[a.to_dict() for a in alternatives],
            boundary={},
            allowed_meanings=[
                "may_report_no_safe_anchor",
                "may_request_new_projection",
                "may_ask_for_human_review",
            ],
            forbidden_meanings=[
                "must_not_improvise_answer",
                "must_not_treat_near_miss_as_anchor",
                "must_not_expand_context_without_projection",
                "must_not_perform_external_effect",
            ],
            safe_next_actions=[
                "declare_insufficient_grounding",
                "build_new_projection",
                "revise_anchor_request",
                "ask_human_for_scope",
            ],
            no_anchor_reason=reason,
            created_at=utc_now(),
        )

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(self, package: AnchorPackage) -> str:
        data = package.to_dict()

        lines = [
            "---",
            "kind: anchor_package",
            f"package_hash: {data['package_hash']}",
            f"anchor_state: {package.anchor_state}",
            f"request_hash: {package.request_hash}",
            f"created_at: {package.created_at}",
            "---",
            "",
            "# Anchor Package",
            "",
            "> An anchor is not truth. It is a safe place for an agent to stand.",
            "",
            "## State",
            "",
            f"- Anchor state: `{package.anchor_state}`",
            f"- Package hash: `{data['package_hash']}`",
            "",
        ]

        if package.selected_anchor:
            selected = package.selected_anchor
            lines += [
                "## Selected anchor",
                "",
                f"- Anchor ID: `{selected['anchor_id']}`",
                f"- Kind: `{selected['anchor_kind']}`",
                f"- Projection: `{selected['projection_hash']}`",
                f"- Boundary: `{selected['source_boundary_hash']}`",
                f"- Lens: `{selected['lens_id']}`",
                f"- Score: `{selected['score']}`",
                f"- Path: `{selected['path']}`",
                "",
                "## Doubt summary",
                "",
                "```json",
                json.dumps(selected["doubt_summary"], ensure_ascii=False, indent=2, sort_keys=True),
                "```",
                "",
            ]
        else:
            lines += [
                "## No safe anchor",
                "",
                f"- Reason: `{package.no_anchor_reason}`",
                "",
            ]

        lines += [
            "## Allowed meanings",
            "",
            *[f"- {m}" for m in package.allowed_meanings],
            "",
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
                    f"- `{alt['anchor_id']}` - score=`{alt['score']}` - "
                    f"blocked=`{str(alt['blocked']).lower()}` - "
                    f"lens=`{alt['lens_id']}` - blockers=`{alt['blockers']}`"
                )
        else:
            lines.append("- None")

        lines.append("")
        return "\n".join(lines)
