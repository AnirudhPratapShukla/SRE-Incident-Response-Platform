from typing import TypedDict


class IncidentState(TypedDict, total=False):

    # Incident information
    incident: str
    service: str
    incident_source: str

    # AWS context
    aws_region: str
    cloudwatch_alarm_name: str
    cloudwatch_alarm_state: str
    cloudwatch_metric: str

    # MCP AWS context
    mcp_ec2_instances: list[dict]
    mcp_cloudwatch_alarms: list[dict]

    # Jira incident
    jira_issue_key: str
    jira_issue_url: str
    jira_status: str

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
    remediation_action: str
    remediation_instance_id: str
    remediation_dry_run: bool
    remediation_result: str

    # Verification
    verification_status: str
    verification_message: str

    execution_status: str
    final_report: str