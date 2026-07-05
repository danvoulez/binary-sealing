"""Sealability Test v0 — gold gate for Diamond candidacy.

Core law:
    Sealability is not sealing.
    Sealability is not truth.
    A projection may become a Diamond only if its boundary, doubt,
    transform path, custody, rights, review, revocation path, scorecard,
    and receipt policy are explicit.

Input:
    projection.json from Projection Builder v0
    optional Cerebro source_index.ndjson
    sealability context dict supplied by process contract / human review

Output:
    sealability_report.json
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

    rows: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

class ReceiptSink(Protocol):
    def emit(self, kind: str, payload: dict, actor: str = "sealability_test") -> dict:
        ...

class NullReceipts:
    def emit(self, kind: str, payload: dict, actor: str = "sealability_test") -> dict:
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

def doubt_severity(state: str) -> int:
    return DOUBT_SEVERITY.get(state, 99)

def max_doubt_severity(doubt_summary: dict) -> int:
    if "max_severity" in doubt_summary:
        try:
            return int(doubt_summary["max_severity"])
        except (TypeError, ValueError):
            return 99

    return doubt_severity(doubt_summary.get("max_state", "missing"))

# ---------------------------------------------------------------------------
# Sealability config and result objects
# ---------------------------------------------------------------------------

@dataclass
class SealabilityConfig:
    """Policy knobs for the gold gate."""

    min_sources: int = 1
    max_allowed_doubt_severity: int = DOUBT_SEVERITY["inferred"]

    require_source_boundary: bool = True
    require_transform_replay: bool = True
    require_doubt_preserved: bool = True
    require_rights: bool = True
    require_scorecard: bool = True
    require_custody_policy: bool = True
    require_revocation_path: bool = True
    require_receipt_policy: bool = True
    require_human_review: bool = True

    # Human-review blockers are allowed only if the context proves review.
    allow_human_review_blocker_if_approved: bool = True

    # A projection with any other policy blocker cannot be sealable.
    allow_other_policy_blockers: bool = False

@dataclass
class RequirementResult:
    key: str
    passed: bool
    severity: str
    message: str
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class SealabilityReport:
    kind: str
    projection_hash: str
    source_boundary_hash: str
    report_status: str
    sealable: bool
    score: int
    requirements: list[dict]
    blockers: list[str]
    warnings: list[str]
    context_hash: str
    checked_at: str
    next_actions: list[str]
    diamond_candidate_ref: Optional[str] = None

    def body(self) -> dict:
        return asdict(self)

    @property
    def report_hash(self) -> str:
        return content_hash(self.body(), "sealability:")

    def to_dict(self) -> dict:
        d = self.body()
        d["report_hash"] = self.report_hash
        return d

@dataclass
class SealabilityResult:
    report_hash: str
    report_status: str
    sealable: bool
    report_path: str
    index_path: str
    blockers: list[str]
    warnings: list[str]
    next_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

# ---------------------------------------------------------------------------
# Sealability Tester
# ---------------------------------------------------------------------------

class SealabilityError(Exception):
    pass

class SealabilityTester:
    def __init__(
        self,
        cerebro_root: str,
        receipts: Optional[ReceiptSink] = None,
        config: Optional[SealabilityConfig] = None,
    ):
        self.cerebro_root = cerebro_root
        self.receipts = receipts or NullReceipts()
        self.config = config or SealabilityConfig()

    def test_projection(
        self,
        projection_path: str,
        context: dict,
        actor: str = "sealability_test",
    ) -> SealabilityResult:
        """Run the gold gate against one projection.

        The context is where process-specific external requirements are declared.

        Expected context shape:

            {
              "rights": {
                "attached": true,
                "license": "internal",
                "constraints": [...]
              },
              "scorecard": {
                "exists": true,
                "path": "...",
                "trust_score": 0.82
              },
              "custody_policy": {
                "exists": true,
                "vault": "nas:minivault",
                "path": "..."
              },
              "revocation": {
                "exists": true,
                "method": "supersede_or_revoke_manifest"
              },
              "receipts": {
                "configured": true,
                "kinds": ["diamond.candidate", "diamond.sealed", "diamond.revoked"]
              },
              "human_review": {
                "approved": true,
                "reviewed_by": "dan",
                "receipt": "receipt:<hash>"
              }
            }
        """
        projection = read_json(projection_path)
        source_index = self._load_source_index()
        context_hash = content_hash(context, "seal-context:")

        self.receipts.emit(
            "sealability.test_started",
            {
                "projection_path": projection_path,
                "projection_hash": projection.get("projection_hash"),
                "context_hash": context_hash,
            },
            actor=actor,
        )

        requirements = self._run_requirements(
            projection=projection,
            projection_path=projection_path,
            source_index=source_index,
            context=context,
        )

        blockers = [
            r.message for r in requirements
            if not r.passed and r.severity == "blocker"
        ]

        warnings = [
            r.message for r in requirements
            if not r.passed and r.severity == "warning"
        ]

        score = self._score(requirements)
        sealable = not blockers

        if sealable:
            report_status = "sealable"
            next_actions = [
                "create_diamond_candidate_manifest",
                "attach_sealability_report",
                "request_final_sealing_authority",
                "emit_diamond_candidate_receipt",
            ]
            diamond_candidate_ref = content_hash(
                {
                    "projection_hash": projection.get("projection_hash"),
                    "source_boundary_hash": projection.get("source_boundary_hash"),
                    "sealability_context": context_hash,
                },
                "diamond-candidate:",
            )
        else:
            report_status = "unsealable"
            next_actions = [
                "keep_as_dynamic_projection",
                "resolve_blockers",
                "rerun_sealability_test",
                "do_not_seal",
            ]
            diamond_candidate_ref = None

        report = SealabilityReport(
            kind="sealability.report.v0",
            projection_hash=projection.get("projection_hash", ""),
            source_boundary_hash=projection.get("source_boundary_hash", ""),
            report_status=report_status,
            sealable=sealable,
            score=score,
            requirements=[r.to_dict() for r in requirements],
            blockers=blockers,
            warnings=warnings,
            context_hash=context_hash,
            checked_at=utc_now(),
            next_actions=next_actions,
            diamond_candidate_ref=diamond_candidate_ref,
        )

        out_dir = os.path.join(
            self.cerebro_root,
            "60_projections",
            "sealability",
            report.report_hash,
        )

        report_path = os.path.join(out_dir, "sealability_report.json")
        index_path = os.path.join(out_dir, "index.md")

        write_json(report_path, report.to_dict())
        write_text(index_path, self._render_index_md(report))

        result = SealabilityResult(
            report_hash=report.report_hash,
            report_status=report.report_status,
            sealable=report.sealable,
            report_path=report_path,
            index_path=index_path,
            blockers=blockers,
            warnings=warnings,
            next_actions=next_actions,
        )

        self.receipts.emit(
            "sealability.test_completed",
            result.to_dict(),
            actor=actor,
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

    # ---------------------------------------------------------------------
    # Requirements
    # ---------------------------------------------------------------------

    def _run_requirements(
        self,
        projection: dict,
        projection_path: str,
        source_index: dict[str, dict],
        context: dict,
    ) -> list[RequirementResult]:
        return [
            self._projection_identity_valid(projection),
            self._source_boundary_explicit(projection),
            self._source_boundary_hash_valid(projection),
            self._transform_path_replayable(projection),
            self._doubts_preserved(projection),
            self._doubt_within_limit(projection),
            self._policy_blockers_resolved(projection, context),
            self._source_count_ok(projection),
            self._source_custody_trace_ok(projection, source_index),
            self._rights_attached(context),
            self._scorecard_exists(context),
            self._custody_policy_exists(context),
            self._revocation_path_exists(context),
            self._receipt_policy_configured(context),
            self._human_review_recorded(context),
            self._truth_warning_present(projection),
        ]

    def _projection_identity_valid(self, projection: dict) -> RequirementResult:
        expected = self._expected_projection_hash(projection)
        actual = projection.get("projection_hash")

        passed = bool(actual and actual == expected)

        return RequirementResult(
            key="projection_identity_valid",
            passed=passed,
            severity="blocker",
            message="projection identity hash matches content"
            if passed else "projection identity hash mismatch",
            evidence={
                "actual": actual,
                "expected": expected,
            },
        )

    def _expected_projection_hash(self, projection: dict) -> str:
        body = {
            "lens_id": projection.get("lens_id"),
            "lens_hash": projection.get("lens_hash"),
            "scope": projection.get("scope"),
            "actor": projection.get("actor"),
            "purpose": projection.get("purpose"),
            "source_records": sorted(projection.get("source_records", [])),
            "excluded_records": sorted(
                projection.get("excluded_records", []),
                key=lambda e: e.get("source_record_id", ""),
            ),
            "selection_trace": projection.get("selection_trace", []),
            "doubt_map": projection.get("doubt_map", {}),
            "doubt_summary": projection.get("doubt_summary", {}),
            "capability_map": projection.get("capability_map", {}),
            "policy_blockers": projection.get("policy_blockers", []),
            "safe_next_actions": projection.get("safe_next_actions", []),
            "meta": projection.get("meta", {}),
        }
        return content_hash(body, "proj:")

    def _source_boundary_explicit(self, projection: dict) -> RequirementResult:
        source_records = projection.get("source_records")
        excluded_records = projection.get("excluded_records")
        boundary_hash = projection.get("source_boundary_hash")

        passed = (
            isinstance(source_records, list)
            and isinstance(excluded_records, list)
            and bool(boundary_hash)
        )

        return RequirementResult(
            key="source_boundary_explicit",
            passed=passed,
            severity="blocker",
            message="source boundary is explicit"
            if passed else "source boundary is not explicit",
            evidence={
                "source_count": len(source_records or []),
                "excluded_count": len(excluded_records or []),
                "source_boundary_hash": boundary_hash,
            },
        )

    def _source_boundary_hash_valid(self, projection: dict) -> RequirementResult:
        expected = content_hash(
            {
                "included": sorted(projection.get("source_records", [])),
                "excluded": sorted(
                    e.get("source_record_id", "")
                    for e in projection.get("excluded_records", [])
                ),
            },
            "boundary:",
        )

        actual = projection.get("source_boundary_hash")
        passed = bool(actual and actual == expected)

        return RequirementResult(
            key="source_boundary_hash_valid",
            passed=passed,
            severity="blocker",
            message="source boundary hash matches included/excluded sources"
            if passed else "source boundary hash mismatch",
            evidence={
                "actual": actual,
                "expected": expected,
            },
        )

    def _transform_path_replayable(self, projection: dict) -> RequirementResult:
        passed = (
            bool(projection.get("lens_id"))
            and bool(projection.get("lens_hash"))
            and isinstance(projection.get("selection_trace"), list)
            and len(projection.get("selection_trace", [])) > 0
        )

        return RequirementResult(
            key="transform_path_replayable",
            passed=passed,
            severity="blocker" if self.config.require_transform_replay else "warning",
            message="transform path is replayable"
            if passed else "transform path is not replayable",
            evidence={
                "lens_id": projection.get("lens_id"),
                "lens_hash": projection.get("lens_hash"),
                "selection_trace_count": len(projection.get("selection_trace", [])),
            },
        )

    def _doubts_preserved(self, projection: dict) -> RequirementResult:
        source_records = set(projection.get("source_records", []))
        doubt_map = projection.get("doubt_map", {})
        doubt_summary = projection.get("doubt_summary", {})

        all_sources_have_doubt = all(s in doubt_map for s in source_records)
        no_extra_doubt = all(s in source_records for s in doubt_map.keys())
        summary_present = bool(doubt_summary)

        passed = all_sources_have_doubt and no_extra_doubt and summary_present

        return RequirementResult(
            key="doubts_preserved",
            passed=passed,
            severity="blocker",
            message="doubt is preserved for all source records"
            if passed else "doubt map does not cover the source boundary cleanly",
            evidence={
                "source_count": len(source_records),
                "doubt_count": len(doubt_map),
                "doubt_summary": doubt_summary,
            },
        )

    def _doubt_within_limit(self, projection: dict) -> RequirementResult:
        severity = max_doubt_severity(projection.get("doubt_summary", {}))
        passed = severity <= self.config.max_allowed_doubt_severity

        return RequirementResult(
            key="doubt_within_limit",
            passed=passed,
            severity="blocker",
            message="doubt is within sealability limit"
            if passed else "doubt exceeds sealability limit",
            evidence={
                "max_doubt_severity": severity,
                "allowed": self.config.max_allowed_doubt_severity,
                "doubt_summary": projection.get("doubt_summary", {}),
            },
        )

    def _policy_blockers_resolved(
        self,
        projection: dict,
        context: dict,
    ) -> RequirementResult:
        blockers = projection.get("policy_blockers", [])
        human_review_ok = bool(context.get("human_review", {}).get("approved"))

        unresolved: list[str] = []

        for blocker in blockers:
            if (
                blocker == "human_review_required_before_anchor_or_seal"
                and self.config.allow_human_review_blocker_if_approved
                and human_review_ok
            ):
                continue

            if not self.config.allow_other_policy_blockers:
                unresolved.append(blocker)

        passed = len(unresolved) == 0

        return RequirementResult(
            key="policy_blockers_resolved",
            passed=passed,
            severity="blocker",
            message="policy blockers resolved"
            if passed else "unresolved policy blockers remain",
            evidence={
                "policy_blockers": blockers,
                "unresolved": unresolved,
                "human_review_approved": human_review_ok,
            },
        )

    def _source_count_ok(self, projection: dict) -> RequirementResult:
        count = len(projection.get("source_records", []))
        passed = count >= self.config.min_sources

        return RequirementResult(
            key="source_count_ok",
            passed=passed,
            severity="blocker",
            message="projection has enough sources"
            if passed else "projection does not have enough sources",
            evidence={
                "source_count": count,
                "min_sources": self.config.min_sources,
            },
        )

    def _source_custody_trace_ok(
        self,
        projection: dict,
        source_index: dict[str, dict],
    ) -> RequirementResult:
        missing: list[str] = []
        weak: list[str] = []

        for source_id in projection.get("source_records", []):
            row = source_index.get(source_id)
            if not row:
                missing.append(source_id)
                continue

            if not row.get("source_card_path") or not row.get("summary_path"):
                weak.append(source_id)

        passed = not missing and not weak

        return RequirementResult(
            key="source_custody_trace_ok",
            passed=passed,
            severity="warning",
            message="source custody trace exists in Cerebro index"
            if passed else "some source records lack Cerebro trace",
            evidence={
                "missing_from_index": missing,
                "weak_rows": weak,
            },
        )

    def _rights_attached(self, context: dict) -> RequirementResult:
        rights = context.get("rights", {})
        passed = bool(rights.get("attached"))

        return RequirementResult(
            key="rights_attached",
            passed=passed,
            severity="blocker" if self.config.require_rights else "warning",
            message="rights and constraints are attached"
            if passed else "rights and constraints are missing",
            evidence=rights,
        )

    def _scorecard_exists(self, context: dict) -> RequirementResult:
        scorecard = context.get("scorecard", {})
        passed = bool(scorecard.get("exists"))

        return RequirementResult(
            key="scorecard_exists",
            passed=passed,
            severity="blocker" if self.config.require_scorecard else "warning",
            message="scorecard exists"
            if passed else "scorecard is missing",
            evidence=scorecard,
        )

    def _custody_policy_exists(self, context: dict) -> RequirementResult:
        custody = context.get("custody_policy", {})
        passed = bool(custody.get("exists"))

        return RequirementResult(
            key="custody_policy_exists",
            passed=passed,
            severity="blocker" if self.config.require_custody_policy else "warning",
            message="custody policy exists"
            if passed else "custody policy is missing",
            evidence=custody,
        )

    def _revocation_path_exists(self, context: dict) -> RequirementResult:
        revocation = context.get("revocation", {})
        passed = bool(revocation.get("exists"))

        return RequirementResult(
            key="revocation_path_exists",
            passed=passed,
            severity="blocker" if self.config.require_revocation_path else "warning",
            message="revocation path exists"
            if passed else "revocation path is missing",
            evidence=revocation,
        )

    def _receipt_policy_configured(self, context: dict) -> RequirementResult:
        receipts = context.get("receipts", {})
        passed = bool(receipts.get("configured"))

        return RequirementResult(
            key="receipt_policy_configured",
            passed=passed,
            severity="blocker" if self.config.require_receipt_policy else "warning",
            message="receipt emission is configured"
            if passed else "receipt policy is missing",
            evidence=receipts,
        )

    def _human_review_recorded(self, context: dict) -> RequirementResult:
        review = context.get("human_review", {})
        passed = bool(review.get("approved") and review.get("reviewed_by"))

        return RequirementResult(
            key="human_review_recorded",
            passed=passed,
            severity="blocker" if self.config.require_human_review else "warning",
            message="human review is recorded"
            if passed else "human review is missing",
            evidence=review,
        )

    def _truth_warning_present(self, projection: dict) -> RequirementResult:
        warning = projection.get("meta", {}).get("warning", "")
        safe_next = projection.get("safe_next_actions", [])

        passed = (
            "not truth" in warning.lower()
            or "do_not_treat_as_truth" in safe_next
        )

        return RequirementResult(
            key="truth_warning_present",
            passed=passed,
            severity="warning",
            message="projection carries explicit non-truth warning"
            if passed else "projection lacks explicit non-truth warning",
            evidence={
                "warning": warning,
                "safe_next_actions": safe_next,
            },
        )

    # ---------------------------------------------------------------------
    # Scoring / rendering
    # ---------------------------------------------------------------------

    def _score(self, requirements: list[RequirementResult]) -> int:
        if not requirements:
            return 0

        total = 0
        possible = 0

        for r in requirements:
            weight = 10 if r.severity == "blocker" else 3
            possible += weight
            if r.passed:
                total += weight

        return round((total / possible) * 100)

    def _render_index_md(self, report: SealabilityReport) -> str:
        data = report.to_dict()

        lines = [
            "---",
            "kind: sealability_report",
            f"report_hash: {data['report_hash']}",
            f"projection_hash: {report.projection_hash}",
            f"source_boundary_hash: {report.source_boundary_hash}",
            f"report_status: {report.report_status}",
            f"sealable: {str(report.sealable).lower()}",
            f"score: {report.score}",
            f"checked_at: {report.checked_at}",
            "---",
            "",
            "# Sealability Report",
            "",
            "> Sealability is not sealing. It only determines whether a projection may become a Diamond candidate.",
            "",
            "## Result",
            "",
            f"- Status: `{report.report_status}`",
            f"- Sealable: `{str(report.sealable).lower()}`",
            f"- Score: `{report.score}`",
            f"- Projection: `{report.projection_hash}`",
            f"- Boundary: `{report.source_boundary_hash}`",
            "",
        ]

        if report.diamond_candidate_ref:
            lines += [
                "## Diamond candidate reference",
                "",
                f"`{report.diamond_candidate_ref}`",
                "",
            ]

        lines += [
            "## Blockers",
            "",
        ]

        if report.blockers:
            lines.extend([f"- {b}" for b in report.blockers])
        else:
            lines.append("- None")

        lines += [
            "",
            "## Warnings",
            "",
        ]

        if report.warnings:
            lines.extend([f"- {w}" for w in report.warnings])
        else:
            lines.append("- None")

        lines += [
            "",
            "## Requirements",
            "",
        ]

        for req in report.requirements:
            mark = "PASS" if req["passed"] else "FAIL"
            lines.append(
                f"- `{mark}` `{req['key']}` — {req['message']} "
                f"(severity=`{req['severity']}`)"
            )

        lines += [
            "",
            "## Next actions",
            "",
            *[f"- {a}" for a in report.next_actions],
            "",
        ]

        return "\n".join(lines)
