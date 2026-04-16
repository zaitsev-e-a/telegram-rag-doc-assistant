from qdrant_client import models
from qdrant_client.http.exceptions import UnexpectedResponse

from chunking_and_embedding.dense import get_dense_embeddings
from chunking_and_embedding.sparse import create_sparse_embeddings
from chunking_and_embedding.reranker import rerank_documents
from core.config import settings
from storage.my_qdrant_client import client


def _user_filter(user_id: int | str) -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=str(user_id)),
            )
        ]
    )


def _collection_exists(collection_name: str) -> bool:
    try:
        collections = client.get_collections().collections
        names = [collection.name for collection in collections]
        return collection_name in names
    except Exception:
        return False


def hybrid_search_documents(
    query_text: str,
    user_id: int | str,
    limit: int = 5,
) -> list[dict]:
    if not query_text.strip():
        return []

    if not _collection_exists(settings.DOCUMENTS_COLLECTION_NAME):
        return []

    dense_vector = get_dense_embeddings([query_text])[0]
    sparse_vector = create_sparse_embeddings([query_text])[0]

    retrieval_limit = (
        max(limit * 3, settings.RERANK_CANDIDATES)
        if settings.RERANK_ENABLED
        else limit
    )

    try:
        response = client.query_points(
            collection_name=settings.DOCUMENTS_COLLECTION_NAME,
            prefetch=[
                models.Prefetch(
                    query=dense_vector,
                    using="dense",
                    filter=_user_filter(user_id),
                    limit=retrieval_limit,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_vector.indices,
                        values=sparse_vector.values,
                    ),
                    using="sparse",
                    filter=_user_filter(user_id),
                    limit=retrieval_limit,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            with_payload=True,
            limit=retrieval_limit,
        )
    except UnexpectedResponse:
        return []

    points = getattr(response, "points", response)
    results = []

    for point in points:
        payload = point.payload or {}
        results.append(
            {
                "id": str(point.id),
                "score": float(point.score) if point.score is not None else 0.0,
                "text": payload.get("text", ""),
                "source": payload.get("source", ""),
                "file_type": payload.get("file_type", ""),
                "document_id": payload.get("document_id", ""),
                "chunk_id": payload.get("chunk_id", -1),
            }
        )

    if settings.RERANK_ENABLED and results:
        results = rerank_documents(
            query=query_text,
            documents=results,
            top_k=limit,
        )
    else:
        results = results[:limit]

    return results


def search_document_summaries(
    query_text: str,
    user_id: int | str,
    limit: int = 3,
) -> list[dict]:
    if not query_text.strip():
        return []

    if not _collection_exists(settings.DOCUMENT_SUMMARIES_COLLECTION_NAME):
        return []

    dense_vector = get_dense_embeddings([query_text])[0]

    try:
        response = client.query_points(
            collection_name=settings.DOCUMENT_SUMMARIES_COLLECTION_NAME,
            query=dense_vector,
            using="dense",
            query_filter=_user_filter(user_id),
            with_payload=True,
            limit=limit,
        )
    except UnexpectedResponse:
        return []

    points = getattr(response, "points", response)
    results = []

    for point in points:
        payload = point.payload or {}
        results.append(
            {
                "id": str(point.id),
                "score": float(point.score) if point.score is not None else 0.0,
                "summary": payload.get("summary", ""),
                "facts": payload.get("facts", []),
                "entities": payload.get("entities", []),
                "source": payload.get("source", ""),
                "file_type": payload.get("file_type", ""),
                "document_id": payload.get("document_id", ""),
                "document_type": payload.get("document_type", ""),
            }
        )

    return results


def search_all_knowledge(
    query_text: str,
    user_id: int | str,
    chunk_limit: int = 5,
    summary_limit: int = 3,
) -> dict:
    return {
        "summaries": search_document_summaries(
            query_text=query_text,
            user_id=user_id,
            limit=summary_limit,
        ),
        "chunks": hybrid_search_documents(
            query_text=query_text,
            user_id=user_id,
            limit=chunk_limit,
        ),
    }


def delete_user_knowledge(user_id: int | str) -> None:
    user_filter = _user_filter(user_id)

    if _collection_exists(settings.DOCUMENTS_COLLECTION_NAME):
        try:
            client.delete(
                collection_name=settings.DOCUMENTS_COLLECTION_NAME,
                points_selector=models.FilterSelector(filter=user_filter),
            )
        except UnexpectedResponse:
            pass

    if _collection_exists(settings.DOCUMENT_SUMMARIES_COLLECTION_NAME):
        try:
            client.delete(
                collection_name=settings.DOCUMENT_SUMMARIES_COLLECTION_NAME,
                points_selector=models.FilterSelector(filter=user_filter),
            )
        except UnexpectedResponse:
            pass