"""Diamond state change request builder."""

from logline_kernel.diamonds.state.gate import StateChangeAuthority, StateChangeRequest


class StateChangeRequestBuilder:
    """Convenience builder for Diamond state change requests."""

    def __init__(self, mode: str, reason: str):
        self.mode = mode
        self.reason = reason
        self.authority_id: str = ""
        self.evidence: dict = {}

    def with_authority(self, authority_id: str) -> "StateChangeRequestBuilder":
        self.authority_id = authority_id
        return self

    def with_evidence(self, evidence: dict) -> "StateChangeRequestBuilder":
        self.evidence = evidence
        return self

    def build(self) -> StateChangeRequest:
        return StateChangeRequest(
            mode=self.mode,
            reason=self.reason,
            authority=StateChangeAuthority(
                authority_id=self.authority_id,
                evidence=self.evidence,
            ),
        )

__all__ = ["StateChangeAuthority", "StateChangeRequest", "StateChangeRequestBuilder"]
