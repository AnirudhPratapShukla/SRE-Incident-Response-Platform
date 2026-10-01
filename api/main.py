from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command
import os
import uuid

from graph.workflow import incident_graph

from services.cloudwatch_incident_runner import (
    start_cloudwatch_incidents,
)

from jira.incidents import (
    create_incident as create_jira_incident,
)

from jira.lifecycle import (
    mark_in_progress,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="SRE Multi-Agent Incident Response API",
    description=(
        "AI-powered SRE incident investigation and "
        "human-approved remediation system."
    ),
    version="1.3.0",
)


# ============================================================
# REQUEST MODELS
# ============================================================

class IncidentRequest(BaseModel):
    incident: str
    service: str


class ApprovalRequest(BaseModel):
    decision: str
    remediation_action: str = ""
    remediation_instance_id: str = ""

    # Explicit safe demo mode.
    #
    # False = real controlled MCP remediation
    # True  = safe simulation; no AWS mutation
    simulation_mode: bool = False


class CloudWatchIncidentRequest(BaseModel):
    region_name: str = "us-east-1"


# ============================================================
# RESULT FORMATTER
# ============================================================

def format_result(
    state,
    status,
    thread_id,
):
    return {
        "status": status,
        "thread_id": thread_id,

        # ----------------------------------------------------
        # Incident
        # ----------------------------------------------------

        "service": state.get(
            "service"
        ),

        "incident": state.get(
            "incident"
        ),

        "incident_source": state.get(
            "incident_source"
        ),

        "aws_region": state.get(
            "aws_region"
        ),

        # ----------------------------------------------------
        # Jira
        # ----------------------------------------------------

        "jira_issue_key": state.get(
            "jira_issue_key"
        ),

        "jira_issue_url": state.get(
            "jira_issue_url"
        ),

        "jira_status": state.get(
            "jira_status"
        ),

        # ----------------------------------------------------
        # RCA
        # ----------------------------------------------------

        "root_cause": state.get(
            "root_cause"
        ),

        "supporting_evidence": state.get(
            "supporting_evidence"
        ),

        "impact": state.get(
            "impact"
        ),

        # ----------------------------------------------------
        # Safety
        # ----------------------------------------------------

        "safety_status": state.get(
            "safety_status"
        ),

        "safety_recommendation": state.get(
            "safety_recommendation"
        ),

        "risk_level": state.get(
            "risk_level"
        ),

        # ----------------------------------------------------
        # Human Approval
        # ----------------------------------------------------

        "approval": state.get(
            "approval"
        ),

        # ----------------------------------------------------
        # Remediation
        # ----------------------------------------------------

        "recommendation": state.get(
            "recommendation"
        ),

        "remediation_action": state.get(
            "remediation_action"
        ),

        "remediation_instance_id": state.get(
            "remediation_instance_id"
        ),

        "remediation_simulation_mode": state.get(
            "remediation_simulation_mode",
            False,
        ),

        "execution_status": state.get(
            "execution_status"
        ),

        "verification_status": state.get(
            "verification_status"
        ),

        "verification_message": state.get(
            "verification_message"
        ),

        "rollback_plan": state.get(
            "rollback_plan"
        ),

        "remediation_plan": state.get(
            "final_report"
        ),
    }


# ============================================================
# JIRA CREATION FOR MANUAL INCIDENT
# ============================================================

def _create_manual_jira_incident(
    request: IncidentRequest,
):
    """
    Create a Jira incident before starting LangGraph.

    Manual incidents must have the same Jira lifecycle
    guarantees as CloudWatch-generated incidents.
    """

    incident = {
        "incident": request.incident,
        "service": request.service,
        "incident_source": "Manual Incident",
        "aws_region": os.getenv(
            "AWS_DEFAULT_REGION",
            "us-east-1",
        ),
    }

    jira_result = create_jira_incident(
        incident
    )

    issue_key = jira_result.get(
        "key"
    )

    if not issue_key:
        raise RuntimeError(
            "Jira incident creation succeeded "
            "but no issue key was returned."
        )

    base_url = os.getenv(
        "JIRA_BASE_URL",
        "",
    ).rstrip("/")

    incident["jira_issue_key"] = (
        issue_key
    )

    if base_url:
        incident["jira_issue_url"] = (
            f"{base_url}/browse/{issue_key}"
        )

    mark_in_progress(
        issue_key=issue_key
    )

    incident["jira_status"] = (
        "IN PROGRESS"
    )

    return incident, jira_result


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "service": (
            "SRE Multi-Agent "
            "Incident Response API"
        ),
        "status": "running",
        "version": "1.3.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# MANUAL INCIDENT
# ============================================================

