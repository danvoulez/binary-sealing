"""Diamond kind vocabulary."""

from dataclasses import dataclass
from typing import Optional


DIAMOND_KINDS = {
    "D.PROJ": "projection diamond",
    "D.DOCS": "document diamond",
    "D.AUDIT": "audit diamond",
    "D.PROD": "product diamond",
    "D.CODE": "code diamond",
    "D.MODEL": "model diamond",
}


@dataclass
class DiamondKind:
    """Validated Diamond kind."""

    code: str
    name: Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            self.name = DIAMOND_KINDS.get(self.code, "unknown")

    def is_known(self) -> bool:
        return self.code in DIAMOND_KINDS

    def to_dict(self) -> dict:
        return {"code": self.code, "name": self.name, "known": self.is_known()}
