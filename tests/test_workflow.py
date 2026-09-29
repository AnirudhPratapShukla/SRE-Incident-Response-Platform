from unittest.mock import patch

from graph.workflow import (
    incident_graph,
    safety_router,
    approval_router,
    jira_review,
    jira_done,
)


def test_workflow_import():

    assert incident_graph is not None

    print(
        "PASS: Checkpoint-enabled workflow imported successfully"
    )


def test_blocked_safety_route():

    state = {
        "safety_status": "BLOCKED"
    }

    result = safety_router(state)

    assert result == "blocked"

    print(
        "PASS: BLOCKED safety route works"
    )


def test_approved_safety_route():

    state = {
        "safety_status": "APPROVED"
    }

    result = safety_router(state)

    assert result == "human_approval"

    print(
        "PASS: APPROVED safety route requires human approval"
    )


def test_approved_human_route():

    state = {
        "approval": "yes"
    }

    result = approval_router(state)

    assert result == "approved"

    print(
        "PASS: Human approval YES route works"
    )


def test_rejected_human_route():

    state = {
        "approval": "no"
    }

    result = approval_router(state)

    assert result == "rejected"

    print(
        "PASS: Human approval NO route works"
    )


@patch(
    "graph.workflow.mark_in_review"
)
def test_jira_review_moves_incident_to_in_review(
    mock_mark_in_review,
):

    state = {
        "safety_status": "APPROVED",
        "jira_issue_key": "SRE-4",
        "jira_status": "IN PROGRESS",
    }

    result = jira_review(state)

    mock_mark_in_review.assert_called_once_with(
        issue_key="SRE-4"
    )

    assert result["jira_issue_key"] == "SRE-4"

    assert result["jira_status"] == (
        "IN REVIEW"
    )


@patch(
    "graph.workflow.mark_in_review"
)
def test_jira_review_does_not_transition_blocked_incident(
    mock_mark_in_review,
):

    state = {
        "safety_status": "BLOCKED",
        "jira_issue_key": "SRE-4",
        "jira_status": "IN PROGRESS",
    }

    result = jira_review(state)

    mock_mark_in_review.assert_not_called()

    assert result["jira_status"] == (
        "IN PROGRESS"
    )


@patch(
    "graph.workflow.mark_in_review"
)
def test_jira_review_requires_issue_key(
    mock_mark_in_review,
):

    state = {
        "safety_status": "APPROVED",
    }

    try:

        jira_review(state)

        assert False, (
            "Expected jira_review to fail when "
            "jira_issue_key is missing."
        )

    except RuntimeError as exc:

        assert str(exc) == (
            "Cannot move Jira incident to In Review "
            "because jira_issue_key is missing."
        )

    mock_mark_in_review.assert_not_called()


@patch(
    "graph.workflow.mark_done"
)
def test_jira_done_moves_approved_incident_to_done(
    mock_mark_done,
):

    state = {
        "approval": "yes",
        "jira_issue_key": "SRE-4",
        "jira_status": "IN REVIEW",
    }

    result = jira_done(state)

    mock_mark_done.assert_called_once_with(
        issue_key="SRE-4"
    )

    assert result["jira_issue_key"] == "SRE-4"

    assert result["jira_status"] == (
        "DONE"
    )


@patch(
    "graph.workflow.mark_done"
)
def test_jira_done_does_not_transition_rejected_incident(
    mock_mark_done,
):

    state = {
        "approval": "no",
        "jira_issue_key": "SRE-4",
        "jira_status": "IN REVIEW",
    }

    result = jira_done(state)

    mock_mark_done.assert_not_called()

    assert result["jira_status"] == (
        "IN REVIEW"
    )


@patch(
    "graph.workflow.mark_done"
)
def test_jira_done_requires_issue_key(
    mock_mark_done,
):

    state = {
        "approval": "yes",
    }

    try:

        jira_done(state)

        assert False, (
            "Expected jira_done to fail when "
            "jira_issue_key is missing."
        )

    except RuntimeError as exc:

        assert str(exc) == (
            "Cannot move Jira incident to Done "
            "because jira_issue_key is missing."
        )

    mock_mark_done.assert_not_called()


if __name__ == "__main__":

    print(
        "\nStarting Workflow Tests...\n"
    )

    test_workflow_import()
    test_blocked_safety_route()
    test_approved_safety_route()
    test_approved_human_route()
    test_rejected_human_route()

    print(
        "\nAll workflow tests passed."
    )