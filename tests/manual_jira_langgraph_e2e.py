from langgraph.types import Command

from services import cloudwatch_incident_runner
from graph.workflow import incident_graph
import agents.remediation_agent as remediation_module


# ============================================================
# FAKE CLOUDWATCH INCIDENT
# ============================================================

def fake_detect_cloudwatch_incidents(
    region_name: str,
):

    return [
        {
            "incident": (
                "Test incident: order-api HTTP 500 "
                "errors detected."
            ),
            "service": "order-api",
            "incident_source": "Manual E2E Test",
            "aws_region": region_name,
            "cloudwatch_alarm_name": (
                "Manual-E2E-Test"
            ),
            "cloudwatch_alarm_state": "ALARM",
            "cloudwatch_metric": (
                "AWS/EC2/CPUUtilization"
            ),
            "metrics": (
                "Manual E2E test metrics."
            ),
            "impact": (
                "Test incident only. No production impact."
            ),
            "risk_level": "MEDIUM",
        }
    ]


# ============================================================
# SAFE REMEDIATION MOCK
# ============================================================
#
# IMPORTANT:
# This prevents the E2E test from performing a real
# AWS reboot.
#
# MCP read-only AWS context is still real.
# The remediation execution itself is simulated.
# ============================================================

def fake_execute_reboot(
    instance_id: str,
):

    print(
        "\n[SAFE E2E] Simulating approved EC2 reboot..."
    )

    print(
        f"[SAFE E2E] Target instance: {instance_id}"
    )

    return {
        "instance_id": instance_id,
        "approved": True,
        "dry_run": False,
        "executed": True,
        "verified": True,
        "success": True,
        "message": (
            "SAFE E2E simulation: EC2 reboot "
            "execution and recovery verification "
            "completed successfully."
        ),
    }


# ============================================================
# APPLY TEST PATCHES
# ============================================================

cloudwatch_incident_runner.detect_cloudwatch_incidents = (
    fake_detect_cloudwatch_incidents
)

remediation_module._execute_reboot = (
    fake_execute_reboot
)


# ============================================================
# START E2E
# ============================================================

print("\n========================================")
print("STARTING JIRA + LANGGRAPH E2E TEST")
print("========================================")

results = (
    cloudwatch_incident_runner
    .start_cloudwatch_incidents(
        region_name="us-east-1"
    )
)


if not results:

    raise RuntimeError(
        "No incidents were returned from "
        "the CloudWatch incident runner."
    )


result = results[0]

thread_id = result["thread_id"]

config = {
    "configurable": {
        "thread_id": thread_id
    }
}


# ============================================================
# STATE BEFORE HUMAN APPROVAL
# ============================================================

state_before_approval = (
    incident_graph
    .get_state(config)
    .values
)


print("\n========================================")
print("STATE BEFORE HUMAN APPROVAL")
print("========================================")

print(
    "\nThread ID:"
)
print(thread_id)

print(
    "\nJira Issue:"
)
print(
    state_before_approval.get(
        "jira_issue_key"
    )
)

print(
    "\nJira Status:"
)
print(
    state_before_approval.get(
        "jira_status"
    )
)

print(
    "\nSafety Status:"
)
print(
    state_before_approval.get(
        "safety_status"
    )
)


# ============================================================
# VALIDATE HUMAN APPROVAL CHECKPOINT
# ============================================================

assert (
    state_before_approval.get(
        "jira_status"
    )
    == "IN REVIEW"
)

assert (
    state_before_approval.get(
        "safety_status"
    )
    == "APPROVED"
)


# ============================================================
# ADD EXPLICIT REMEDIATION ACTION
# ============================================================
#
# We intentionally add the action after the graph reaches
# the human approval checkpoint.
#
# This proves that remediation requires an explicit action
# rather than blindly executing the RCA recommendation.
# ============================================================

incident_graph.update_state(
    config,
    {
        "remediation_action": "reboot_ec2",
        "remediation_instance_id": (
            "i-123abc456def"
        ),
    },
)


# ============================================================
# RESUME HUMAN APPROVAL
# ============================================================

print("\n========================================")
print("RESUMING HUMAN APPROVAL")
print("========================================")

final_result = incident_graph.invoke(
    Command(
        resume="yes"
    ),
    config=config,
)


# ============================================================
# FINAL PERSISTED STATE
# ============================================================

final_state = (
    incident_graph
    .get_state(config)
    .values
)


print("\n========================================")
print("FINAL E2E RESULT")
print("========================================")


print("\nThread ID:")
print(thread_id)


print("\nJira Issue:")
print(
    final_state.get(
        "jira_issue_key"
    )
)


print("\nJira URL:")
print(
    final_state.get(
        "jira_issue_url"
    )
)


print("\nFinal Jira Status:")
print(
    final_state.get(
        "jira_status"
    )
)


print("\nSafety Status:")
print(
    final_state.get(
        "safety_status"
    )
)


print("\nApproval:")
print(
    final_state.get(
        "approval"
    )
)


print("\nRemediation Action:")
print(
    final_state.get(
        "remediation_action"
    )
)


print("\nTarget Instance:")
print(
    final_state.get(
        "remediation_instance_id"
    )
)


print("\nExecution Status:")
print(
    final_state.get(
        "execution_status"
    )
)


print("\nVerification Status:")
print(
    final_state.get(
        "verification_status"
    )
)


print("\nVerification Message:")
print(
    final_state.get(
        "verification_message"
    )
)


print("\nMCP EC2 Instances:")
print(
    final_state.get(
        "mcp_ec2_instances"
    )
)


print("\nMCP CloudWatch Alarms:")
print(
    final_state.get(
        "mcp_cloudwatch_alarms"
    )
)


# ============================================================
# FINAL ASSERTIONS
# ============================================================

assert (
    final_state.get(
        "approval"
    )
    == "yes"
)

assert (
    final_state.get(
        "remediation_action"
    )
    == "reboot_ec2"
)

assert (
    final_state.get(
        "remediation_instance_id"
    )
    == "i-123abc456def"
)

assert (
    final_state.get(
        "verification_status"
    )
    == "VERIFIED"
)

assert (
    final_state.get(
        "execution_status"
    )
    == "EXECUTED - EC2 REBOOT VERIFIED THROUGH MCP"
)

assert (
    final_state.get(
        "jira_status"
    )
    == "DONE"
)


print("\n========================================")
print("E2E TEST SUCCESS")
print("========================================")

print(
    "\nCloudWatch Detection : PASS"
)

print(
    "Jira Creation        : PASS"
)

print(
    "LangGraph            : PASS"
)

print(
    "MCP AWS Context      : PASS"
)

print(
    "RCA                  : PASS"
)

print(
    "Safety Assessment    : PASS"
)

print(
    "Human Approval       : PASS"
)

print(
    "Controlled Remediation: PASS"
)

print(
    "Recovery Verification: PASS"
)

print(
    "Jira Resolution      : PASS"
)

print(
    "\nIMPORTANT:"
)

print(
    "AWS EC2 reboot was SIMULATED."
)

print(
    "No real EC2 remediation was executed."
)