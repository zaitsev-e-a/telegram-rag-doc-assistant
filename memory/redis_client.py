import redis

from core.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
)


def check_redis_connection():
    try:
        if redis_client.ping():
            print("Подключение к Redis успешно!")
        else:
            print("Не удалось подключиться к Redis.")
    except Exception as e:
        print(f"Ошибка при подключении к Redis: {e}")