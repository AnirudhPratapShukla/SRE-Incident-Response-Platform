from utils.instrumentation import log_agent_execution

from tools.logs import get_logs
from graph.state import IncidentState


@log_agent_execution("log_agent")
def log_agent(state: IncidentState) -> IncidentState:

    service = state.get("service", "unknown")

    print(f"\n[Log Agent] Checking logs for {service}...")

    logs = get_logs.invoke(
        {"service": service}
    )

    state["logs"] = logs

    print("[Log Agent] Logs collected.")

    return state