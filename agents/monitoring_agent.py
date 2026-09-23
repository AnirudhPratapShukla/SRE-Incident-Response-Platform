from utils.instrumentation import log_agent_execution

from tools.metrics import get_metrics
from graph.state import IncidentState


@log_agent_execution("monitoring_agent")
def monitoring_agent(state: IncidentState) -> IncidentState:

    service = state.get("service", "unknown")

    print(f"\n[Monitoring Agent] Checking metrics for {service}...")

    metrics = get_metrics.invoke(
        {"service": service}
    )

    state["metrics"] = metrics

    print("[Monitoring Agent] Metrics collected.")

    return state