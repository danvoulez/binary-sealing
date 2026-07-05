"""Nine-slot vocabulary constants for LogLine Acts."""

ACT_SLOTS = [
    "who", "did", "this", "when",
    "confirmed_by", "if_ok", "if_doubt", "if_not", "status",
]

REQUIRED_SLOTS = ["who", "did", "this", "when"]

ACT_STATUSES = {
    "draft", "valid", "ghost", "denied", "doubt",
    "conflicting", "revoked", "private", "registered",
    "blocked", "qualified",
}

DOUBT_STATES = {
    "known", "supported", "inferred", "contested",
    "missing", "stale", "policy_blocked", "human_required",
    "unsafe_to_act", "safe_to_continue",
}

ACTIVATION_STATES = {
    "registered", "readable", "projectable", "actionable",
    "effect_intended", "airlock_required", "committed", "revoked", "expired",
}
