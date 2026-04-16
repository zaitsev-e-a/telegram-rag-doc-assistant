from fastembed import SparseTextEmbedding

from core.config import settings


_model = None


def get_sparse_model():
    global _model

    if _model is None:
        _model = SparseTextEmbedding(model_name=settings.SPARSE_EMBEDDING_MODEL_NAME)

    return _model


def create_sparse_embeddings(texts: list[str]):
    if not texts:
        return []

    model = get_sparse_model()
    return list(model.embed(texts))