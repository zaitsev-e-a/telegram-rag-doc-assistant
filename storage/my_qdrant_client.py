from qdrant_client import QdrantClient

from core.config import settings


client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
)


def check_qdrant_connection():
    try:
        collections = client.get_collections()
        print(f"Подключение к Qdrant успешно! Коллекции: {collections.collections}")
    except Exception as e:
        print(f"Ошибка при подключении к Qdrant: {e}")