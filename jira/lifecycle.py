from jira.client import JiraClient


def mark_in_progress(
    issue_key: str,
    client: JiraClient | None = None,
) -> None:
    """Move a Jira incident to In Progress."""

    jira_client = client or JiraClient()

    jira_client.transition_issue_to_status(
        issue_key=issue_key,
        status_name="In Progress",
    )


def mark_in_review(
    issue_key: str,
    client: JiraClient | None = None,
) -> None:
    """Move a Jira incident to In Review."""

    jira_client = client or JiraClient()

    jira_client.transition_issue_to_status(
        issue_key=issue_key,
        status_name="In Review",
    )


def mark_done(
    issue_key: str,
    client: JiraClient | None = None,
) -> None:
    """Move a Jira incident to Done."""

    jira_client = client or JiraClient()

    jira_client.transition_issue_to_status(
        issue_key=issue_key,
        status_name="Done",
    )