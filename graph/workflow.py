import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import IncidentState

from agents.monitoring_agent import monitoring_agent
from agents.log_agent import log_agent
from agents.infrastructure_agent import infrastructure_agent
from agents.rag_agent import rag_agent
from agents.rca_agent import rca_agent
from agents.safety_agent import safety_agent
from agents.remediation_agent import remediation_agent
from agents.human_approval import human_approval


# ============================================================
# CHECKPOINT DATABASE
# ============================================================

connection = sqlite3.connect(
    "sre_checkpoints.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)


# ============================================================
# GRAPH
# ============================================================

workflow = StateGraph(IncidentState)


# Add agents
workflow.add_node(
    "monitoring",
    monitoring_agent
)

workflow.add_node(
    "logs",
    log_agent
)

workflow.add_node(
    "infrastructure",
    infrastructure_agent
)

workflow.add_node(
    "rag",
    rag_agent
)

workflow.add_node(
    "rca",
    rca_agent
)

workflow.add_node(
    "safety",
    safety_agent
)

workflow.add_node(
    "human_approval",
    human_approval
)

workflow.add_node(
    "remediation",
    remediation_agent
)


# ============================================================
# INVESTIGATION FLOW
# ============================================================

workflow.add_edge(
    START,
    "monitoring"
)

workflow.add_edge(
    "monitoring",
    "logs"
)

workflow.add_edge(
    "logs",
    "infrastructure"
)

workflow.add_edge(
    "infrastructure",
    "rag"
)

workflow.add_edge(
    "rag",
    "rca"
)

workflow.add_edge(
    "rca",
    "safety"
)


# ============================================================
# SAFETY ROUTING
# ============================================================

def safety_router(state: IncidentState):

    safety_status = state.get(
        "safety_status",
        "UNKNOWN"
    )

    if safety_status == "BLOCKED":
        return "blocked"

    return "human_approval"


workflow.add_conditional_edges(
    "safety",
    safety_router,
    {
        "human_approval": "human_approval",
        "blocked": END
    }
)


# ============================================================
# HUMAN APPROVAL ROUTING
# ============================================================

def approval_router(state: IncidentState):

    approval = state.get(
        "approval",
        ""
    ).lower()

    if approval in [
        "yes",
        "approve",
        "approved"
    ]:
        return "approved"

    return "rejected"


workflow.add_conditional_edges(
    "human_approval",
    approval_router,
    {
        "approved": "remediation",
        "rejected": END
    }
)


# ============================================================
# REMEDIATION
# ============================================================

workflow.add_edge(
    "remediation",
    END
)


# ============================================================
# COMPILE
# ============================================================

incident_graph = workflow.compile(
    checkpointer=checkpointer
)