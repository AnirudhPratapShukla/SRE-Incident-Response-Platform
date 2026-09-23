from agents.rca_agent import parse_rca_response


def test_rca_parser():

    sample_response = """
MOST LIKELY ROOT CAUSE:
Database connection pool exhaustion.

SUPPORTING EVIDENCE:
Database connection timeouts and connection pool
exhaustion warnings are present in the logs.

IMPACT:
Requests are timing out and HTTP 500 errors are
being returned by the order-api service.

RECOMMENDED FIX:
Increase the database connection pool size and
optimize database connection handling.

ROLLBACK PLAN:
Restore the previous database connection pool
configuration if unexpected behavior occurs.

PREVENTION RECOMMENDATIONS:
Perform load testing and monitor database
connection pool utilization.
"""

    result = parse_rca_response(sample_response)

    assert (
        result["root_cause"]
        == "Database connection pool exhaustion."
    )

    assert "connection timeouts" in (
        result["supporting_evidence"]
    )

    assert "HTTP 500" in result["impact"]

    assert "Increase the database connection pool" in (
        result["recommendation"]
    )

    assert "Restore the previous database connection" in (
        result["rollback_plan"]
    )

    print("PASS: RCA parser extracted all sections")


if __name__ == "__main__":

    print("\nStarting RCA Tests...\n")

    test_rca_parser()

    print("\nAll RCA tests passed.")