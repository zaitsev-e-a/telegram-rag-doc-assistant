from core.config import settings
from llm.generation import generate_chat_response
from memory.redis_history import (
    get_last_messages,
    save_message_to_redis,
    trim_history,
)
from rag.context_builder import build_rag_context


def build_messages_for_llm(
    user_id: int | str,
    message_text: str,
) -> list[dict]:
    history = get_last_messages(
        user_id=user_id,
        limit=settings.REDIS_HISTORY_LIMIT,
    )

    rag_data = build_rag_context(
        query_text=message_text,
        user_id=user_id,
        chunk_limit=settings.RAG_CHUNK_LIMIT,
        summary_limit=settings.RAG_SUMMARY_LIMIT,
    )

    system_parts = [
        (
            "Ты Telegram-бот для анализа документов. "
            "Всегда отвечай только на русском языке. "
            "Не выдумывай факты. Если делаешь предположения не опираясь на документ, то пиши об этом."
            "Не называй себя Claude, Anthropic, OpenAI, Gemini или другой внешней системой. "
            "Если тебя спрашивают, какая ты модель, отвечай: "
            "'Я AI-ассистент для анализа документов.' "
            "Если пользователь сообщает своё имя, старайся помнить его в рамках текущего диалога. "
            "Если вопрос связан с документами, используй контекст документов. "
            "Если вопрос не связан с документами, отвечай кратко и по существу."
        )
    ]

    if rag_data["knowledge_prefix"]:
        system_parts.append(rag_data["knowledge_prefix"])

    if rag_data["rag_context"]:
        system_parts.append("Контекст из документов:\n" + rag_data["rag_context"])

    messages = [
        {
            "role": "system",
            "content": "\n\n".join(system_parts),
        }
    ]

    for item in history:
        role = item.get("role")
        text = (item.get("text") or "").strip()
        if role in {"user", "assistant"} and text:
            messages.append(
                {
                    "role": role,
                    "content": text,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": message_text.strip(),
        }
    )

    return messages


def process_message(user_id: int | str, message_text: str) -> str:
    user_text = (message_text or "").strip()
    if not user_text:
        return "Пустое сообщение не удалось обработать."

    messages = build_messages_for_llm(
        user_id=user_id,
        message_text=user_text,
    )

    answer = generate_chat_response(messages).strip()
    if not answer:
        answer = "Не удалось сгенерировать ответ."

    save_message_to_redis(user_id=user_id, role="user", text=user_text)
    save_message_to_redis(user_id=user_id, role="assistant", text=answer)
    trim_history(user_id=user_id, keep_last=settings.REDIS_HISTORY_LIMIT)

    return answer