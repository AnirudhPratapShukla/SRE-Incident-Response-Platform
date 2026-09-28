import os
from typing import Any

import requests
from dotenv import load_dotenv


class JiraClientError(RuntimeError):
    """Raised when a Jira API operation fails."""


class JiraClient:
    """Small Jira Cloud REST API client for the SRE platform."""

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
        timeout: int = 15,
    ):
        load_dotenv()

        self.base_url = (
            base_url or os.getenv("JIRA_BASE_URL", "")
        ).rstrip("/")

        self.email = email or os.getenv("JIRA_EMAIL", "")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN", "")
        self.timeout = timeout

        if not self.base_url:
            raise JiraClientError("JIRA_BASE_URL is not configured.")

        if not self.email:
            raise JiraClientError("JIRA_EMAIL is not configured.")

        if not self.api_token:
            raise JiraClientError("JIRA_API_TOKEN is not configured.")

        self.session = requests.Session()
        self.session.auth = (self.email, self.api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a Jira API request with consistent error handling."""

        url = f"{self.base_url}{path}"

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise JiraClientError(
                f"Jira request failed: {exc}"
            ) from exc

        if not response.ok:
            try:
                details = response.json()
            except ValueError:
                details = response.text[:500]

            raise JiraClientError(
                f"Jira API error {response.status_code}: {details}"
            )

        return response

    def test_connection(self) -> dict[str, Any]:
        """Return the authenticated Jira user."""

        response = self._request(
            "GET",
            "/rest/api/3/myself",
        )

        return response.json()

    def get_project(self, project_key: str) -> dict[str, Any]:
        """Get Jira project information."""

        response = self._request(
            "GET",
            f"/rest/api/3/project/{project_key}",
        )

        return response.json()

    def get_issue_types(
        self,
        project_key: str,
    ) -> list[dict[str, Any]]:
        """Get issue types available for project creation."""

        response = self._request(
            "GET",
            f"/rest/api/3/issue/createmeta/"
            f"{project_key}/issuetypes",
        )

        return response.json().get("issueTypes", [])

    def create_issue(
        self,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a Jira issue."""

        response = self._request(
            "POST",
            "/rest/api/3/issue",
            json={"fields": fields},
        )

        return response.json()