import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone


load_dotenv()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME"
)

PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "sre-incidents"
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)


# --------------------------------------------------
# Clients
# --------------------------------------------------

gemini_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

pinecone_client = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pinecone_client.Index(
    PINECONE_INDEX_NAME
)


# --------------------------------------------------
# Create embedding
# --------------------------------------------------

def create_embedding(text: str) -> list[float]:

    result = gemini_client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )

    return result.embeddings[0].values


# --------------------------------------------------
# Upsert document
# --------------------------------------------------

def upsert_document(
    document_id: str,
    text: str,
    metadata: dict
):

    embedding = create_embedding(text)

    index.upsert(
        vectors=[
            {
                "id": document_id,
                "values": embedding,
                "metadata": {
                    **metadata,
                    "text": text
                }
            }
        ],
        namespace=PINECONE_NAMESPACE
    )

    return document_id