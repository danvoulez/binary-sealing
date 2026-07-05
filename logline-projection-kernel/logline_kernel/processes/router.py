# Light Router
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class RouteDecision:
    process_id: str
    colour: str
    engine: str
    lens_id: str
    queue: str
    ui_state: str
    capability_state: str
    allowed_next: list[str]
    blocked: bool = False
    problems: list[str] = field(default_factory=list)

class LightRouter:
    """Maps process lights to queues, UI states, and next legal actions."""

    def __init__(self):
        self.engine_queues: dict[str, str] = {}
        self.colour_ui: dict[str, str] = {}

    def bind_engine(self, engine: str, queue: str) -> None:
        self.engine_queues[engine] = queue

    def bind_colour(self, colour: str, ui_state: str) -> None:
        self.colour_ui[colour] = ui_state

    def route(self, light: dict) -> RouteDecision:
        blocked = light.get("registration_state") != "ignited"
        colour = light.get("colour", "red")
        engine = light.get("engine", "quarantine")

        return RouteDecision(
            process_id=light["process_id"],
            colour=colour,
            engine=engine,
            lens_id=light["lens_id"],
            queue=self.engine_queues.get(engine, "queue:quarantine"),
            ui_state=self.colour_ui.get(colour, "ui:blocked"),
            capability_state=light.get("capability_state", "registered"),
            allowed_next=self._allowed_next_for(colour, blocked),
            blocked=blocked,
            problems=light.get("problems", []),
        )

    def _allowed_next_for(self, colour: str, blocked: bool) -> list[str]:
        if blocked:
            return ["review", "quarantine", "revise_record"]

        if colour == "blue":
            return ["flux_export", "hash", "write_nas", "emit_receipt"]

        if colour == "green":
            return ["build_projection", "inspect_projection", "score_projection"]

        if colour == "gold":
            return ["test_sealability", "seal_diamond", "emit_vault_receipt"]

        if colour == "purple":
            return ["find_anchor", "verify_anchor", "continue_with_boundary"]

        if colour == "orange":
            return ["intend_effect", "send_to_airlock", "await_commit"]

        return ["inspect", "review"]
