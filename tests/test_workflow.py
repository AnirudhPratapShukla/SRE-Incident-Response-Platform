import pytest

import graph.workflow as workflow_module


# ============================================================
# WORKFLOW IMPORT
# ============================================================

def test_workflow_import():

    assert workflow_module.workflow is not None
    assert workflow_module.incident_graph is not None


# ============================================================
# SAFETY ROUTING
# ============================================================

def test_blocked_safety_route():

    state = {
        "safety_status": "BLOCKED"
    }

    result = workflow_module.safety_router(state)

    assert result == "blocked"


def test_approved_safety_route():

    state = {
        "safety_status": "APPROVED"
    }

    result = workflow_module.safety_router(state)

    assert result == "human_approval"


# ============================================================
# HUMAN APPROVAL ROUTING
# ============================================================

def test_approved_human_route():

    state = {
        "approval": "yes"
    }

    result = workflow_module.approval_router(state)

    assert result == "approved"


def test_rejected_human_route():

    state = {
        "approval": "no"
    }

    result = workflow_module.approval_router(state)

    assert result == "rejected"


# ============================================================
# JIRA REVIEW
# ============================================================

def test_jira_review_moves_incident_to_in_review(
    monkeypatch
):

    transitions = []

    def fake_mark_in_review(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_in_review",
        fake_mark_in_review,
    )

    state = {
        "jira_issue_key": "SRE-TEST-1",
        "safety_status": "APPROVED",
    }

    result = workflow_module.jira_review(state)

    assert transitions == ["SRE-TEST-1"]
    assert result["jira_status"] == "IN REVIEW"


def test_jira_review_does_not_transition_blocked_incident(
    monkeypatch
):

    transitions = []

    def fake_mark_in_review(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_in_review",
        fake_mark_in_review,
    )

    state = {
        "jira_issue_key": "SRE-TEST-2",
        "safety_status": "BLOCKED",
    }

    result = workflow_module.jira_review(state)

    assert transitions == []
    assert "jira_status" not in result


def test_jira_review_requires_issue_key():

    state = {
        "safety_status": "APPROVED",
    }

    with pytest.raises(
        RuntimeError,
        match="jira_issue_key is missing",
    ):
        workflow_module.jira_review(state)


# ============================================================
# JIRA DONE
# ============================================================

def test_jira_done_moves_executed_incident_to_done(
    monkeypatch
):

    transitions = []

    def fake_mark_done(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_done",
        fake_mark_done,
    )

    state = {
        "jira_issue_key": "SRE-TEST-3",
        "approval": "yes",
        "execution_status": (
            "EXECUTED - EC2 REBOOT VERIFIED THROUGH MCP"
        ),
        "verification_status": "VERIFIED",
    }

    result = workflow_module.jira_done(state)

    assert transitions == ["SRE-TEST-3"]
    assert result["jira_status"] == "DONE"


def test_jira_done_does_not_transition_failed_remediation(
    monkeypatch
):

    transitions = []

    def fake_mark_done(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_done",
        fake_mark_done,
    )

    state = {
        "jira_issue_key": "SRE-TEST-5",
        "approval": "yes",
        "execution_status": "EXECUTION FAILED",
        "verification_status": "FAILED",
    }

    result = workflow_module.jira_done(state)

    assert transitions == []
    assert "jira_status" not in result


def test_jira_done_does_not_transition_unexecuted_remediation(
    monkeypatch
):

    transitions = []

    def fake_mark_done(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_done",
        fake_mark_done,
    )

    state = {
        "jira_issue_key": "SRE-TEST-6",
        "approval": "yes",
        "execution_status": (
            "APPROVED - READY FOR CONTROLLED EXECUTION"
        ),
        "verification_status": "NOT RUN",
    }

    result = workflow_module.jira_done(state)

    assert transitions == []
    assert "jira_status" not in result


def test_jira_done_does_not_transition_rejected_incident(
    monkeypatch
):

    transitions = []

    def fake_mark_done(issue_key):

        transitions.append(issue_key)

    monkeypatch.setattr(
        workflow_module,
        "mark_done",
        fake_mark_done,
    )

    state = {
        "jira_issue_key": "SRE-TEST-4",
        "approval": "no",
        "execution_status": "NOT EXECUTED",
        "verification_status": "NOT RUN",
    }

    result = workflow_module.jira_done(state)

    assert transitions == []
    assert "jira_status" not in result


def test_jira_done_requires_issue_key():

    state = {
        "approval": "yes",
        "execution_status": (
            "EXECUTED - EC2 REBOOT VERIFIED THROUGH MCP"
        ),
        "verification_status": "VERIFIED",
    }

    with pytest.raises(
        RuntimeError,
        match="jira_issue_key is missing",
    ):
        workflow_module.jira_done(state)


# ============================================================
# MCP AWS CONTEXT
# ============================================================

def test_workflow_contains_mcp_aws_context():

    nodes = workflow_module.workflow.nodes

    assert "infrastructure" in nodes
    assert "mcp_aws_context" in nodes
    assert "rag" in nodes


# ============================================================
# MCP AWS CONTEXT ORDER
# ============================================================

def test_mcp_aws_context_is_between_infrastructure_and_rag():

    graph = workflow_module.workflow

    edges = graph.edges

    assert (
        "infrastructure",
        "mcp_aws_context"
    ) in edges

    assert (
        "mcp_aws_context",
        "rag"
    ) in edges