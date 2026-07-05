"""AccessPackage: result returned when Diamond access is granted."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AccessPackage:
    """Portable package produced when Diamond access is granted."""

    diamond_id: str
    access_request_hash: str
    access_mode: str
    allowed_meanings: list[str] = field(default_factory=list)
    forbidden_meanings: list[str] = field(default_factory=list)
    safe_next_actions: list[str] = field(default_factory=list)
    boundary_hash: Optional[str] = None
    package_hash: Optional[str] = None
    created_at: str = ""

    def to_dict(self) -> dict:
        from logline_kernel.core.hashing import content_hash

        d = {
            "diamond_id": self.diamond_id,
            "access_request_hash": self.access_request_hash,
            "access_mode": self.access_mode,
            "allowed_meanings": self.allowed_meanings,
            "forbidden_meanings": self.forbidden_meanings,
            "safe_next_actions": self.safe_next_actions,
            "boundary_hash": self.boundary_hash,
            "created_at": self.created_at,
        }
        self.package_hash = content_hash(d, "access-package:")
        d["package_hash"] = self.package_hash
        return d
