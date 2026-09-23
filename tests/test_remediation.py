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
        "approval": approval
    }


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

    print("PASS: Approved remediation test")


def test_rejected_remediation():

    state = create_test_state("no")

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "REJECTED" in result["final_report"]

    print("PASS: Rejected remediation test")


def test_pending_approval():

    state = create_test_state("")

    result = remediation_agent(state)

    assert result["execution_status"] == (
        "NOT EXECUTED"
    )

    assert "REQUIRED" in result["final_report"]

    print("PASS: Pending approval test")


if __name__ == "__main__":

    print("\nStarting Remediation Tests...\n")

    test_approved_remediation()
    test_rejected_remediation()
    test_pending_approval()

    print("\nAll remediation tests passed.")