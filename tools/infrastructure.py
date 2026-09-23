import json
from pathlib import Path

from langchain.tools import tool


INFRA_FILE = Path(
    "data/metrics/infrastructure.json"
)


@tool
def get_infrastructure_status(service: str) -> str:
    """
    Get read-only infrastructure health information
    for a production service.
    """

    print(
        f"\n[Tool] get_infrastructure_status({service})"
    )

    if not INFRA_FILE.exists():
        return "Infrastructure data file not found."

    try:
        with open(
            INFRA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            infrastructure = json.load(file)

    except Exception as e:
        return f"Unable to read infrastructure data: {e}"

    if service not in infrastructure:
        return f"No infrastructure data found for {service}"

    status = infrastructure[service]

    print(
        "[Tool] Infrastructure status retrieved from JSON"
    )

    return json.dumps(
        {
            "service": service,
            **status
        },
        indent=2
    )