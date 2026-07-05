"""AccessRequestBuilder helper."""

from logline_kernel.diamonds.access.gate import AccessActor, AccessRequest


class AccessRequestBuilder:
    """Convenience builder for Diamond access requests."""

    def __init__(self, actor_id: str, mode: str, purpose: str, reason: str = ""):
        self.actor_id = actor_id
        self.mode = mode
        self.purpose = purpose
        self.reason = reason
        self.roles: list[str] = []
        self.scope: dict = {}

    def with_roles(self, roles: list[str]) -> "AccessRequestBuilder":
        self.roles = roles
        return self

    def with_scope(self, scope: dict) -> "AccessRequestBuilder":
        self.scope = scope
        return self

    def build(self) -> AccessRequest:
        return AccessRequest(
            actor=AccessActor(actor_id=self.actor_id, roles=self.roles),
            mode=self.mode,
            purpose=self.purpose,
            reason=self.reason,
            scope=self.scope,
        )
