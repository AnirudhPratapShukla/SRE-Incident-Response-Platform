from utils.instrumentation import log_agent_execution

from graph.state import IncidentState

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:3b"
)


def parse_rca_response(response_text: str) -> dict:
    """
    Convert the LLM's structured RCA response into
    separate fields for the incident state.
    """

    sections = {
        "root_cause": "",
        "supporting_evidence": "",
        "impact": "",
        "recommendation": "",
        "rollback_plan": ""
    }

    current_section = None

    for line in response_text.splitlines():

        line_clean = line.strip()

        if not line_clean:
            continue

        lower_line = line_clean.lower()

        if "most likely root cause" in lower_line:
            current_section = "root_cause"
            continue

        if "supporting evidence" in lower_line:
            current_section = "supporting_evidence"
            continue

        if "impact" in lower_line:
            current_section = "impact"
            continue

        if "recommended fix" in lower_line:
            current_section = "recommendation"
            continue

        if "prevention recommendations" in lower_line:
            current_section = "recommendation"
            continue

        if "rollback plan" in lower_line:
            current_section = "rollback_plan"
            continue

        if current_section:
            sections[current_section] += line + "\n"

    # Clean extracted sections
    for key in sections:
        sections[key] = sections[key].strip()

    # Fallback if the model does not follow the requested format
    if not sections["root_cause"]:
        sections["root_cause"] = response_text.strip()

    if not sections["recommendation"]:
        sections["recommendation"] = (
            "Review the identified root cause and apply "
            "a controlled remediation."
        )

    if not sections["rollback_plan"]:
        sections["rollback_plan"] = (
            "Restore the previous configuration if the "
            "remediation causes unexpected behavior."
        )

    return sections


@log_agent_execution("rca_agent")
def rca_agent(state: IncidentState) -> IncidentState:

    print("\n[RCA Agent] Analyzing incident evidence...")

    service = state.get(
        "service",
        "unknown"
    )

    metrics = state.get(
        "metrics",
        "No metrics available."
    )

    logs = state.get(
        "logs",
        "No logs available."
    )

    infrastructure = state.get(
        "infrastructure",
        "No infrastructure information available."
    )

    historical_incidents = state.get(
        "historical_incidents",
        "No historical incidents available."
    )

    prompt = f"""
You are an experienced Site Reliability Engineer
performing Root Cause Analysis.

Analyze the following production incident.

SERVICE:
{service}

CURRENT METRICS:
{metrics}

CURRENT LOGS:
{logs}

INFRASTRUCTURE STATUS:
{infrastructure}

HISTORICAL INCIDENTS:
{historical_incidents}

Perform a structured RCA.

IMPORTANT:
Return the analysis using EXACTLY these section headings:

MOST LIKELY ROOT CAUSE:
Provide the most likely technical root cause.

SUPPORTING EVIDENCE:
Explain the evidence from metrics and logs.

IMPACT:
Explain the likely impact on the service.

RECOMMENDED FIX:
Provide a practical remediation recommendation.

ROLLBACK PLAN:
Explain how the remediation can be safely rolled back.

PREVENTION RECOMMENDATIONS:
Provide recommendations to reduce the chance of recurrence.

Correlate the metrics, logs, infrastructure status,
and historical incidents.

Do not invent infrastructure problems that are not
supported by the provided evidence.

Clearly explain why the identified root cause is
the most likely explanation.

Keep the analysis concise and technically specific.
"""

    response = llm.invoke(prompt)

    rca_text = response.content

    parsed_rca = parse_rca_response(rca_text)

    state["root_cause"] = parsed_rca["root_cause"]
    state["supporting_evidence"] = parsed_rca[
        "supporting_evidence"
    ]
    state["impact"] = parsed_rca["impact"]
    state["recommendation"] = parsed_rca[
        "recommendation"
    ]
    state["rollback_plan"] = parsed_rca[
        "rollback_plan"
    ]

    print(
        "[RCA Agent] Root Cause Analysis completed."
    )

    return state