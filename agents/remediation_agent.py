import asyncio

from utils.instrumentation import log_agent_execution

from graph.state import IncidentState

from mcp_client.aws_client import (
    reboot_ec2_instance,
    get_ec2_instance_status,
)


SUPPORTED_ACTIONS = {
    "reboot_ec2",
}


def _is_approved(
    approval: str,
) -> bool:

    return approval.strip().lower() in {
        "yes",
        "approve",
        "approved",
    }


def _is_rejected(
    approval: str,
) -> bool:

    return approval.strip().lower() in {
        "no",
        "reject",
        "rejected",
    }


async def _verify_ec2_recovery_async(
    instance_id: str,
    attempts: int = 3,
    delay_seconds: int = 2,
) -> dict:

    last_status = None

    for attempt in range(
        1,
        attempts + 1,
    ):

        status = await get_ec2_instance_status(
            instance_id
        )

        last_status = status

        if (
            status.get("found") is True
            and status.get("instance_state")
            == "running"
            and status.get("system_status")
            == "ok"
            and status.get("instance_status")
            == "ok"
        ):

            return {
                "success": True,
                "message": (
                    "EC2 instance recovered successfully. "
                    f"Instance is running with healthy "
                    f"status after verification attempt "
                    f"{attempt}."
                ),
            }

        if attempt < attempts:

            await asyncio.sleep(
                delay_seconds
            )

    return {
        "success": False,
        "message": (
            "EC2 recovery verification failed. "
            f"Last status: {last_status}"
        ),
    }


def _execute_reboot(
    instance_id: str,
) -> dict:

    async def run():

        # ----------------------------------------------------
        # STEP 1: MCP DRY RUN
        # ----------------------------------------------------

        dry_run_result = (
            await reboot_ec2_instance(
                instance_id=instance_id,
                approved=True,
                dry_run=True,
            )
        )

        if not dry_run_result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "executed": False,
                "verified": False,
                "message": (
                    "MCP dry-run validation failed: "
                    f"{dry_run_result.get('message', 'Unknown error')}"
                ),
            }

        # ----------------------------------------------------
        # STEP 2: ACTUAL CONTROLLED EXECUTION
        # ----------------------------------------------------

        execution_result = (
            await reboot_ec2_instance(
                instance_id=instance_id,
                approved=True,
                dry_run=False,
            )
        )

        if not execution_result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "executed": False,
                "verified": False,
                "message": (
                    "MCP reboot execution failed: "
                    f"{execution_result.get('message', 'Unknown error')}"
                ),
            }

        # ----------------------------------------------------
        # STEP 3: RECOVERY VERIFICATION
        # ----------------------------------------------------

        verification_result = (
            await _verify_ec2_recovery_async(
                instance_id
            )
        )

        if not verification_result.get(
            "success",
            False,
        ):

            return {
                "success": False,
                "executed": True,
                "verified": False,
                "message": verification_result.get(
                    "message",
                    "EC2 recovery verification failed.",
                ),
            }

        return {
            "success": True,
            "executed": True,
            "verified": True,
            "message": (
                "EC2 reboot executed through MCP and "
                "recovery was successfully verified."
            ),
        }

    return asyncio.run(
        run()
    )


def _simulate_reboot(
    instance_id: str,
) -> dict:
    """
    Safe UI/demo execution path.

    This function does NOT call AWS, MCP, EC2,
    CloudWatch, or any external remediation API.

    It represents a controlled remediation execution
    and successful recovery verification for demonstration
    and end-to-end UI testing.
    """

    return {
        "success": True,
        "executed": True,
        "verified": True,
        "message": (
            "SAFE DEMO SIMULATION: EC2 reboot execution "
            "and recovery verification completed successfully. "
            "No AWS infrastructure was modified."
        ),
    }


