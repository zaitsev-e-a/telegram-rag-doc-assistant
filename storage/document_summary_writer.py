import uuid

from qdrant_client import models

from core.config import settings
from storage.my_qdrant_client import client


def upload_document_summary(summary_payload, dense_vector) -> None:
    point_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{summary_payload['document_id']}:summary",
        )
    )

    point = models.PointStruct(
        id=point_id,
        vector={
            "dense": dense_vector,
        },
        payload=summary_payload,
    )

    client.upsert(
        collection_name=settings.DOCUMENT_SUMMARIES_COLLECTION_NAME,
        points=[point],
    )