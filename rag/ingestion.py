from pathlib import Path

from rag.pinecone_client import upsert_document


INCIDENTS_DIR = Path(
    "data/incidents"
)


def ingest_incidents():

    incident_files = list(
        INCIDENTS_DIR.glob("*.txt")
    )

    print(
        f"Found {len(incident_files)} incident files."
    )

    for file_path in incident_files:

        text = file_path.read_text(
            encoding="utf-8"
        )

        document_id = file_path.stem

        metadata = {
            "source": file_path.name,
            "type": "historical_incident"
        }

        upsert_document(
            document_id=document_id,
            text=text,
            metadata=metadata
        )

        print(
            f"Uploaded: {document_id}"
        )


if __name__ == "__main__":

    ingest_incidents()