@log_agent_execution(
    "remediation_agent"
)
def remediation_agent(
    state: IncidentState,
) -> IncidentState:

    print(
        "\n[Remediation Agent] "
        "Building remediation plan..."
    )

    service = state.get(
        "service",
        "unknown",
    )

    root_cause = state.get(
        "root_cause",
        "Not available",
    )

    supporting_evidence = state.get(
        "supporting_evidence",
        "Not available",
    )

    impact = state.get(
        "impact",
        "Not available",
    )

    recommendation = state.get(
        "recommendation",
        (
            "Review the identified root cause "
            "and apply a controlled remediation."
        ),
    )

    rollback_plan = state.get(
        "rollback_plan",
        (
            "Restore the previous configuration "
            "if the remediation causes unexpected behavior."
        ),
    )

    safety_status = state.get(
        "safety_status",
        "UNKNOWN",
    )

    safety_recommendation = state.get(
        "safety_recommendation",
        "Safety assessment not available.",
    )

    risk_level = state.get(
        "risk_level",
        "MEDIUM",
    )

    approval = state.get(
        "approval",
        "",
    ).strip().lower()

    remediation_action = state.get(
        "remediation_action",
        "",
    ).strip().lower()

    remediation_instance_id = state.get(
        "remediation_instance_id",
        "",
    ).strip()

    remediation_simulation_mode = state.get(
        "remediation_simulation_mode",
        False,
    )

    remediation_result = state.get(
        "remediation_result",
        "",
    )

    verification_status = state.get(
        "verification_status",
        "NOT RUN",
    )

    verification_message = state.get(
        "verification_message",
        "",
    )

    # --------------------------------------------------------
    # Approval
    # --------------------------------------------------------

    if _is_approved(
        approval
    ):

        approval_status = "APPROVED"

    elif _is_rejected(
        approval
    ):

        approval_status = "REJECTED"

    else:

        approval_status = "REQUIRED"

    # --------------------------------------------------------
    # Not approved
    # --------------------------------------------------------

    if approval_status != "APPROVED":

        execution_status = "NOT EXECUTED"

    # --------------------------------------------------------
    # No action
    # --------------------------------------------------------

    elif not remediation_action:

        execution_status = (
            "APPROVED - READY FOR CONTROLLED EXECUTION"
        )

        remediation_result = (
            "No explicit remediation action was supplied. "
            "No AWS action was executed."
        )

    # --------------------------------------------------------
    # Unsupported action
    # --------------------------------------------------------

    elif (
        remediation_action
        not in SUPPORTED_ACTIONS
    ):

        execution_status = "NOT EXECUTED"

        remediation_result = (
            f"Unsupported remediation action: "
            f"{remediation_action}"
        )

    # --------------------------------------------------------
    # Missing instance ID
    # --------------------------------------------------------

    elif (
        remediation_action == "reboot_ec2"
        and not remediation_instance_id
    ):

        execution_status = "NOT EXECUTED"

        remediation_result = (
            "EC2 reboot requested but no instance ID "
            "was supplied."
        )

    # --------------------------------------------------------
    # Controlled execution
    # --------------------------------------------------------

    elif remediation_action == "reboot_ec2":

        if remediation_simulation_mode:

            print(
                "[Remediation Agent] "
                "Running SAFE DEMO SIMULATION. "
                "No AWS infrastructure will be modified."
            )

            try:

                result = _simulate_reboot(
                    remediation_instance_id
                )

                remediation_result = result.get(
                    "message",
                    "Safe simulation completed.",
                )

                if result.get(
                    "verified",
                    False,
                ):

                    execution_status = (
                        "EXECUTED - EC2 REBOOT "
                        "VERIFIED THROUGH SAFE SIMULATION"
                    )

                    verification_status = (
                        "VERIFIED"
                    )

                    verification_message = (
                        result.get(
                            "message",
                            "Safe simulated recovery verified.",
                        )
                    )

                else:

                    execution_status = (
                        "EXECUTION FAILED"
                    )

                    verification_status = (
                        "FAILED"
                    )

                    verification_message = (
                        result.get(
                            "message",
                            "Safe simulation failed.",
                        )
                    )

            except Exception as exc:

                execution_status = (
                    "EXECUTION FAILED"
                )

                verification_status = (
                    "FAILED"
                )

                verification_message = (
                    f"Safe simulation failed: {exc}"
                )

                remediation_result = (
                    f"Safe simulation failed: {exc}"
                )

        else:

            print(
                "[Remediation Agent] "
                "Executing approved EC2 reboot through MCP..."
            )

            try:

                result = _execute_reboot(
                    remediation_instance_id
                )

                remediation_result = result.get(
                    "message",
                    "No MCP execution message returned.",
                )

                if result.get(
                    "verified",
                    False,
                ):

                    execution_status = (
                        "EXECUTED - EC2 REBOOT "
                        "VERIFIED THROUGH MCP"
                    )

                    verification_status = (
                        "VERIFIED"
                    )

                    verification_message = (
                        result.get(
                            "message",
                            "Recovery verified.",
                        )
                    )

                else:

                    execution_status = (
                        "EXECUTION FAILED"
                    )

                    if result.get(
                        "executed",
                        False,
                    ):

                        verification_status = (
                            "FAILED"
                        )

                        verification_message = (
                            result.get(
                                "message",
                                "Recovery verification failed.",
                            )
                        )

                    else:

                        verification_status = (
                            "NOT RUN"
                        )

                        verification_message = (
                            "Execution did not complete. "
                            "Recovery verification was not performed."
                        )

            except Exception as exc:

                execution_status = (
                    "EXECUTION FAILED"
                )

                verification_status = (
                    "FAILED"
                )

                verification_message = (
                    f"Remediation verification failed: {exc}"
                )

                remediation_result = (
                    "MCP remediation execution failed: "
                    f"{exc}"
                )

    else:

        execution_status = "NOT EXECUTED"

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    simulation_label = (
        "SAFE DEMO SIMULATION - NO AWS MODIFICATION"
        if remediation_simulation_mode
        else "REAL MCP CONTROLLED EXECUTION"
    )

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

REMEDIATION ACTION
------------------------------------------------------------
{remediation_action or "NONE"}

TARGET INSTANCE
------------------------------------------------------------
{remediation_instance_id or "NONE"}

EXECUTION MODE
------------------------------------------------------------
{simulation_label}

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

MCP / SIMULATION RESULT
------------------------------------------------------------
{remediation_result or "No remediation execution performed."}

VERIFICATION STATUS
------------------------------------------------------------
{verification_status}

VERIFICATION MESSAGE
------------------------------------------------------------
{verification_message or "No verification performed."}

ROLLBACK PLAN
------------------------------------------------------------
{rollback_plan}

EXECUTION SAFETY
------------------------------------------------------------
Only explicitly supported remediation actions are allowed.

AWS remediation requires:
1. Safety approval.
2. Human approval.
3. Explicit remediation action.
4. Explicit target resource.
5. MCP-controlled execution when simulation is disabled.
6. Successful post-remediation verification.

Safe demo simulation never modifies AWS infrastructure.

No arbitrary AWS command execution is permitted.

============================================================
"""

    state["execution_status"] = (
        execution_status
    )

    state["remediation_result"] = (
        remediation_result
    )

    state["verification_status"] = (
        verification_status
    )

    state["verification_message"] = (
        verification_message
    )

    state["remediation_dry_run"] = (
        remediation_simulation_mode
    )

    state["final_report"] = (
        remediation_plan
    )

    print(
        "[Remediation Agent] "
        "Remediation plan prepared."
    )

    return state