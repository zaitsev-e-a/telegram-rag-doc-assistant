import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from core.config import settings
from llm.api_generation import (
    generate_api_chat_response,
    generate_api_text_response,
)


_tokenizer = None
_model = None


def get_model_and_tokenizer():
    global _tokenizer, _model

    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL_NAME)

    if _model is None:
        _model = AutoModelForCausalLM.from_pretrained(
            settings.LLM_MODEL_NAME,
            torch_dtype=torch.float32,
        )

    return _model, _tokenizer


def _generate_local_chat_response(messages: list[dict]) -> str:
    model, tokenizer = get_model_and_tokenizer()

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(text, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=settings.LLM_MAX_NEW_TOKENS,
        do_sample=False,
        temperature=0.1,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id,
    )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    answer = tokenizer.decode(generated, skip_special_tokens=True).strip()

    return answer


def generate_chat_response(messages: list[dict]) -> str:
    if settings.LLM_PROVIDER == "api":
        try:
            return generate_api_chat_response(messages)
        except Exception as e:
            print("[WARN] API не работает, fallback на локальную модель:", e)

    return _generate_local_chat_response(messages)


def generate_text(prompt: str) -> str:
    if settings.LLM_PROVIDER == "api":
        try:
            return generate_api_text_response(prompt)
        except Exception as e:
            print("[WARN] API не работает, fallback на локальную модель:", e)

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

    return _generate_local_chat_response(messages)