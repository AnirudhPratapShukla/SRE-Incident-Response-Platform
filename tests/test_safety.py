from agents.safety_agent import safety_agent


def test_safe_remediation():

    state = {
        "root_cause": "Database connection pool exhaustion",
        "recommendation": "Increase database connection pool size"
    }

    result = safety_agent(state)

    assert result["safety_status"] == "APPROVED"

    print("PASS: Safe remediation approved")


def test_dangerous_remediation():

    state = {
        "root_cause": "Delete production database immediately"
    }

    result = safety_agent(state)

    assert result["safety_status"] == "BLOCKED"

    print("PASS: Dangerous remediation blocked")


if __name__ == "__main__":

    print("\nStarting Safety Tests...\n")

    test_safe_remediation()
    test_dangerous_remediation()

    print("\nAll safety tests passed.")