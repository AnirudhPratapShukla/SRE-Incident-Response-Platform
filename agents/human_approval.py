from utils.instrumentation import log_agent_execution

from graph.state import IncidentState
from langgraph.types import interrupt


@log_agent_execution("human_approval")
def human_approval(state: IncidentState) -> IncidentState:

    print("\n[Human Approval] Remediation requires human review.")

    approval_request = {
        "message": "The proposed remediation requires human approval.",
        "service": state.get("service", ""),
        "root_cause": state.get("root_cause", ""),
        "recommendation": state.get("recommendation", ""),
    }

    # Pause workflow and wait for human decision
    decision = interrupt(approval_request)

    approval = str(decision).strip().lower()

    state["approval"] = approval

    if approval in ["yes", "approve", "approved"]:

        state["execution_status"] = (
            "APPROVED - READY FOR CONTROLLED EXECUTION"
        )

        print("[Human Approval] Remediation approved.")

    else:

        state["execution_status"] = "NOT EXECUTED"

        print("[Human Approval] Remediation rejected.")

    return state