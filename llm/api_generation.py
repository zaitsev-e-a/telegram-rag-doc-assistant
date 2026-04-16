from openai import OpenAI

from core.config import settings


_client = None


def get_api_client() -> OpenAI:
    global _client

    if _client is None:
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY не найден в окружении")
        if not settings.LLM_BASE_URL:
            raise ValueError("LLM_BASE_URL не найден в окружении")
        if not settings.LLM_API_MODEL:
            raise ValueError("LLM_API_MODEL не найден в окружении")

        _client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    return _client


def generate_api_chat_response(messages: list[dict]) -> str:
    client = get_api_client()

    response = client.chat.completions.create(
        model=settings.LLM_API_MODEL,
        messages=messages,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_NEW_TOKENS,
        timeout=settings.LLM_TIMEOUT,
    )

    if not response or not hasattr(response, "choices") or not response.choices:
        raise RuntimeError("API вернул некорректный ответ")

    message = response.choices[0].message
    if not message or not message.content:
        raise RuntimeError("API вернул пустой content")

    return message.content.strip()


def generate_api_text_response(prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты помощник для анализа документов. "
                "Всегда отвечай строго только на русском языке. "
                "Не выдумывай факты. Если делаешь предположения не опираясь на документ, то пиши об этом."
                "Сохраняй структурированный формат ответа, если он требуется в инструкции."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    return generate_api_chat_response(messages)