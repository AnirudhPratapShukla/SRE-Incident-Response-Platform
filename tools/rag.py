from langchain.tools import tool

from rag.retrieval import search_incidents


@tool
def search_historical_incidents(query: str) -> str:
    """
    Search historical SRE incidents for similar problems,
    root causes, resolutions, and prevention steps.
    """

    print("\n[Tool] search_historical_incidents()")
    print(f"[Tool] Query: {query}")

    results = search_incidents(query, top_k=3)

    if not results.matches:
        print("[Tool] No historical incidents found")
        return "No similar historical incidents found."

    output = []

    for match in results.matches:
        metadata = match["metadata"]

        output.append(
            f"""
Incident: {match["id"]}
Similarity Score: {match["score"]}

{metadata["text"]}
"""
        )

    print(
        f"[Tool] Found {len(results.matches)} historical incidents"
    )

    return "\n".join(output)


if __name__ == "__main__":

    query = input("Search historical incidents: ")

    result = search_historical_incidents.invoke(
        {"query": query}
    )

    print("\nHistorical Incident Results:\n")
    print(result)