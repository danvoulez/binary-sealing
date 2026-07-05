"""Core processual data objects for the LogLine Projection Kernel.

Everything in this module is deliberately dependency-free (stdlib only) so the
kernel can run anywhere.

Core law:
    Registration is not truth.
    Qualification is not activation.
    Projection is not truth.
    Sealing is not omniscience.

All identity is content-addressed: an object's id is the sha256 of its
canonical JSON body.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

from logline_kernel.core import receipt_v0
from logline_kernel.core.hashing import content_hash
from logline_kernel.core.time import is_iso8601

# ---------------------------------------------------------------------------
# Process Record / Act - consequence-bearing vector, not admitted truth
# ---------------------------------------------------------------------------

ACT_SLOTS = [
    "who",
    "did",
    "this",
    "when",
    "confirmed_by",
    "if_ok",
    "if_doubt",
    "if_not",
    "status",
]

# Minimum shape required to enter the process layer.
REGISTERABLE_SLOTS = ["who", "did", "this", "when"]

# Full shape required for qualification.
QUALIFICATION_SLOTS = ACT_SLOTS

PROCESS_STATUSES = {
    "draft",        # exists but not ready for process
    "registered",   # well-shaped enough to enter process
    "qualified",    # full consequence structure present
    "projectable",  # safe to participate in projection
    "doubt",        # unresolved doubt attached
    "blocked",      # blocked by policy, evidence, or process rule
    "denied",       # rejected by process rule
    "revoked",      # previously valid process object withdrawn
    "private",      # valid but restricted
    "ghost",        # captured but not confirmed
}

@dataclass
class Act:
    """A processual LogLine object.

    This is not a claim of truth. It is a consequence-bearing record that may
    enter a process, be qualified, projected, activated, or sealed depending on
    later rules.

    The name Act is kept because it is the LogLine primitive, but semantically
    this class behaves as a process record.
    """

    who: str
    did: str
    this: str
    when: str
    confirmed_by: str = ""
    if_ok: str = ""
    if_doubt: str = ""
    if_not: str = ""
    status: str = "draft"
    aux: dict = field(default_factory=dict)

    def body(self) -> dict:
        """Canon content body: nine slots plus AUX as free top-level fields.

        Per the Foundation canon (logline.receipt.v0), AUX is any non-reserved
        top-level field — included in content_hash, excluded from tuple_hash.
        AUX must not shadow the nine slots or canon metadata names.
        """
        d = {k: getattr(self, k) for k in ACT_SLOTS}
        for key in self.aux:
            if key in receipt_v0.RESERVED_FIELDS:
                raise ValueError(f"aux field shadows reserved name: {key}")
            if key in receipt_v0.FORBIDDEN_LEGACY_FIELDS:
                raise ValueError(f"aux field uses forbidden legacy name: {key}")
        d.update(self.aux)
        return d

    @property
    def tuple_hash(self) -> str:
        """D42: identity of the pure act — the nine slots, nothing else."""
        return content_hash({k: getattr(self, k) for k in ACT_SLOTS})

    @property
    def process_id(self) -> str:
        """Canon content hash (bare 64-hex): id == content_hash."""
        return content_hash(self.body())

    @property
    def act_id(self) -> str:
        """Compatibility alias.

        Prefer process_id in kernel code to avoid implying admitted truth.
        """
        return self.process_id

    def to_receipt(self, when: Optional[str] = None) -> dict:
        """Emit this act as a full conformant logline.receipt.v0.

        An Act at rest and an emitted Receipt are different objects: the
        receipt adds canon metadata (receipt_version, json_canonicalization,
        hashes, id), so their content hashes legitimately differ.
        """
        return receipt_v0.emit(
            who=self.who,
            did=self.did,
            this=self.this,
            when=when if when is not None else self.when,
            confirmed_by=self.confirmed_by,
            if_ok=self.if_ok,
            if_doubt=self.if_doubt,
            if_not=self.if_not,
            status=self.status,
            aux=self.aux or None,
        )

    @classmethod
    def from_dict(cls, d: dict) -> "Act":
        aux = d.get("AUX", d.get("aux", {})) or {}
        return cls(
            who=d.get("who", ""),
            did=d.get("did", ""),
            this=d.get("this", ""),
            when=d.get("when", ""),
            confirmed_by=d.get("confirmed_by") or "",
            if_ok=d.get("if_ok") or "",
            if_doubt=d.get("if_doubt") or "",
            if_not=d.get("if_not") or "",
            status=d.get("status", "draft"),
            aux=aux,
        )

    def register_problems(self) -> list[str]:
        """Return problems blocking this object from entering process.

        Empty means registerable, not true.
        """
        problems: list[str] = []

        for slot in REGISTERABLE_SLOTS:
            value = getattr(self, slot)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"missing_registerable_slot:{slot}")

        if self.status not in PROCESS_STATUSES:
            problems.append(f"invalid_status:{self.status}")

        if self.when and not _looks_like_timestamp(self.when):
            problems.append("when_not_iso8601")

        return problems

    def qualification_problems(self) -> list[str]:
        """Return problems blocking full process qualification.

        Empty means the record has complete consequence structure.
        It still does not mean truth, activation, or effect permission.
        """
        problems = self.register_problems()

        for slot in QUALIFICATION_SLOTS:
            value = getattr(self, slot)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"missing_qualification_slot:{slot}")

        return problems

    def is_registerable(self) -> bool:
        return not self.register_problems()

    def is_qualified_shape(self) -> bool:
        return not self.qualification_problems()

def _looks_like_timestamp(s: str) -> bool:
    return is_iso8601(s)

# ---------------------------------------------------------------------------
# Doubt vocabulary
#
# Invariant: doubt must never collapse silently.
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
    "supported": 1,
    "inferred": 2,
    "stale": 3,
    "missing": 4,
    "contested": 5,
    "policy_blocked": 6,
    "human_required": 7,
    "unsafe_to_act": 8,
    "safe_to_continue": 0,
}

def aggregate_doubt(doubt_map: dict[str, str]) -> dict:
    """Aggregate doubt without erasing it."""
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
# Process capability states
#
# Invariant: registration is not qualification; qualification is not activation.
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

PROCESS_TRANSITIONS = {
    "registered": {"readable", "revoked", "expired"},
    "readable": {"projectable", "revoked", "expired"},
    "projectable": {"actionable", "airlock_required", "revoked", "expired"},
    "actionable": {"effect_intended", "airlock_required", "revoked", "expired"},
    "airlock_required": {"actionable", "revoked", "expired"},
    "effect_intended": {"committed", "revoked", "expired"},
    "committed": set(),
    "revoked": set(),
    "expired": set(),
}

def can_transition_process(current: str, target: str) -> bool:
    return target in PROCESS_TRANSITIONS.get(current, set())

def transition_process(current: str, target: str) -> str:
    if not can_transition_process(current, target):
        raise ValueError(f"invalid_process_transition:{current}->{target}")
    return target

# ---------------------------------------------------------------------------
# Projection - bounded process view, not truth
# ---------------------------------------------------------------------------

@dataclass
class Projection:
    lens_id: str
    scope: dict
    actor: str
    purpose: str

    # Process records inside the evidence boundary.
    source_records: list[str]

    # Explicitly excluded records: [{"process_id": "...", "reason": "..."}]
    excluded_records: list[dict]

    # Ordered compiler trace: [{"process_id": "...", "rule": "...", "decision": "..."}]
    selection_trace: list[dict]

    # process_id -> doubt state
    doubt_map: dict[str, str]

    # aggregated doubt view
    doubt_summary: dict

    # process_id -> process capability state
    capability_map: dict[str, str]

    policy_blockers: list
    safe_next_actions: list
    built_at: str = ""

    meta: dict = field(default_factory=lambda: {
        "is_projection": True,
        "warning": "A projection is a bounded reasoning surface, not truth itself.",
    })

    def hashable_body(self) -> dict:
        """Everything that defines projection identity.

        built_at is excluded so rebuilding the same projection from the same
        process set remains reproducible.
        """
        return {
            "lens_id": self.lens_id,
            "scope": self.scope,
            "actor": self.actor,
            "purpose": self.purpose,
            "source_records": sorted(self.source_records),
            "excluded_records": sorted(
                self.excluded_records,
                key=lambda e: e["process_id"],
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
                    e["process_id"] for e in self.excluded_records
                ),
            },
            "boundary:",
        )

    def validate(self) -> list[str]:
        problems: list[str] = []
        source_set = set(self.source_records)

        for item in self.excluded_records:
            if "process_id" not in item:
                problems.append("excluded_record_missing_process_id")
            if "reason" not in item:
                problems.append(
                    f"excluded_record_missing_reason:{item.get('process_id', '<unknown>')}"
                )

        for process_id, state in self.doubt_map.items():
            if process_id not in source_set:
                problems.append(f"doubt_for_non_source_record:{process_id}")
            if state not in DOUBT_STATES:
                problems.append(f"invalid_doubt_state:{process_id}:{state}")

        for process_id, state in self.capability_map.items():
            if process_id not in source_set:
                problems.append(f"capability_for_non_source_record:{process_id}")
            if state not in PROCESS_CAPABILITIES:
                problems.append(f"invalid_process_capability:{process_id}:{state}")

        return problems

    def to_dict(self) -> dict:
        d = asdict(self)
        d["projection_hash"] = self.projection_hash
        d["source_boundary_hash"] = self.source_boundary_hash
        return d

# ---------------------------------------------------------------------------
# Sealability - projection may become Diamond only if process conditions pass
# ---------------------------------------------------------------------------

SEALABILITY_REQUIREMENTS = [
    "source_boundary_explicit",
    "transform_path_replayable",
    "doubts_preserved",
    "rights_attached",
    "scorecard_exists",
    "custody_policy_exists",
    "revocation_path_exists",
    "receipt_emission_configured",
]

def sealability_problems(report: dict) -> list[str]:
    """Return missing requirements blocking Diamond sealing.

    This is deliberately dumb and explicit. The private kernel may compute the
    report, but this public object can verify the declared result.
    """
    problems: list[str] = []

    for key in SEALABILITY_REQUIREMENTS:
        if report.get(key) is not True:
            problems.append(f"sealability_missing:{key}")

    return problems
