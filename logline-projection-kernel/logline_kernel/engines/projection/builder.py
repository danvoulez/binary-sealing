"""Projection Builder v0 — green engine for Dynamic Projections.

Core law:
    Projection is not truth.
    Projection is a bounded reasoning surface.
    Doubt must never collapse silently.
    A projection may become a Diamond only later, after sealability.

Input:
    Cerebro source_index.ndjson
    Cerebro graph.json
    ProjectionLens

Output:
    projection.json
    index.md
    receipt events
    projection-ready object for later anchoring / scoring / sealability

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

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "projection_builder") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "projection_builder") -> dict:
        return {
            "kind": kind,
            "payload": payload,
            "actor": actor,
            "at": utc_now(),
        }

# ---------------------------------------------------------------------------
# Doubt vocabulary
# ---------------------------------------------------------------------------

DOUBT_STATES = [
    "known",
    "supported",
    "inferred",
    "contested",
    "missing",
    "stale",
    "policy_blocked",
    "human_required",
    "unsafe_to_act",
    "safe_to_continue",
]

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

def aggregate_doubt(doubt_map: dict[str, str]) -> dict:
    counts: dict[str, int] = {}
    max_state = "known"
    max_severity = 0

    for state in doubt_map.values():
        counts[state] = counts.get(state, 0) + 1
        severity = DOUBT_SEVERITY.get(state, 99)
        if severity > max_severity:
            max_severity = severity
            max_state = state

    return {
        "max_state": max_state,
        "max_severity": max_severity,
        "counts": counts,
        "safe_to_continue": max_severity < DOUBT_SEVERITY["human_required"],
        "safe_to_act": max_severity < DOUBT_SEVERITY["policy_blocked"],
    }

# ---------------------------------------------------------------------------
# Process capability vocabulary
# ---------------------------------------------------------------------------

PROCESS_CAPABILITIES = [
    "registered",
    "readable",
    "projectable",
    "actionable",
    "effect_intended",
    "airlock_required",
    "committed",
    "revoked",
    "expired",
]

# ---------------------------------------------------------------------------
# Lens contract
# ---------------------------------------------------------------------------

@dataclass
class ProjectionLens:
    """A lens defines how to slice the Cerebro graph.

    It is not a SQL query.
    It is a process contract for a bounded view.

    v0 is intentionally simple and deterministic:
      - include by concept
      - include by fold_state
      - exclude by concept/fold_state
      - require projection_ready if desired
    """

    lens_id: str
    title: str
    purpose: str
    colour: str = "green"
    include_concepts: list[str] = field(default_factory=list)
    include_any_concepts: list[str] = field(default_factory=list)
    exclude_concepts: list[str] = field(default_factory=list)
    allowed_fold_states: list[str] = field(default_factory=lambda: [
        "indexed",
        "folding",
        "projectable",
        "stable",
        "sealable",
    ])
    blocked_fold_states: list[str] = field(default_factory=lambda: [
        "raw",
        "mirrored",
    ])
    require_projection_ready: bool = True
    min_sources: int = 1
    max_sources: int = 50
    default_capability: str = "projectable"
    review_required: bool = True
    aux: dict = field(default_factory=dict)

    def body(self) -> dict:
        return asdict(self)

    @property
    def lens_hash(self) -> str:
        return content_hash(self.body(), "lens:")

# ---------------------------------------------------------------------------
# Projection object
# ---------------------------------------------------------------------------

@dataclass
class Projection:
    lens_id: str
    lens_hash: str
    scope: dict
    actor: str
    purpose: str

    # Included source_record_id values.
    source_records: list[str]

    # Explicitly excluded: [{"source_record_id": "...", "reason": "..."}]
    excluded_records: list[dict]

    # Ordered trace: [{"source_record_id": "...", "rule": "...", "decision": "..."}]
    selection_trace: list[dict]

    # source_record_id -> doubt state
    doubt_map: dict[str, str]
    doubt_summary: dict

    # source_record_id -> process capability state
    capability_map: dict[str, str]

    policy_blockers: list[str]
    safe_next_actions: list[str]

    built_at: str = ""
    meta: dict = field(default_factory=lambda: {
        "is_projection": True,
        "warning": "A projection is a bounded reasoning surface, not truth itself.",
    })

    def hashable_body(self) -> dict:
        return {
            "lens_id": self.lens_id,
            "lens_hash": self.lens_hash,
            "scope": self.scope,
            "actor": self.actor,
            "purpose": self.purpose,
            "source_records": sorted(self.source_records),
            "excluded_records": sorted(
                self.excluded_records,
                key=lambda e: e["source_record_id"],
            ),
            "selection_trace": self.selection_trace,
            "doubt_map": self.doubt_map,
            "doubt_summary": self.doubt_summary,
            "capability_map": self.capability_map,
            "policy_blockers": self.policy_blockers,
            "safe_next_actions": self.safe_next_actions,
            "meta": self.meta,
        }

    @property
    def projection_hash(self) -> str:
        return content_hash(self.hashable_body(), "proj:")

    @property
    def source_boundary_hash(self) -> str:
        return content_hash(
            {
                "included": sorted(self.source_records),
                "excluded": sorted(
                    e["source_record_id"] for e in self.excluded_records
                ),
            },
            "boundary:",
        )

    def validate(self) -> list[str]:
        problems: list[str] = []
        source_set = set(self.source_records)

        for item in self.excluded_records:
            if "source_record_id" not in item:
                problems.append("excluded_record_missing_source_record_id")
            if "reason" not in item:
                problems.append(
                    f"excluded_record_missing_reason:{item.get('source_record_id', '<unknown>')}"
                )

        for source_id, state in self.doubt_map.items():
            if source_id not in source_set:
                problems.append(f"doubt_for_non_source_record:{source_id}")
            if state not in DOUBT_STATES:
                problems.append(f"invalid_doubt_state:{source_id}:{state}")

        for source_id, state in self.capability_map.items():
            if source_id not in source_set:
                problems.append(f"capability_for_non_source_record:{source_id}")
            if state not in PROCESS_CAPABILITIES:
                problems.append(f"invalid_capability_state:{source_id}:{state}")

        return problems

    def to_dict(self) -> dict:
        d = asdict(self)
        d["projection_hash"] = self.projection_hash
        d["source_boundary_hash"] = self.source_boundary_hash
        return d

# ---------------------------------------------------------------------------
# Builder result
# ---------------------------------------------------------------------------

@dataclass
class ProjectionBuildResult:
    projection_hash: str
    source_boundary_hash: str
    projection_path: str
    index_path: str
    included_count: int
    excluded_count: int
    doubt_summary: dict
    policy_blockers: list[str]
    safe_next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Projection Builder
# ---------------------------------------------------------------------------

class ProjectionBuildError(Exception):
    pass

class ProjectionBuilder:
    def __init__(
        self,
        cerebro_root: str,
        receipts: Optional[ReceiptSink] = None,
    ):
        self.cerebro_root = cerebro_root
        self.receipts = receipts or NullReceipts()

    def build(
        self,
        lens: ProjectionLens,
        actor: str,
        scope: Optional[dict] = None,
    ) -> ProjectionBuildResult:
        """Build a bounded projection from Cerebro.

        This is deterministic:
          same source index + same lens + same scope = same projection hash,
          except for built_at, which is excluded from identity.
        """
        scope = scope or {}

        self.receipts.emit(
            "projection.build_started",
            {
                "lens_id": lens.lens_id,
                "lens_hash": lens.lens_hash,
                "actor": actor,
                "scope": scope,
            },
            actor=actor,
        )

        sources = self._load_sources()
        graph = self._load_graph()

        included, excluded, trace = self._select_sources(
            sources=sources,
            graph=graph,
            lens=lens,
            scope=scope,
        )

        doubt_map = self._build_doubt_map(included, lens)
        doubt_summary = aggregate_doubt(doubt_map)
        capability_map = self._build_capability_map(included, doubt_map, lens)

        policy_blockers = self._policy_blockers(
            included=included,
            excluded=excluded,
            lens=lens,
            doubt_summary=doubt_summary,
        )

        safe_next_actions = self._safe_next_actions(
            included=included,
            policy_blockers=policy_blockers,
            doubt_summary=doubt_summary,
            lens=lens,
        )

        projection = Projection(
            lens_id=lens.lens_id,
            lens_hash=lens.lens_hash,
            scope=scope,
            actor=actor,
            purpose=lens.purpose,
            source_records=[
                s["source_record_id"] for s in included
            ],
            excluded_records=excluded,
            selection_trace=trace,
            doubt_map=doubt_map,
            doubt_summary=doubt_summary,
            capability_map=capability_map,
            policy_blockers=policy_blockers,
            safe_next_actions=safe_next_actions,
            built_at=utc_now(),
        )

        problems = projection.validate()
        if problems:
            self.receipts.emit(
                "projection.build_failed",
                {
                    "lens_id": lens.lens_id,
                    "problems": problems,
                },
                actor=actor,
            )
            raise ProjectionBuildError(f"projection_invalid:{problems}")

        out_dir = os.path.join(
            self.cerebro_root,
            "60_projections",
            "active",
            projection.projection_hash,
        )

        projection_path = os.path.join(out_dir, "projection.json")
        index_path = os.path.join(out_dir, "index.md")

        write_json(projection_path, projection.to_dict())
        write_text(index_path, self._render_index_md(projection, included, lens))

        result = ProjectionBuildResult(
            projection_hash=projection.projection_hash,
            source_boundary_hash=projection.source_boundary_hash,
            projection_path=projection_path,
            index_path=index_path,
            included_count=len(included),
            excluded_count=len(excluded),
            doubt_summary=doubt_summary,
            policy_blockers=policy_blockers,
            safe_next_actions=safe_next_actions,
        )

        self.receipts.emit(
            "projection.build_completed",
            result.to_dict(),
            actor=actor,
        )

        return result

    # ---------------------------------------------------------------------
    # Loading
    # ---------------------------------------------------------------------

    def _load_sources(self) -> list[dict]:
        path = os.path.join(self.cerebro_root, "00_index", "source_index.ndjson")
        return read_ndjson(path)

    def _load_graph(self) -> dict:
        path = os.path.join(self.cerebro_root, "00_index", "graph.json")
        if not os.path.exists(path):
            return {"kind": "cerebro.graph.v0", "nodes": {}, "edges": []}
        return read_json(path)

    # ---------------------------------------------------------------------
    # Selection
    # ---------------------------------------------------------------------

    def _select_sources(
        self,
        sources: list[dict],
        graph: dict,
        lens: ProjectionLens,
        scope: dict,
    ) -> tuple[list[dict], list[dict], list[dict]]:
        included: list[dict] = []
        excluded: list[dict] = []
        trace: list[dict] = []

        ordered_sources = sorted(
            sources,
            key=lambda s: (
                s.get("source_record_id", ""),
                s.get("cerebro_source_id", ""),
            ),
        )

        for source in ordered_sources:
            decision, reason = self._source_decision(source, lens, scope)

            source_id = source.get("source_record_id", "<missing>")

            trace.append({
                "source_record_id": source_id,
                "rule": "lens_selection_v0",
                "decision": decision,
                "reason": reason,
            })

            if decision == "include":
                included.append(source)
            else:
                excluded.append({
                    "source_record_id": source_id,
                    "reason": reason,
                })

            if len(included) >= lens.max_sources:
                # Remaining sources are excluded explicitly so the boundary is honest.
                continue

        # If max_sources was exceeded, force extra included candidates into excluded.
        if len(included) > lens.max_sources:
            overflow = included[lens.max_sources:]
            included = included[:lens.max_sources]

            for source in overflow:
                excluded.append({
                    "source_record_id": source.get("source_record_id", "<missing>"),
                    "reason": "excluded:max_sources_reached",
                })

        return included, excluded, trace

    def _source_decision(
        self,
        source: dict,
        lens: ProjectionLens,
        scope: dict,
    ) -> tuple[str, str]:
        concepts = set(source.get("concepts", []))
        fold_state = source.get("fold_state")
        projection_ready = bool(source.get("projection_ready"))

        if lens.require_projection_ready and not projection_ready:
            return "exclude", "excluded:not_projection_ready"

        if fold_state in lens.blocked_fold_states:
            return "exclude", f"excluded:blocked_fold_state:{fold_state}"

        if lens.allowed_fold_states and fold_state not in lens.allowed_fold_states:
            return "exclude", f"excluded:fold_state_not_allowed:{fold_state}"

        if any(c in concepts for c in lens.exclude_concepts):
            return "exclude", "excluded:excluded_concept_match"

        if lens.include_concepts:
            missing = [c for c in lens.include_concepts if c not in concepts]
            if missing:
                return "exclude", f"excluded:missing_required_concepts:{','.join(missing)}"

        if lens.include_any_concepts:
            if not any(c in concepts for c in lens.include_any_concepts):
                return "exclude", "excluded:no_any_concept_match"

        scope_concepts = set(scope.get("concepts", []))
        if scope_concepts and not concepts.intersection(scope_concepts):
            return "exclude", "excluded:outside_scope_concepts"

        return "include", "included:lens_match"

    # ---------------------------------------------------------------------
    # Doubt / capability / policy
    # ---------------------------------------------------------------------

    def _build_doubt_map(
        self,
        included: list[dict],
        lens: ProjectionLens,
    ) -> dict[str, str]:
        doubt_map: dict[str, str] = {}

        for source in included:
            source_id = source["source_record_id"]
            fold_state = source.get("fold_state")
            projection_ready = bool(source.get("projection_ready"))
            concepts = source.get("concepts", [])

            if not projection_ready:
                doubt_map[source_id] = "missing"
            elif fold_state in {"stable", "sealable"}:
                doubt_map[source_id] = "supported"
            elif fold_state == "projectable":
                doubt_map[source_id] = "inferred"
            elif fold_state == "folding":
                doubt_map[source_id] = "inferred"
            elif fold_state == "indexed":
                doubt_map[source_id] = "stale" if not concepts else "inferred"
            else:
                doubt_map[source_id] = "missing"

        return doubt_map

    def _build_capability_map(
        self,
        included: list[dict],
        doubt_map: dict[str, str],
        lens: ProjectionLens,
    ) -> dict[str, str]:
        capability_map: dict[str, str] = {}

        for source in included:
            source_id = source["source_record_id"]
            doubt = doubt_map.get(source_id, "missing")

            if doubt in {"policy_blocked", "human_required", "unsafe_to_act"}:
                capability_map[source_id] = "readable"
            elif doubt in {"missing", "contested"}:
                capability_map[source_id] = "readable"
            else:
                capability_map[source_id] = lens.default_capability

        return capability_map

    def _policy_blockers(
        self,
        included: list[dict],
        excluded: list[dict],
        lens: ProjectionLens,
        doubt_summary: dict,
    ) -> list[str]:
        blockers: list[str] = []

        if len(included) < lens.min_sources:
            blockers.append(
                f"min_sources_not_met:{len(included)}<{lens.min_sources}"
            )

        if doubt_summary["max_state"] in {
            "policy_blocked",
            "human_required",
            "unsafe_to_act",
        }:
            blockers.append(f"doubt_blocks_action:{doubt_summary['max_state']}")

        if lens.review_required:
            blockers.append("human_review_required_before_anchor_or_seal")

        return blockers

    def _safe_next_actions(
        self,
        included: list[dict],
        policy_blockers: list[str],
        doubt_summary: dict,
        lens: ProjectionLens,
    ) -> list[str]:
        if not included:
            return [
                "revise_lens",
                "add_more_sources",
                "do_not_anchor",
                "do_not_seal",
            ]

        actions = [
            "inspect_projection",
            "review_source_boundary",
            "review_doubt_map",
        ]

        if doubt_summary["safe_to_continue"]:
            actions.append("mini_llm_review")
            actions.append("compare_with_related_projection")

        if not policy_blockers:
            actions.append("candidate_anchor")
            actions.append("score_sealability")
        else:
            actions.append("resolve_policy_blockers")

        actions.append("do_not_treat_as_truth")

        return actions

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def _render_index_md(
        self,
        projection: Projection,
        included: list[dict],
        lens: ProjectionLens,
    ) -> str:
        data = projection.to_dict()

        lines = [
            "---",
            f"kind: dynamic_projection",
            f"projection_hash: {data['projection_hash']}",
            f"source_boundary_hash: {data['source_boundary_hash']}",
            f"lens_id: {lens.lens_id}",
            f"lens_hash: {lens.lens_hash}",
            f"status: active",
            f"built_at: {projection.built_at}",
            "---",
            "",
            f"# Projection — {lens.title}",
            "",
            "> A projection is a bounded reasoning surface, not truth itself.",
            "",
            "## Purpose",
            "",
            lens.purpose,
            "",
            "## Boundary",
            "",
            f"- Included sources: `{len(projection.source_records)}`",
            f"- Excluded sources: `{len(projection.excluded_records)}`",
            f"- Source boundary hash: `{data['source_boundary_hash']}`",
            "",
            "## Doubt summary",
            "",
            "```json",
            json.dumps(projection.doubt_summary, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## Policy blockers",
            "",
        ]

        if projection.policy_blockers:
            lines.extend([f"- {b}" for b in projection.policy_blockers])
        else:
            lines.append("- None")

        lines += [
            "",
            "## Safe next actions",
            "",
            *[f"- {a}" for a in projection.safe_next_actions],
            "",
            "## Included sources",
            "",
        ]

        for source in included:
            lines.append(
                f"- `{source.get('source_record_id')}` — "
                f"{source.get('title', '<untitled>')} — "
                f"fold_state=`{source.get('fold_state')}` — "
                f"summary=`{source.get('summary_path')}`"
            )

        lines += [
            "",
            "## Selection trace",
            "",
            "```json",
            json.dumps(projection.selection_trace, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
        ]

        return "\n".join(lines)
