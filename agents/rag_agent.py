from utils.instrumentation import log_agent_execution

from tools.rag import search_historical_incidents
from graph.state import IncidentState


@log_agent_execution("rag_agent")
def rag_agent(state: IncidentState) -> IncidentState:

    service = state.get("service", "unknown")
    incident = state.get("incident", "")
    logs = state.get("logs", "")

    print(
        f"\n[RAG Agent] Searching historical incidents "
        f"for {service}..."
    )

    query = f"""
    {service}
    {incident}
    HTTP 500
    database connection timeout
    unable to acquire database connection
    connection pool exhausted
    """

    historical_incidents = search_historical_incidents.invoke(
        {"query": query}
    )

    state["historical_incidents"] = historical_incidents

    print("[RAG Agent] Historical incidents retrieved.")

    return state