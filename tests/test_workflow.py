from graph.workflow import (
    incident_graph,
    safety_router,
    approval_router
)


def test_workflow_import():

    assert incident_graph is not None

    print("PASS: Checkpoint-enabled workflow imported successfully")


def test_blocked_safety_route():

    state = {
        "safety_status": "BLOCKED"
    }

    result = safety_router(state)

    assert result == "blocked"

    print("PASS: BLOCKED safety route works")


def test_approved_safety_route():

    state = {
        "safety_status": "APPROVED"
    }

    result = safety_router(state)

    assert result == "human_approval"

    print("PASS: APPROVED safety route requires human approval")


def test_approved_human_route():

    state = {
        "approval": "yes"
    }

    result = approval_router(state)

    assert result == "approved"

    print("PASS: Human approval YES route works")


def test_rejected_human_route():

    state = {
        "approval": "no"
    }

    result = approval_router(state)

    assert result == "rejected"

    print("PASS: Human approval NO route works")


if __name__ == "__main__":

    print("\nStarting Workflow Tests...\n")

    test_workflow_import()
    test_blocked_safety_route()
    test_approved_safety_route()
    test_approved_human_route()
    test_rejected_human_route()

    print("\nAll workflow tests passed.")