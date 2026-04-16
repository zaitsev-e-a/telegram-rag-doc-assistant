from qdrant_client import models

from core.config import settings
from storage.my_qdrant_client import client


def create_qdrant_collection() -> None:
    collections = client.get_collections().collections
    names = [collection.name for collection in collections]

    if settings.DOCUMENTS_COLLECTION_NAME in names:
        return

    client.create_collection(
        collection_name=settings.DOCUMENTS_COLLECTION_NAME,
        vectors_config={
            "dense": models.VectorParams(
                size=settings.DENSE_VECTOR_SIZE,
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams()
        },
    )

    for field_name in ("user_id", "document_id", "source", "file_type", "chunk_id"):
        try:
            client.create_payload_index(
                collection_name=settings.DOCUMENTS_COLLECTION_NAME,
                field_name=field_name,
                field_schema=(
                    models.PayloadSchemaType.INTEGER
                    if field_name == "chunk_id"
                    else models.PayloadSchemaType.KEYWORD
                ),
            )
        except Exception:
            pass