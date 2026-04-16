import uuid

from qdrant_client import models

from core.config import settings
from storage.my_qdrant_client import client


def upload_points(chunks, dense_vectors, sparse_vectors) -> None:
    points = []

    for i, chunk in enumerate(chunks):
        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_DNS,
                f"{chunk['document_id']}:{chunk['chunk_id']}",
            )
        )

        payload = {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "source": chunk["source"],
            "file_type": chunk["file_type"],
            "user_id": str(chunk["user_id"]),
            "document_id": chunk["document_id"],
        }

        points.append(
            models.PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vectors[i],
                    "sparse": models.SparseVector(
                        indices=sparse_vectors[i].indices,
                        values=sparse_vectors[i].values,
                    ),
                },
                payload=payload,
            )
        )

    client.upsert(
        collection_name=settings.DOCUMENTS_COLLECTION_NAME,
        points=points,
    )