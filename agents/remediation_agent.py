from utils.instrumentation import log_agent_execution

from graph.state import IncidentState


@log_agent_execution("remediation_agent")
def remediation_agent(state: IncidentState) -> IncidentState:

    print("\n[Remediation Agent] Building remediation plan...")

    service = state.get(
        "service",
        "unknown"
    )

    root_cause = state.get(
        "root_cause",
        "Not available"
    )

    supporting_evidence = state.get(
        "supporting_evidence",
        "Not available"
    )

    impact = state.get(
        "impact",
        "Not available"
    )

    recommendation = state.get(
        "recommendation",
        "Review the identified root cause and apply "
        "a controlled remediation."
    )

    rollback_plan = state.get(
        "rollback_plan",
        "Restore the previous configuration if the "
        "remediation causes unexpected behavior."
    )

    safety_status = state.get(
        "safety_status",
        "UNKNOWN"
    )

    safety_recommendation = state.get(
        "safety_recommendation",
        "Safety assessment not available."
    )

    risk_level = state.get(
        "risk_level",
        "MEDIUM"
    )

    approval = state.get(
        "approval",
        ""
    ).strip().lower()

    if approval in [
        "yes",
        "approve",
        "approved"
    ]:

        approval_status = "APPROVED"

        execution_status = (
            "APPROVED - READY FOR CONTROLLED EXECUTION"
        )

    elif approval in [
        "no",
        "reject",
        "rejected"
    ]:

        approval_status = "REJECTED"

        execution_status = "NOT EXECUTED"

    else:

        approval_status = "REQUIRED"

        execution_status = "NOT EXECUTED"

    remediation_plan = f"""
============================================================
                    REMEDIATION PLAN
============================================================

SERVICE
------------------------------------------------------------
{service}

ROOT CAUSE
------------------------------------------------------------
{root_cause}

SUPPORTING EVIDENCE
------------------------------------------------------------
{supporting_evidence}

IMPACT
------------------------------------------------------------
{impact}

PROPOSED ACTION
------------------------------------------------------------
{recommendation}

SAFETY ASSESSMENT
------------------------------------------------------------
{safety_recommendation}

RISK LEVEL
------------------------------------------------------------
{risk_level}

SAFETY STATUS
------------------------------------------------------------
{safety_status}

HUMAN APPROVAL
------------------------------------------------------------
{approval_status}

EXECUTION STATUS
------------------------------------------------------------
{execution_status}

ROLLBACK PLAN
------------------------------------------------------------
{rollback_plan}

EXECUTION SAFETY
------------------------------------------------------------
No production infrastructure will be changed
automatically by this system.

The remediation plan is prepared for controlled
execution only.

IMPORTANT
------------------------------------------------------------
This system prepares and validates a remediation
plan. It does NOT directly modify production
infrastructure.
"""

    state["execution_status"] = execution_status
    state["final_report"] = remediation_plan

    print(
        "[Remediation Agent] Remediation plan prepared."
    )

    return state