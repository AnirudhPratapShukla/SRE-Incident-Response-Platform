import agents.remediation_agent as remediation_module

from agents.remediation_agent import remediation_agent


def create_test_state(approval):

    return {
        "service": "order-api",
        "root_cause": "Database connection pool exhaustion",
        "supporting_evidence": (
            "Database connection timeouts and pool "
            "exhaustion warnings were detected."
        ),
        "impact": (
            "HTTP 500 errors and request timeouts "
            "are affecting the service."
        ),
        "recommendation": (
            "Increase the database connection pool size "
            "and optimize database connection handling."
        ),
        "rollback_plan": (
            "Restore the previous database connection "
            "pool configuration."
        ),
        "safety_status": "APPROVED",
        "safety_recommendation": (
            "APPROVED FOR REVIEW: Remediation appears "
            "non-destructive."
        ),
        "risk_level": "MEDIUM",
        "approval": approval,
    }


# ============================================================
# BASIC REMEDIATION TESTS
# ============================================================

def test_approved_remediation():

    state = create_test_state("yes")

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "APPROVED - READY FOR CONTROLLED EXECUTION"
    )

    assert "Database connection pool exhaustion" in (
        result["final_report"]
    )

    assert "HTTP 500 errors" in (
        result["final_report"]
    )

    assert "Increase the database connection pool" in (
        result["final_report"]
    )

    assert "MEDIUM" in result["final_report"]


def test_rejected_remediation():

    state = create_test_state("no")

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "REJECTED" in result["final_report"]


def test_pending_approval():

    state = create_test_state("")

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "REQUIRED" in result["final_report"]


# ============================================================
# CONTROLLED REMEDIATION VALIDATION
# ============================================================

def test_unsupported_remediation_action():

    state = create_test_state("yes")

    state["remediation_action"] = "terminate_ec2"

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "Unsupported remediation action" in (
        result["remediation_result"]
    )


def test_reboot_requires_instance_id():

    state = create_test_state("yes")

    state["remediation_action"] = "reboot_ec2"

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "no instance ID" in (
        result["remediation_result"]
    )


# ============================================================
# SUCCESSFUL REBOOT + VERIFICATION
# ============================================================

def test_reboot_approved_and_executed(monkeypatch):

    state = create_test_state("yes")

    state["remediation_action"] = "reboot_ec2"
    state["remediation_instance_id"] = "i-123abc456def"

    def fake_execute_reboot(instance_id):

        assert instance_id == "i-123abc456def"

        return {
            "instance_id": instance_id,
            "approved": True,
            "dry_run": False,
            "executed": True,
            "verified": True,
            "success": True,
            "message": (
                "EC2 reboot executed through MCP and "
                "recovery was successfully verified."
            ),
        }

    monkeypatch.setattr(
        remediation_module,
        "_execute_reboot",
        fake_execute_reboot,
    )

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "EXECUTED - EC2 REBOOT VERIFIED THROUGH MCP"
    )

    assert result["remediation_result"] == (
        "EC2 reboot executed through MCP and "
        "recovery was successfully verified."
    )

    assert result["verification_status"] == "VERIFIED"

    assert "EXECUTED" in result["final_report"]

    assert "VERIFIED" in result["final_report"]


# ============================================================
# FAILED REBOOT / VERIFICATION
# ============================================================

def test_reboot_execution_failure(monkeypatch):

    state = create_test_state("yes")

    state["remediation_action"] = "reboot_ec2"
    state["remediation_instance_id"] = "i-123abc456def"

    def fake_execute_reboot(instance_id):

        assert instance_id == "i-123abc456def"

        return {
            "instance_id": instance_id,
            "approved": True,
            "dry_run": False,
            "executed": False,
            "verified": False,
            "success": False,
            "message": (
                "MCP reboot execution failed."
            ),
        }

    monkeypatch.setattr(
        remediation_module,
        "_execute_reboot",
        fake_execute_reboot,
    )

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "EXECUTION FAILED"
    )

    assert "MCP reboot execution failed" in (
        result["remediation_result"]
    )

    assert result["verification_status"] == "NOT RUN"


