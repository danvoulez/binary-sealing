"""Sealing authority store."""

from dataclasses import dataclass, field
from typing import Optional

from logline_kernel.diamonds.sealing.sealer import SealingAuthority


@dataclass
class SealingAuthorityStore:
    """In-memory store of sealing authorities for v0."""

    authorities: dict[str, SealingAuthority] = field(default_factory=dict)

    def add(self, authority: SealingAuthority) -> None:
        self.authorities[authority.authority_id] = authority

    def get(self, authority_id: str) -> Optional[SealingAuthority]:
        return self.authorities.get(authority_id)

    def list(self) -> list[str]:
        return list(self.authorities.keys())
