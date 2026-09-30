import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import IncidentState

from agents.monitoring_agent import monitoring_agent
from agents.log_agent import log_agent
from agents.infrastructure_agent import infrastructure_agent
from agents.mcp_aws_agent import mcp_aws_agent
from agents.rag_agent import rag_agent
from agents.rca_agent import rca_agent
from agents.safety_agent import safety_agent
from agents.remediation_agent import remediation_agent
from agents.human_approval import human_approval

from jira.lifecycle import (
    mark_in_review,
    mark_done,
)


# ============================================================
# CHECKPOINT DATABASE
# ============================================================

connection = sqlite3.connect(
    "sre_checkpoints.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)


# ============================================================
# JIRA REVIEW
# ============================================================

def jira_review(
    state: IncidentState,
) -> IncidentState:
    """
    Move a non-blocked Jira incident to In Review
    before human approval.
    """

    safety_status = state.get(
        "safety_status",
        "UNKNOWN"
    )

    if safety_status == "BLOCKED":
        return state

    issue_key = state.get(
        "jira_issue_key"
    )

    if not issue_key:
        raise RuntimeError(
            "Cannot move Jira incident to In Review "
            "because jira_issue_key is missing."
        )

    mark_in_review(
        issue_key=issue_key
    )

    state["jira_status"] = "IN REVIEW"

    return state


# ============================================================
# JIRA DONE
# ============================================================

def jira_done(
    state: IncidentState,
) -> IncidentState:
    """
    Move an approved Jira incident to Done after
    the remediation plan has been prepared.
    """

    approval = state.get(
        "approval",
        ""
    ).strip().lower()

    if approval not in [
        "yes",
        "approve",
        "approved"
    ]:
        return state

    issue_key = state.get(
        "jira_issue_key"
    )

    if not issue_key:
        raise RuntimeError(
            "Cannot move Jira incident to Done "
            "because jira_issue_key is missing."
        )

    mark_done(
        issue_key=issue_key
    )

    state["jira_status"] = "DONE"

    return state


# ============================================================
# GRAPH
# ============================================================

workflow = StateGraph(IncidentState)


# ============================================================
# ADD AGENTS
# ============================================================

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
    "mcp_aws_context",
    mcp_aws_agent
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
    "jira_review",
    jira_review
)

workflow.add_node(
    "human_approval",
    human_approval
)

workflow.add_node(
    "remediation",
    remediation_agent
)

workflow.add_node(
    "jira_done",
    jira_done
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
    "mcp_aws_context"
)

workflow.add_edge(
    "mcp_aws_context",
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

workflow.add_edge(
    "safety",
    "jira_review"
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
    "jira_review",
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
    "jira_done"
)


# ============================================================
# JIRA DONE → END
# ============================================================

workflow.add_edge(
    "jira_done",
    END
)


# ============================================================
# COMPILE
# ============================================================

incident_graph = workflow.compile(
    checkpointer=checkpointer
)