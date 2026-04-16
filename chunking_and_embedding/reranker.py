from fastembed.rerank.cross_encoder import TextCrossEncoder

from core.config import settings


_model = None


def get_reranker():
    global _model

    if _model is None:
        _model = TextCrossEncoder(model_name=settings.RERANKER_MODEL_NAME)

    return _model


def rerank_documents(
    query: str,
    documents: list[dict],
    top_k: int | None = None,
) -> list[dict]:
    if not query.strip() or not documents:
        return documents

    reranker = get_reranker()

    doc_texts = [
        (doc.get("text") or "").strip()
        for doc in documents
    ]

    scores = list(reranker.rerank(query, doc_texts))

    rescored = []
    for doc, score in zip(documents, scores):
        item = dict(doc)
        item["rerank_score"] = float(score)
        rescored.append(item)

    rescored.sort(key=lambda x: x["rerank_score"], reverse=True)

    if top_k is not None:
        rescored = rescored[:top_k]

    return rescored