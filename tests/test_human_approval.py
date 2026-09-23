from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from graph.state import IncidentState
from agents.human_approval import human_approval


workflow = StateGraph(IncidentState)

workflow.add_node("human_approval", human_approval)

workflow.add_edge(START, "human_approval")
workflow.add_edge("human_approval", END)

checkpointer = InMemorySaver()

graph = workflow.compile(
    checkpointer=checkpointer
)


config = {
    "configurable": {
        "thread_id": "human-approval-test"
    }
}


initial_state = {
    "service": "order-api",
    "root_cause": "Database connection pool exhaustion",
    "recommendation": "Increase database connection pool size",
    "safety_status": "BLOCKED"
}


print("\nStarting Human Approval Test...\n")

result = graph.invoke(
    initial_state,
    config=config
)


print("\nGraph paused:")
print(result["__interrupt__"])

decision = input("\nApprove remediation? (yes/no): ").strip().lower()


result = graph.invoke(
    Command(resume=decision),
    config=config
)


print("\nFinal State:")
print("Approval:", result.get("approval"))