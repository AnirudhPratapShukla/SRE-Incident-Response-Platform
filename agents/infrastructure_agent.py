from graph.state import IncidentState

from tools.infrastructure import get_infrastructure_status


def infrastructure_agent(
    state: IncidentState
) -> IncidentState:

    service = state.get("service", "unknown")

    print(
        f"\n[Infrastructure Agent] "
        f"Checking infrastructure for {service}..."
    )

    infrastructure = get_infrastructure_status.invoke(
        {
            "service": service
        }
    )

    state["infrastructure"] = infrastructure

    print(
        "[Infrastructure Agent] "
        "Infrastructure status collected."
    )

    return state