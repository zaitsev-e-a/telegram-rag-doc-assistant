from fastembed import TextEmbedding

from core.config import settings


_model = None


def get_dense_model():
    global _model

    if _model is None:
        _model = TextEmbedding(model_name=settings.DENSE_MODEL_NAME)

    return _model


def get_dense_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = get_dense_model()
    vectors = list(model.embed(texts))
    return [vector.tolist() for vector in vectors]