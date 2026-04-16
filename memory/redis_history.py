import json

from memory.redis_client import redis_client


def _history_key(user_id: int | str) -> str:
    return f"chat:{user_id}:history"


def save_message_to_redis(user_id: int | str, role: str, text: str) -> None:
    item = {
        "role": role,
        "text": text,
    }

    redis_client.rpush(_history_key(user_id), json.dumps(item, ensure_ascii=False))


def get_last_messages(user_id: int | str, limit: int = 10) -> list[dict]:
    raw_items = redis_client.lrange(_history_key(user_id), -limit, -1)

    result = []
    for raw in raw_items:
        try:
            result.append(json.loads(raw))
        except Exception:
            continue

    return result


def trim_history(user_id: int | str, keep_last: int) -> None:
    redis_client.ltrim(_history_key(user_id), -keep_last, -1)


def clear_user_history(user_id: int | str) -> None:
    redis_client.delete(_history_key(user_id))