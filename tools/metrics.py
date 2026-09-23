import json
from pathlib import Path

from langchain.tools import tool


METRICS_FILE = Path("data/metrics/current_metrics.json")


@tool
def get_metrics(service: str) -> str:
    """
    Get current monitoring metrics for a production service.
    """

    print(f"\n[Tool] get_metrics({service})")

    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as file:
            metrics_data = json.load(file)

    except FileNotFoundError:
        return "Metrics data file not found."

    if service not in metrics_data:
        return f"No metrics found for service: {service}"

    metrics = metrics_data[service]

    result = {
        "service": service,
        **metrics
    }

    print("[Tool] Metrics retrieved from JSON")

    return str(result)