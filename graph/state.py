from typing import TypedDict


class IncidentState(TypedDict, total=False):

    # Incident information
    incident: str
    service: str

    # Investigation data
    metrics: str
    logs: str
    infrastructure: str
    historical_incidents: str

    # Analysis
    root_cause: str
    supporting_evidence: str
    impact: str
    recommendation: str
    rollback_plan: str

    # Safety
    safety_status: str
    safety_recommendation: str
    risk_level: str

    # Human approval
    approval: str

    # Remediation
    execution_status: str
    final_report: str