from pathlib import Path

from langchain.tools import tool


LOG_FILE = Path("data/logs/application.log")


@tool
def get_logs(service: str) -> str:
    """
    Get recent application logs for a production service.
    """

    print(f"\n[Tool] get_logs({service})")

    if not LOG_FILE.exists():
        return "Application log file not found."

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()

    except Exception as e:
        return f"Unable to read log file: {e}"

    service_logs = []

    for line in lines:
        if service in line:
            service_logs.append(line.strip())

    if not service_logs:
        return f"No logs found for service: {service}"

    result = "\n".join(service_logs)

    print("[Tool] Logs retrieved from application.log")

    return result