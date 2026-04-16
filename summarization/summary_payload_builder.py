from datetime import datetime, timezone


def infer_document_type(parsed_summary: dict, source: str) -> str:
    if parsed_summary.get("document_type"):
        return parsed_summary["document_type"]

    summary = parsed_summary.get("summary", "").lower()
    source = source.lower()

    if "устав" in summary or "устав" in source:
        return "устав"
    if "договор" in summary or "договор" in source:
        return "договор"
    if "приказ" in summary or "приказ" in source:
        return "приказ"
    if "положение" in summary or "положение" in source:
        return "положение"
    if "инструкция" in summary or "инструкция" in source:
        return "инструкция"
    if "регламент" in summary or "регламент" in source:
        return "регламент"

    return "неизвестно"


def build_summary_payload(
    user_id,
    document_id,
    source,
    file_type,
    parsed_summary: dict,
    chunk_count: int,
):
    facts = parsed_summary.get("facts", [])
    entities = parsed_summary.get("entities", [])

    return {
        "user_id": str(user_id),
        "document_id": document_id,
        "source": source,
        "file_type": file_type,
        "summary": parsed_summary.get("summary", ""),
        "facts": facts,
        "entities": entities,
        "document_type": infer_document_type(parsed_summary, source),
        "chunk_count": chunk_count,
        "facts_count": len(facts),
        "entities_count": len(entities),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }