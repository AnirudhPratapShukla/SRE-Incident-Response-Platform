from utils.instrumentation import log_agent_execution

from graph.state import IncidentState


@log_agent_execution("safety_agent")
def safety_agent(state: IncidentState) -> IncidentState:

    print("\n[Safety Agent] Evaluating remediation safety...")

    root_cause = state.get(
        "root_cause",
        ""
    )

    recommendation = state.get(
        "recommendation",
        ""
    )

    dangerous_keywords = [
        "delete database",
        "drop database",
        "delete production",
        "terminate all",
        "destroy infrastructure",
        "delete infrastructure",
        "remove production",
        "shutdown production"
    ]

    text_to_check = (
        root_cause + " " + recommendation
    ).lower()

    blocked = False

    for keyword in dangerous_keywords:

        if keyword.lower() in text_to_check:
            blocked = True
            break

    if blocked:

        state["safety_status"] = "BLOCKED"
        state["risk_level"] = "HIGH"

        state["safety_recommendation"] = (
            "BLOCKED: Proposed remediation contains "
            "a potentially destructive operation. "
            "Production execution is not permitted."
        )

        print(
            "[Safety Agent] BLOCKED - "
            "Destructive remediation detected."
        )

    else:

        state["safety_status"] = "APPROVED"
        state["risk_level"] = "MEDIUM"

        state["safety_recommendation"] = (
            "APPROVED FOR REVIEW: Remediation appears "
            "non-destructive, but production changes "
            "still require controlled approval."
        )

        print(
            "[Safety Agent] Remediation passed "
            "safety checks."
        )

    return state