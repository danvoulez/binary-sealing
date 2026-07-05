"""Process registry and light router for the LogLine Projection Kernel.

This module prevents blind registration.

A record may only be registered after a process contract has been selected.
The registry can resolve explicit process requests, suggest candidate processes,
or quarantine records that do not fit any known process.

Dependency-free: stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Callable, Any

# ---------------------------------------------------------------------------
# Process matching
# ---------------------------------------------------------------------------

@dataclass
class MatchRule:
    """Small, explicit process-discovery rule.

    These rules do not define slot meaning. The ProcessContract does that.
    MatchRule only helps decide which process contracts are plausible.
    """

    slot: str
    op: str
    value: Any
    weight: int = 1

    def matches(self, act: "Act") -> bool:
        candidate = getattr(act, self.slot, None)

        if self.op == "equals":
            return candidate == self.value

        if self.op == "in":
            return candidate in self.value

        if self.op == "contains":
            return isinstance(candidate, str) and self.value in candidate

        if self.op == "startswith":
            return isinstance(candidate, str) and candidate.startswith(self.value)

        if self.op == "aux_has":
            return self.value in act.aux

        if self.op == "aux_equals":
            key, expected = self.value
            return act.aux.get(key) == expected

        raise ValueError(f"unknown_match_op:{self.op}")

@dataclass
class ProcessCandidate:
    process_id: str
    contract_hash: str
    score: int
    colour: str
    engine: str
    lens_id: str
    problems: list[str]
    reasons: list[str]

    @property
    def usable(self) -> bool:
        return not self.problems

@dataclass
class RegisteredProcess:
    contract: "ProcessContract"
    match_rules: list[MatchRule] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True

    def candidate_for(self, act: "Act") -> ProcessCandidate:
        score = self.priority
        reasons: list[str] = []

        for rule in self.match_rules:
            if rule.matches(act):
                score += rule.weight
                reasons.append(f"matched:{rule.slot}:{rule.op}:{rule.value}")

        problems = self.contract.registration_problems(act)

        # Penalize invalid registration shape, but still expose as candidate
        # for debugging and human review.
        if problems:
            score -= 100

        return ProcessCandidate(
            process_id=self.contract.process_id,
            contract_hash=self.contract.contract_hash,
            score=score,
            colour=self.contract.colour,
            engine=self.contract.engine,
            lens_id=self.contract.lens_id,
            problems=problems,
            reasons=reasons,
        )

# ---------------------------------------------------------------------------
# Process Registry
# ---------------------------------------------------------------------------

class ProcessResolutionError(Exception):
    def __init__(self, code: str, candidates: list[ProcessCandidate]):
        self.code = code
        self.candidates = candidates
        super().__init__(code)

class ProcessRegistry:
    """Registry of process contracts.

    Resolution order:
      1. If AUX.process_id is explicit, use only that process.
      2. Otherwise, score all enabled processes by match rules.
      3. If exactly one usable process clearly wins, select it.
      4. If none or ambiguous, do not guess; return candidates.
    """

    def __init__(self):
        self._processes: dict[str, RegisteredProcess] = {}

    def add(
        self,
        contract: "ProcessContract",
        match_rules: Optional[list[MatchRule]] = None,
        priority: int = 0,
        enabled: bool = True,
    ) -> None:
        self._processes[contract.process_id] = RegisteredProcess(
            contract=contract,
            match_rules=match_rules or [],
            priority=priority,
            enabled=enabled,
        )

    def get(self, process_id: str) -> Optional["ProcessContract"]:
        item = self._processes.get(process_id)
        if not item or not item.enabled:
            return None
        return item.contract

    def candidates(self, act: "Act") -> list[ProcessCandidate]:
        out: list[ProcessCandidate] = []

        for item in self._processes.values():
            if not item.enabled:
                continue
            out.append(item.candidate_for(act))

        return sorted(out, key=lambda c: c.score, reverse=True)

    def resolve(self, act: "Act") -> "ProcessContract":
        explicit = act.aux.get("process_id") or act.aux.get("process")

        if explicit:
            item = self._processes.get(explicit)
            if not item or not item.enabled:
                raise ProcessResolutionError("unknown_explicit_process", [])

            candidate = item.candidate_for(act)
            if candidate.problems:
                raise ProcessResolutionError("explicit_process_rejected", [candidate])

            return item.contract

        candidates = self.candidates(act)
        usable = [c for c in candidates if c.usable and c.score > 0]

        if not usable:
            raise ProcessResolutionError("no_matching_process", candidates)

        if len(usable) == 1:
            return self._processes[usable[0].process_id].contract

        # Require a clear winner. If top two tie, do not guess.
        if usable[0].score == usable[1].score:
            raise ProcessResolutionError("ambiguous_process", usable[:5])

        return self._processes[usable[0].process_id].contract

