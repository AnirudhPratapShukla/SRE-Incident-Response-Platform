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


if __name__ == "__main__":

    print("\nStarting Remediation Tests...\n")

    test_approved_remediation()
    test_rejected_remediation()
    test_pending_approval()

    print("\nBasic remediation tests passed.")