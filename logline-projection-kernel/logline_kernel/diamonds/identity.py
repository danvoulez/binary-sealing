"""Diamond identity helpers."""

from dataclasses import dataclass
from typing import Any

from logline_kernel.core.hashing import content_hash


@dataclass
class DiamondIdentity:
    """Content-addressed identity for a Diamond."""

    diamond_id: str
    kind: str
    manifest_hash: str

    @classmethod
    def from_manifest(cls, manifest: dict) -> "DiamondIdentity":
        diamond_id = manifest["diamond_id"]
        kind = manifest["kind"]
        manifest_hash = content_hash(manifest, "manifest:")
        return cls(diamond_id=diamond_id, kind=kind, manifest_hash=manifest_hash)

    def verify(self, manifest: dict) -> bool:
        return content_hash(manifest, "manifest:") == self.manifest_hash

    def to_dict(self) -> dict:
        return {
            "diamond_id": self.diamond_id,
            "kind": self.kind,
            "manifest_hash": self.manifest_hash,
        }
