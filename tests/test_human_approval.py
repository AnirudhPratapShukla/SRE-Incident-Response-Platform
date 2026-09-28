from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from graph.state import IncidentState
from agents.human_approval import human_approval


def create_test_graph():

    workflow = StateGraph(IncidentState)

    workflow.add_node(
        "human_approval",
        human_approval
    )

    workflow.add_edge(
        START,
        "human_approval"
    )

    workflow.add_edge(
        "human_approval",
        END
    )

    checkpointer = InMemorySaver()

    return workflow.compile(
        checkpointer=checkpointer
    )


def test_human_approval_yes():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "human-approval-test-yes"
        }
    }

    initial_state = {
        "service": "order-api",
        "root_cause": (
            "Database connection pool exhaustion"
        ),
        "recommendation": (
            "Increase database connection pool size"
        ),
        "safety_status": "BLOCKED"
    }

    result = graph.invoke(
        initial_state,
        config=config
    )

    assert "__interrupt__" in result

    result = graph.invoke(
        Command(resume="yes"),
        config=config
    )

    assert result.get("approval") == "yes"

    print(
        "PASS: Human approval YES workflow works"
    )


def test_human_approval_no():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "human-approval-test-no"
        }
    }

    initial_state = {
        "service": "order-api",
        "root_cause": (
            "Database connection pool exhaustion"
        ),
        "recommendation": (
            "Increase database connection pool size"
        ),
        "safety_status": "BLOCKED"
    }

    result = graph.invoke(
        initial_state,
        config=config
    )

    assert "__interrupt__" in result

    result = graph.invoke(
        Command(resume="no"),
        config=config
    )

    assert result.get("approval") == "no"

    print(
        "PASS: Human approval NO workflow works"
    )


if __name__ == "__main__":

    print(
        "\nStarting Human Approval Tests...\n"
    )

    test_human_approval_yes()
    test_human_approval_no()

    print(
        "\nAll human approval tests passed."
    )
