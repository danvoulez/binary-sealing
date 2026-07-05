"""AccessPolicy: permission rules for Diamond access."""

from dataclasses import dataclass, field


@dataclass
class AccessPolicy:
    """Default access policy for a Diamond."""

    diamond_id: str
    allowed_roles: list[str] = field(default_factory=list)
    allowed_modes: list[str] = field(default_factory=lambda: ["read", "anchor", "export_package"])
    required_reason: bool = True
    max_doubt_severity: int = 4  # missing
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "diamond_id": self.diamond_id,
            "allowed_roles": self.allowed_roles,
            "allowed_modes": self.allowed_modes,
            "required_reason": self.required_reason,
            "max_doubt_severity": self.max_doubt_severity,
            "constraints": self.constraints,
        }
