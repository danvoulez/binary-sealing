"""Diamond artifact references."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArtifactRef:
    """Reference to an artifact that belongs to a Diamond."""

    role: str
    path: str
    sha256: Optional[str] = None
    media_type: str = "application/octet-stream"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "path": self.path,
            "sha256": self.sha256,
            "media_type": self.media_type,
            "metadata": self.metadata,
        }


@dataclass
class DiamondArtifact:
    """Artifact embedded in a Diamond manifest."""

    role: str
    path: str
    sha256: Optional[str] = None
    media_type: str = "application/octet-stream"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "path": self.path,
            "sha256": self.sha256,
            "media_type": self.media_type,
            "metadata": self.metadata,
        }
