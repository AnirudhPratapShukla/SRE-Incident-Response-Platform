from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command
import uuid

from graph.workflow import incident_graph


app = FastAPI(
    title="SRE Multi-Agent Incident Response API",
    description=(
        "AI-powered SRE incident investigation and "
        "human-approved remediation system."
    ),
    version="1.0.0"
)


class IncidentRequest(BaseModel):
    incident: str
    service: str


class ApprovalRequest(BaseModel):
    decision: str


def format_result(state, status, thread_id):

    return {
        "status": status,
        "thread_id": thread_id,

        # Incident
        "service": state.get("service"),
        "incident": state.get("incident"),

        # RCA
        "root_cause": state.get("root_cause"),
        "supporting_evidence": state.get(
            "supporting_evidence"
        ),
        "impact": state.get("impact"),

        # Safety
        "safety_status": state.get(
            "safety_status"
        ),
        "safety_recommendation": state.get(
            "safety_recommendation"
        ),
        "risk_level": state.get(
            "risk_level"
        ),

        # Human approval
        "approval": state.get(
            "approval"
        ),

        # Remediation
        "recommendation": state.get(
            "recommendation"
        ),
        "execution_status": state.get(
            "execution_status"
        ),
        "rollback_plan": state.get(
            "rollback_plan"
        ),
        "remediation_plan": state.get(
            "final_report"
        )
    }


@app.get("/")
def root():

    return {
        "service": "SRE Multi-Agent",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/incident")
def create_incident(
    request: IncidentRequest
):

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "incident": request.incident,
        "service": request.service
    }

    # Persist incident context before
    # starting the workflow.
    incident_graph.update_state(
        config,
        initial_state
    )

    result = incident_graph.invoke(
        None,
        config=config
    )

    if "__interrupt__" in result:

        interrupt_data = result[
            "__interrupt__"
        ][0]

        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": (
                interrupt_data.value
            )
        }

    final_state = incident_graph.get_state(
        config
    ).values

    return format_result(
        final_state,
        "completed",
        thread_id
    )


@app.post(
    "/incident/{thread_id}/approve"
)
def approve_incident(
    thread_id: str,
    request: ApprovalRequest
):

    decision = (
        request.decision
        .strip()
        .lower()
    )

    if decision not in [
        "yes",
        "no",
        "approve",
        "approved",
        "reject",
        "rejected"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be one of: "
                "yes, no, approve, approved, "
                "reject, rejected"
            )
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Verify that the checkpoint exists.
    checkpoint = incident_graph.get_state(
        config
    )

    if not checkpoint.values:

        raise HTTPException(
            status_code=404,
            detail=(
                "No active incident found for "
                "the supplied thread_id."
            )
        )

    result = incident_graph.invoke(
        Command(resume=decision),
        config=config
    )

    if "__interrupt__" in result:

        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": (
                result[
                    "__interrupt__"
                ][0].value
            )
        }

    # Read the complete persisted state
    # after the workflow resumes.
    final_state = incident_graph.get_state(
        config
    ).values

    return format_result(
        final_state,
        "completed",
        thread_id
    )