import re


def estimate_tokens(text: str) -> int:
    words = re.findall(
        r"[A-Za-zА-Яа-яЁё0-9]+(?:-[A-Za-zА-Яа-яЁё0-9]+)*",
        text,
        flags=re.UNICODE,
    )

    if not words:
        return 0

    ru_count = sum(1 for w in words if re.search(r"[А-Яа-яЁё]", w))
    en_count = len(words) - ru_count

    ru_tokens = ru_count * 1.6
    en_tokens = en_count * 1.3

    return max(1, int(ru_tokens + en_tokens))


def split_into_paragraphs(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = re.split(r"\n{2,}", text)
    return [p.strip() for p in paragraphs if p.strip()]


def split_into_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?…])\s+(?=[A-ZА-ЯЁ0-9\"«])", text)
    return [s.strip() for s in sentences if s.strip()]


def split_long_sentence(sentence: str, max_tokens: int) -> list[str]:
    words = sentence.split()
    if not words:
        return []

    parts = []
    current_words = []

    for word in words:
        candidate = " ".join(current_words + [word]).strip()

        if current_words and estimate_tokens(candidate) > max_tokens:
            parts.append(" ".join(current_words).strip())
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        parts.append(" ".join(current_words).strip())

    return parts


def build_overlap(sentences: list[str], max_overlap_tokens: int) -> list[str]:
    overlap_sentences = []
    total_tokens = 0

    for sentence in reversed(sentences):
        sent_tokens = estimate_tokens(sentence)

        if overlap_sentences and total_tokens + sent_tokens > max_overlap_tokens:
            break

        overlap_sentences.insert(0, sentence)
        total_tokens += sent_tokens

    return overlap_sentences


def chunk_text(text: str,
    chunk_size: int = 220,
    chunk_overlap: int = 40,
) -> list[str]:
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        return []

    chunks = []
    current_sentences = []
    current_tokens = 0

    for paragraph in paragraphs:
        sentences = split_into_sentences(paragraph)
        if not sentences:
            continue

        for sentence in sentences:
            sent_tokens = estimate_tokens(sentence)

            if sent_tokens > chunk_size:
                sentence_parts = split_long_sentence(sentence, chunk_size)
            else:
                sentence_parts = [sentence]

            for part in sentence_parts:
                part_tokens = estimate_tokens(part)

                if current_sentences and (current_tokens + part_tokens > chunk_size):
                    chunk = " ".join(current_sentences).strip()
                    if chunk:
                        chunks.append(chunk)

                    overlap_sentences = build_overlap(current_sentences, chunk_overlap)
                    current_sentences = overlap_sentences.copy()
                    current_tokens = sum(
                        estimate_tokens(sentence) for sentence in current_sentences
                    )

                current_sentences.append(part)
                current_tokens += part_tokens

    if current_sentences:
        chunk = " ".join(current_sentences).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def chunk_text_with_metadata(
    text: str,
    source: str,
    file_type: str,
    user_id: int | str,
    document_id: str,
    chunk_size: int = 220,
    chunk_overlap: int = 40,
) -> list[dict]:
    raw_chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    result = []
    for i, chunk in enumerate(raw_chunks):
        result.append(
            {
                "chunk_id": i,
                "text": chunk,
                "source": source,
                "file_type": file_type,
                "user_id": str(user_id),
                "document_id": document_id,
            }
        )

    return result