@app.post("/incident")
def create_incident(
    request: IncidentRequest,
):
    # --------------------------------------------------------
    # 1. Create Jira incident FIRST
    # --------------------------------------------------------

    incident, jira_result = (
        _create_manual_jira_incident(
            request
        )
    )

    # --------------------------------------------------------
    # 2. Create LangGraph thread
    # --------------------------------------------------------

    thread_id = str(
        uuid.uuid4()
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # --------------------------------------------------------
    # 3. Persist complete initial state
    # --------------------------------------------------------

    incident_graph.update_state(
        config,
        incident,
    )

    # --------------------------------------------------------
    # 4. Start investigation
    # --------------------------------------------------------

    result = incident_graph.invoke(
        None,
        config=config,
    )

    # --------------------------------------------------------
    # 5. Human approval interrupt
    # --------------------------------------------------------

    if "__interrupt__" in result:
        interrupt_data = result[
            "__interrupt__"
        ][0]

        current_state = (
            incident_graph
            .get_state(config)
            .values
        )

        return {
            "status": "approval_required",

            "thread_id": thread_id,

            "jira": jira_result,

            "approval_request": (
                interrupt_data.value
            ),

            "service": current_state.get(
                "service"
            ),

            "incident": current_state.get(
                "incident"
            ),

            "jira_issue_key": (
                current_state.get(
                    "jira_issue_key"
                )
            ),

            "jira_issue_url": (
                current_state.get(
                    "jira_issue_url"
                )
            ),

            "jira_status": (
                current_state.get(
                    "jira_status"
                )
            ),

            "safety_status": (
                current_state.get(
                    "safety_status"
                )
            ),

            "risk_level": (
                current_state.get(
                    "risk_level"
                )
            ),

            "root_cause": (
                current_state.get(
                    "root_cause"
                )
            ),

            "supporting_evidence": (
                current_state.get(
                    "supporting_evidence"
                )
            ),

            "impact": (
                current_state.get(
                    "impact"
                )
            ),

            "recommendation": (
                current_state.get(
                    "recommendation"
                )
            ),

            "remediation_simulation_mode": (
                current_state.get(
                    "remediation_simulation_mode",
                    False,
                )
            ),
        }

    # --------------------------------------------------------
    # 6. Completed workflow
    # --------------------------------------------------------

    final_state = (
        incident_graph
        .get_state(config)
        .values
    )

    return format_result(
        final_state,
        "completed",
        thread_id,
    )


# ============================================================
# CLOUDWATCH INCIDENTS
# ============================================================

@app.post("/cloudwatch/incidents")
def create_cloudwatch_incidents(
    request: CloudWatchIncidentRequest,
):
    results = start_cloudwatch_incidents(
        region_name=request.region_name
    )

    if not results:
        return {
            "status": "no_incidents",
            "region": request.region_name,
            "incidents_detected": 0,
            "incidents": [],
        }

    incidents = []

    for result in results:
        graph_result = result["result"]

        incident_data = {
            "thread_id": result[
                "thread_id"
            ],

            "incident": result[
                "incident"
            ],
        }

        if "__interrupt__" in graph_result:
            interrupt_data = (
                graph_result[
                    "__interrupt__"
                ][0]
            )

            incident_data[
                "status"
            ] = "approval_required"

            incident_data[
                "approval_request"
            ] = interrupt_data.value

        else:
            incident_data[
                "status"
            ] = "workflow_started"

        incidents.append(
            incident_data
        )

    return {
        "status": "incidents_detected",
        "region": request.region_name,
        "incidents_detected": len(
            incidents
        ),
        "incidents": incidents,
    }


# ============================================================
# HUMAN APPROVAL
# ============================================================

@app.post(
    "/incident/{thread_id}/approve"
)
def approve_incident(
    thread_id: str,
    request: ApprovalRequest,
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
        "rejected",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be one of: "
                "yes, no, approve, approved, "
                "reject, rejected"
            ),
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # --------------------------------------------------------
    # Verify checkpoint
    # --------------------------------------------------------

    checkpoint = (
        incident_graph
        .get_state(config)
    )

    if not checkpoint.values:
        raise HTTPException(
            status_code=404,
            detail=(
                "No active incident found "
                "for the supplied thread_id."
            ),
        )

    # --------------------------------------------------------
    # Read controlled remediation inputs
    # --------------------------------------------------------

    remediation_action = (
        request.remediation_action
        .strip()
        .lower()
    )

    remediation_instance_id = (
        request.remediation_instance_id
        .strip()
    )

    simulation_mode = (
        request.simulation_mode
    )

    # --------------------------------------------------------
    # Persist remediation details when supplied.
    #
    # Backward compatibility:
    #
    # Existing clients/tests can still send:
    #
    #     {"decision": "yes"}
    #
    # The UI can additionally send:
    #
    #     remediation_action
    #     remediation_instance_id
    #     simulation_mode
    # --------------------------------------------------------

    if decision in [
        "yes",
        "approve",
        "approved",
    ]:

        if remediation_action:

            if (
                remediation_action
                == "reboot_ec2"
                and not remediation_instance_id
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "remediation_instance_id is "
                        "required for reboot_ec2."
                    ),
                )

            incident_graph.update_state(
                config,
                {
                    "remediation_action": (
                        remediation_action
                    ),

                    "remediation_instance_id": (
                        remediation_instance_id
                    ),

                    "remediation_simulation_mode": (
                        simulation_mode
                    ),
                },
            )

    # --------------------------------------------------------
    # Resume LangGraph
    # --------------------------------------------------------

    result = incident_graph.invoke(
        Command(
            resume=decision
        ),
        config=config,
    )

    # --------------------------------------------------------
    # Another interrupt
    # --------------------------------------------------------

    if "__interrupt__" in result:
        return {
            "status": "approval_required",

            "thread_id": thread_id,

            "approval_request": (
                result[
                    "__interrupt__"
                ][0].value
            ),
        }

    # --------------------------------------------------------
    # Final persisted state
    # --------------------------------------------------------

    final_state = (
        incident_graph
        .get_state(config)
        .values
    )

    return format_result(
        final_state,
        "completed",
        thread_id,
    )