def test_reboot_execution_without_recovery_verification(
    monkeypatch
):

    state = create_test_state("yes")

    state["remediation_action"] = "reboot_ec2"
    state["remediation_instance_id"] = "i-123abc456def"

    def fake_execute_reboot(instance_id):

        return {
            "instance_id": instance_id,
            "approved": True,
            "dry_run": False,
            "executed": True,
            "verified": False,
            "success": False,
            "message": (
                "EC2 reboot executed, but recovery "
                "verification failed."
            ),
        }

    monkeypatch.setattr(
        remediation_module,
        "_execute_reboot",
        fake_execute_reboot,
    )

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "EXECUTION FAILED"
    )

    assert result["verification_status"] == "FAILED"

    assert "verification failed" in (
        result["verification_message"]
    ).lower()


# ============================================================
# DIRECT MCP EXECUTION + VERIFICATION
# ============================================================

def test_execute_reboot_with_successful_verification(
    monkeypatch
):

    async def fake_reboot_ec2_instance(
        instance_id,
        approved,
        dry_run,
    ):

        assert instance_id == "i-123abc456def"
        assert approved is True

        if dry_run:

            return {
                "instance_id": instance_id,
                "approved": True,
                "dry_run": True,
                "executed": False,
                "success": True,
                "message": (
                    "Dry-run validation successful."
                ),
            }

        return {
            "instance_id": instance_id,
            "approved": True,
            "dry_run": False,
            "executed": True,
            "success": True,
            "message": (
                "EC2 reboot requested successfully."
            ),
        }

    async def fake_get_ec2_instance_status(
        instance_id,
    ):

        return {
            "instance_id": instance_id,
            "found": True,
            "instance_state": "running",
            "system_status": "ok",
            "instance_status": "ok",
        }

    async def fake_sleep(seconds):

        return None

    monkeypatch.setattr(
        remediation_module,
        "reboot_ec2_instance",
        fake_reboot_ec2_instance,
    )

    monkeypatch.setattr(
        remediation_module,
        "get_ec2_instance_status",
        fake_get_ec2_instance_status,
    )

    monkeypatch.setattr(
        remediation_module.asyncio,
        "sleep",
        fake_sleep,
    )

    result = remediation_module._execute_reboot(
        "i-123abc456def"
    )

    assert result["success"] is True
    assert result["executed"] is True
    assert result["verified"] is True
    assert "verified" in (
        result["message"]
    ).lower()


def test_execute_reboot_with_failed_verification(
    monkeypatch
):

    async def fake_reboot_ec2_instance(
        instance_id,
        approved,
        dry_run,
    ):

        if dry_run:

            return {
                "instance_id": instance_id,
                "approved": True,
                "dry_run": True,
                "executed": False,
                "success": True,
                "message": (
                    "Dry-run validation successful."
                ),
            }

        return {
            "instance_id": instance_id,
            "approved": True,
            "dry_run": False,
            "executed": True,
            "success": True,
            "message": (
                "EC2 reboot requested successfully."
            ),
        }

    async def fake_get_ec2_instance_status(
        instance_id,
    ):

        return {
            "instance_id": instance_id,
            "found": True,
            "instance_state": "stopped",
            "system_status": "initializing",
            "instance_status": "initializing",
        }

    async def fake_sleep(seconds):

        return None

    monkeypatch.setattr(
        remediation_module,
        "reboot_ec2_instance",
        fake_reboot_ec2_instance,
    )

    monkeypatch.setattr(
        remediation_module,
        "get_ec2_instance_status",
        fake_get_ec2_instance_status,
    )

    monkeypatch.setattr(
        remediation_module.asyncio,
        "sleep",
        fake_sleep,
    )

    result = remediation_module._execute_reboot(
        "i-123abc456def"
    )

    assert result["success"] is False
    assert result["executed"] is True
    assert result["verified"] is False
    assert "verification failed" in (
        result["message"]
    ).lower()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\nStarting Remediation Tests...\n")

    test_approved_remediation()
    test_rejected_remediation()
    test_pending_approval()

    print("\nBasic remediation tests passed.")