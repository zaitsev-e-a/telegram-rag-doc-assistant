from llm.generation import generate_text
from llm.summary_prompts import (
    build_chunk_group_facts_prompt,
    build_document_aggregation_prompt,
)
from summarization.summary_parser import (
    parse_chunk_facts_response,
    parse_document_summary_response,
)


def _deduplicate_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []

    for item in items:
        normalized = " ".join(item.split()).strip().lower()
        if not normalized:
            continue

        if normalized not in seen:
            seen.add(normalized)
            result.append(item.strip())

    return result


def _chunk_groups(chunks: list[dict], group_size: int = 5) -> list[list[dict]]:
    return [chunks[i:i + group_size] for i in range(0, len(chunks), group_size)]


def extract_chunk_facts(chunks: list[dict], group_size: int = 5) -> dict:
    all_facts = []
    all_entities = []

    for group in _chunk_groups(chunks, group_size=group_size):
        texts = [chunk["text"] for chunk in group]
        prompt = build_chunk_group_facts_prompt(texts)

        try:
            response = generate_text(prompt)
            parsed = parse_chunk_facts_response(response)

            all_facts.extend(parsed.get("facts", []))
            all_entities.extend(parsed.get("entities", []))

        except Exception as e:
            chunk_ids = [chunk.get("chunk_id") for chunk in group]
            print(f"[WARN] Не удалось извлечь факты из chunk_group={chunk_ids}: {e}")

    all_facts = _deduplicate_preserve_order(all_facts)
    all_entities = _deduplicate_preserve_order(all_entities)

    return {
        "facts": all_facts,
        "entities": all_entities,
    }


def aggregate_document_facts(
    facts: list[str],
    entities: list[str],
    source: str,
) -> dict:
    prompt = build_document_aggregation_prompt(
        facts=facts,
        entities=entities,
        source=source,
    )

    response = generate_text(prompt)
    parsed = parse_document_summary_response(response)

    parsed["facts"] = _deduplicate_preserve_order(parsed.get("facts", []))
    parsed["entities"] = _deduplicate_preserve_order(parsed.get("entities", []))

    return parsed


def summarize_document(chunks: list[dict], source: str) -> dict:
    extracted = extract_chunk_facts(chunks=chunks, group_size=5)

    aggregated = aggregate_document_facts(
        facts=extracted["facts"],
        entities=extracted["entities"],
        source=source,
    )

    if not aggregated.get("facts"):
        aggregated["facts"] = extracted["facts"]

    if not aggregated.get("entities"):
        aggregated["entities"] = extracted["entities"]

    return aggregated