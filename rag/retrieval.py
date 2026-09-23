from rag.pinecone_client import (
    create_embedding,
    index,
    PINECONE_NAMESPACE
)


def search_incidents(
    query: str,
    top_k: int = 3
):

    query_embedding = create_embedding(
        query
    )

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=PINECONE_NAMESPACE,
        include_metadata=True
    )

    return results


if __name__ == "__main__":

    query = (
        "HTTP 500 errors caused by "
        "database connection pool exhaustion"
    )

    results = search_incidents(query)

    for match in results.matches:

        print(
            "\nScore:",
            match["score"]
        )

        print(
            "ID:",
            match["id"]
        )

        print(
            "Source:",
            match["metadata"]["source"]
        )

        print(
            match["metadata"]["text"][:500]
        )
