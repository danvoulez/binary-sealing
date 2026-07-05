"""Vault receipt emitted when a Diamond is sealed."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VaultReceipt:
    """Receipt proving custody of a sealed Diamond."""

    diamond_id: str
    vault_path: str
    sealed_at: str
    sealed_by: str
    manifest_hash: str
    signature: Optional[dict] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "diamond_id": self.diamond_id,
            "vault_path": self.vault_path,
            "sealed_at": self.sealed_at,
            "sealed_by": self.sealed_by,
            "manifest_hash": self.manifest_hash,
            "signature": self.signature,
            "metadata": self.metadata,
        }
