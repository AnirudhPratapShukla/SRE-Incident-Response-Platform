from fastapi.testclient import TestClient

import api.main as api_main


class FakeCheckpoint:

    def __init__(self):
        self.values = {
            "incident": "Test incident",
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
            "safety_status": "APPROVED",
            "safety_recommendation": (
                "APPROVED FOR REVIEW: Remediation appears "
                "non-destructive."
            ),
            "risk_level": "MEDIUM",
            "approval": "yes",
            "recommendation": (
                "Increase the database connection pool size."
            ),
            "execution_status": (
                "APPROVED - READY FOR CONTROLLED EXECUTION"
            ),
            "rollback_plan": (
                "Restore previous connection pool configuration."
            ),
            "final_report": "Remediation plan prepared."
        }


class FakeGraph:

    def __init__(self):

        self.checkpoint = FakeCheckpoint()

    def get_state(self, config):

        return self.checkpoint

    def invoke(self, command, config):

        return self.checkpoint.values


def test_approval_endpoint():

    original_graph = api_main.incident_graph

    try:

        api_main.incident_graph = FakeGraph()

        client = TestClient(api_main.app)

        response = client.post(
            "/incident/test-thread/approve",
            json={
                "decision": "yes"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "completed"

        assert data["thread_id"] == "test-thread"

        assert data["service"] == "order-api"

        assert data["incident"] == "Test incident"

        assert data["root_cause"] == (
            "Database connection pool exhaustion"
        )

        assert data["safety_status"] == "APPROVED"

        assert data["safety_recommendation"] == (
            "APPROVED FOR REVIEW: Remediation appears "
            "non-destructive."
        )

        assert data["risk_level"] == "MEDIUM"

        assert data["approval"] == "yes"

        assert data["execution_status"] == (
            "APPROVED - READY FOR CONTROLLED EXECUTION"
        )

        assert data["recommendation"] == (
            "Increase the database connection pool size."
        )

        print(
            "PASS: FastAPI approval endpoint works"
        )

    finally:

        api_main.incident_graph = original_graph


if __name__ == "__main__":

    print("\nStarting API Tests...\n")

    test_approval_endpoint()

    print("\nAll API tests passed.")