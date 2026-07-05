"""Diamonds — gold lifecycle: sealability, manifest, sealing, access, state, resolve."""

from logline_kernel.diamonds.access.gate import (
    AccessActor,
    AccessDecision,
    AccessRequest,
    AccessResult,
    DiamondAccessError,
    DiamondAccessGate,
)
from logline_kernel.diamonds.manifest.artifacts import ArtifactRef, DiamondArtifact
from logline_kernel.diamonds.manifest.builder import (
    DiamondBuildResult,
    DiamondManifestBuilder,
    DiamondManifestBuildError,
)
from logline_kernel.diamonds.manifest.manifest import DiamondManifest
from logline_kernel.diamonds.resolution.package import DiamondResolutionPackage
from logline_kernel.diamonds.resolution.request import DiamondResolveRequest
from logline_kernel.diamonds.resolution.resolver import (
    DiamondCandidate,
    DiamondResolveError,
    DiamondResolveResult,
    DiamondResolver,
    DiamondStateResolver,
)
from logline_kernel.diamonds.sealability.config import SealabilityConfig
from logline_kernel.diamonds.sealability.report import SealabilityReport
from logline_kernel.diamonds.sealability.tester import (
    SealabilityError,
    SealabilityResult,
    SealabilityTester,
)
from logline_kernel.diamonds.sealing.sealer import (
    DiamondSealError,
    DiamondSealer,
    DiamondSealResult,
    SealingAuthority,
)
from logline_kernel.diamonds.state.gate import (
    DiamondStateError,
    DiamondStateEvent,
    DiamondStateGate,
    DiamondStateResolver,
    DiamondStateResult,
    StateChangeAuthority,
    StateChangeRequest,
)

__all__ = [
    "AccessActor",
    "AccessDecision",
    "AccessRequest",
    "AccessResult",
    "DiamondAccessError",
    "DiamondAccessGate",
    "ArtifactRef",
    "DiamondArtifact",
    "DiamondBuildResult",
    "DiamondManifestBuilder",
    "DiamondManifestBuildError",
    "DiamondManifest",
    "DiamondResolutionPackage",
    "DiamondResolveRequest",
    "DiamondCandidate",
    "DiamondResolveError",
    "DiamondResolveResult",
    "DiamondResolver",
    "DiamondStateResolver",
    "SealabilityConfig",
    "SealabilityReport",
    "SealabilityError",
    "SealabilityResult",
    "SealabilityTester",
    "DiamondSealError",
    "DiamondSealer",
    "DiamondSealResult",
    "SealingAuthority",
    "DiamondStateError",
    "DiamondStateEvent",
    "DiamondStateGate",
    "DiamondStateResult",
    "StateChangeAuthority",
    "StateChangeRequest",
]
