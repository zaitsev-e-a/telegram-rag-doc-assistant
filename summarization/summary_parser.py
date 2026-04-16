import re


def _extract_section(text: str, section_name: str, next_sections: list[str]) -> str:
    if next_sections:
        next_pattern = "|".join(re.escape(name) for name in next_sections)
        pattern = rf"{re.escape(section_name)}:\s*(.*?)(?=\n(?:{next_pattern}):|\Z)"
    else:
        pattern = rf"{re.escape(section_name)}:\s*(.*)$"

    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""

    return match.group(1).strip()


def _split_bullets(section_text: str) -> list[str]:
    if not section_text:
        return []

    items = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"^[-•*\d\.\)\s]+", "", line).strip()
        if line:
            items.append(line)

    return items


def _normalize_text(text: str) -> str:
    return (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("**", "")
        .replace("##", "")
        .strip()
    )


def parse_chunk_facts_response(response: str) -> dict:
    if not response:
        return {
            "facts": [],
            "entities": [],
        }

    text = _normalize_text(response)

    facts_text = _extract_section(
        text,
        "FACTS",
        ["ENTITIES"],
    )

    entities_text = _extract_section(
        text,
        "ENTITIES",
        [],
    )

    return {
        "facts": _split_bullets(facts_text),
        "entities": _split_bullets(entities_text),
    }


def parse_document_summary_response(response: str) -> dict:
    if not response:
        return {
            "summary": "",
            "facts": [],
            "entities": [],
            "document_type": "",
        }

    text = _normalize_text(response)

    summary_text = _extract_section(
        text,
        "SUMMARY",
        ["FACTS", "ENTITIES", "DOCUMENT_TYPE"],
    )

    facts_text = _extract_section(
        text,
        "FACTS",
        ["ENTITIES", "DOCUMENT_TYPE"],
    )

    entities_text = _extract_section(
        text,
        "ENTITIES",
        ["DOCUMENT_TYPE"],
    )

    document_type_text = _extract_section(
        text,
        "DOCUMENT_TYPE",
        [],
    )

    summary = " ".join(
        line.strip() for line in summary_text.splitlines() if line.strip()
    )
    facts = _split_bullets(facts_text)
    entities = _split_bullets(entities_text)

    document_type = ""
    if document_type_text:
        document_type = document_type_text.splitlines()[0].strip()

    return {
        "summary": summary,
        "facts": facts,
        "entities": entities,
        "document_type": document_type,
    }