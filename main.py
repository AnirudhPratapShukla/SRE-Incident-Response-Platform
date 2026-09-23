import re
import uuid

from langgraph.types import Command

from graph.workflow import incident_graph


def clean_text(text):
    """
    Clean Markdown formatting from LLM-generated output
    before displaying it in the terminal.
    """

    if not text:
        return "Not available"

    text = str(text)

    text = re.sub(
        r"^#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = text.replace("**", "")
    text = text.replace("__", "")

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def print_section(title, content):

    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

    print(clean_text(content))


def print_final_report(final_state):

    print("\n")
    print("=" * 60)
    print("                 SRE INCIDENT REPORT")
    print("=" * 60)

    print_section(
        "INCIDENT",
        final_state.get(
            "incident",
            "Not available"
        )
    )

    print_section(
        "SERVICE",
        final_state.get(
            "service",
            "Not available"
        )
    )

    print_section(
        "ROOT CAUSE",
        final_state.get(
            "root_cause",
            "Not available"
        )
    )

    print_section(
        "SUPPORTING EVIDENCE",
        final_state.get(
            "supporting_evidence",
            "Not available"
        )
    )

    print_section(
        "IMPACT",
        final_state.get(
            "impact",
            "Not available"
        )
    )

    print_section(
        "SAFETY",
        f"""
Status     : {final_state.get("safety_status", "Unknown")}
Risk Level : {final_state.get("risk_level", "Unknown")}
"""
    )

    print_section(
        "HUMAN APPROVAL",
        final_state.get(
            "approval",
            "Not required"
        )
    )

    print_section(
        "RECOMMENDATION",
        final_state.get(
            "recommendation",
            "Not available"
        )
    )

    print_section(
        "EXECUTION STATUS",
        final_state.get(
            "execution_status",
            "Not executed"
        )
    )

    print_section(
        "ROLLBACK PLAN",
        final_state.get(
            "rollback_plan",
            "Not available"
        )
    )

    print_section(
        "REMEDIATION PLAN",
        final_state.get(
            "final_report",
            "No remediation plan generated"
        )
    )

    print("\n" + "=" * 60)
    print("              END OF INCIDENT REPORT")
    print("=" * 60)
    print()


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("              SRE MULTI-AGENT SYSTEM")
    print("=" * 60)

    incident = input(
        "\nEnter the incident: "
    ).strip()

    service = input(
        "Enter the service name: "
    ).strip()

    initial_state = {
        "incident": incident,
        "service": service
    }

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\nStarting investigation...")
    print(f"Incident ID: {thread_id}\n")

    result = incident_graph.invoke(
        initial_state,
        config=config
    )

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0]

        approval_request = interrupt_data.value

        print("\n" + "=" * 60)
        print("              HUMAN APPROVAL REQUIRED")
        print("=" * 60)

        print_section(
            "MESSAGE",
            approval_request.get(
                "message",
                "Approval required."
            )
        )

        print_section(
            "SERVICE",
            approval_request.get(
                "service",
                ""
            )
        )

        print_section(
            "ROOT CAUSE",
            approval_request.get(
                "root_cause",
                ""
            )
        )

        print_section(
            "RECOMMENDATION",
            approval_request.get(
                "recommendation",
                ""
            )
        )

        approval = input(
            "\nApprove remediation? (yes/no): "
        ).strip().lower()

        print("\nResuming workflow...\n")

        result = incident_graph.invoke(
            Command(resume=approval),
            config=config
        )

    print_final_report(result)