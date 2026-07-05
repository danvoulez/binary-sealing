from dataclasses import dataclass, field, asdict
from typing import Optional

from logline_kernel.acts.act import Act
from logline_kernel.core.hashing import content_hash
from logline_kernel.core.time import is_iso8601


@dataclass
class SlotRule:
    meaning: str
    required: bool = False
    validator: Optional[str] = None


@dataclass
class ProcessContract:
    """A process owns the meaning of the nine slots.

    The Act provides the stable connector.
    The process contract provides the semantics, colour, engine, lens, and rules.
    """

    process_id: str
    version: str
    title: str
    colour: str
    engine: str
    lens_id: str
    slot_rules: dict[str, SlotRule]
    allowed_statuses: set[str]
    required_aux: list[str] = field(default_factory=list)
    effects_allowed: bool = False

    def contract_body(self) -> dict:
        return {
            "process_id": self.process_id,
            "version": self.version,
            "title": self.title,
            "colour": self.colour,
            "engine": self.engine,
            "lens_id": self.lens_id,
            "slot_rules": {
                k: asdict(v) for k, v in self.slot_rules.items()
            },
            "allowed_statuses": sorted(self.allowed_statuses),
            "required_aux": sorted(self.required_aux),
            "effects_allowed": self.effects_allowed,
        }

    @property
    def contract_hash(self) -> str:
        return content_hash(self.contract_body(), "process:")

    def registration_problems(self, act: Act) -> list[str]:
        """Return problems blocking registration into this process.

        Empty means the record fits this process contract.
        It does not mean truth.
        It does not mean activation.
        It means the right engine may be ignited in registered state.
        """
        problems: list[str] = []

        # Base processability: a record must at least have the four orientation slots.
        for slot in ["who", "did", "this", "when"]:
            value = getattr(act, slot)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"{self.process_id}:missing_orientation_slot:{slot}")

        if act.when and not is_iso8601(act.when):
            problems.append(f"{self.process_id}:when_not_iso8601")

        if act.status not in self.allowed_statuses:
            problems.append(f"{self.process_id}:invalid_status:{act.status}")

        # Process-local slot semantics.
        for slot, rule in self.slot_rules.items():
            value = getattr(act, slot)
            if rule.required and (not isinstance(value, str) or not value.strip()):
                problems.append(f"{self.process_id}:missing_slot:{slot}")

        # Process-local AUX requirements.
        for key in self.required_aux:
            if key not in act.aux:
                problems.append(f"{self.process_id}:missing_aux:{key}")

        return problems

    def can_register(self, act: Act) -> bool:
        return not self.registration_problems(act)

    def light_for(self, act: Act) -> dict:
        """Return the process light produced by this attempted registration."""
        problems = self.registration_problems(act)

        if problems:
            return {
                "process_id": self.process_id,
                "contract_hash": self.contract_hash,
                "colour": "red",
                "engine": "quarantine",
                "lens_id": self.lens_id,
                "registration_state": "blocked",
                "capability_state": "registered",
                "problems": problems,
            }

        return {
            "process_id": self.process_id,
            "contract_hash": self.contract_hash,
            "colour": self.colour,
            "engine": self.engine,
            "lens_id": self.lens_id,
            "registration_state": "ignited",
            "capability_state": "registered",
            "problems": [],
        }
