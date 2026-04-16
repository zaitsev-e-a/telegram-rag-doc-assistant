from storage.qdrant_search import search_all_knowledge


def _format_summary_block(item: dict) -> str:
    facts = item.get("facts", [])
    entities = item.get("entities", [])

    facts_text = "\n".join(f"- {fact}" for fact in facts[:10]) if facts else "-"
    entities_text = "\n".join(f"- {entity}" for entity in entities[:10]) if entities else "-"

    return "\n".join(
        [
            "[SUMMARY ДОКУМЕНТА]",
            f"Источник: {item.get('source', 'unknown')}",
            f"Тип документа: {item.get('document_type', 'неизвестно')}",
            f"Краткое содержание: {item.get('summary', '')}",
            "Факты:",
            facts_text,
            "Сущности:",
            entities_text,
        ]
    )


def _format_chunk_block(item: dict) -> str:
    return "\n".join(
        [
            "[ФРАГМЕНТ ДОКУМЕНТА]",
            f"Источник: {item.get('source', 'unknown')}",
            f"Chunk ID: {item.get('chunk_id', -1)}",
            item.get("text", ""),
        ]
    )


def build_rag_context(
    query_text: str,
    user_id: int | str,
    chunk_limit: int = 5,
    summary_limit: int = 3,
) -> dict:
    results = search_all_knowledge(
        query_text=query_text,
        user_id=user_id,
        chunk_limit=chunk_limit,
        summary_limit=summary_limit,
    )

    summaries = results["summaries"]
    chunks = results["chunks"]

    sources = []
    seen = set()

    for item in summaries + chunks:
        source = item.get("source", "").strip()
        if source and source not in seen:
            seen.add(source)
            sources.append(source)

    knowledge_prefix = ""
    if sources:
        knowledge_prefix = (
            "Пользователь прикрепил следующие файлы: "
            + ", ".join(sources[:10])
            + "."
        )

    parts = []

    if summaries:
        parts.append("\n\n".join(_format_summary_block(item) for item in summaries))

    if chunks:
        parts.append("\n\n".join(_format_chunk_block(item) for item in chunks))

    return {
        "knowledge_prefix": knowledge_prefix,
        "rag_context": "\n\n".join(parts).strip(),
        "raw_results": results,
    }