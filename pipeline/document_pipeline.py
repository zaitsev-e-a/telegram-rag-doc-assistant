import uuid

from chunking_and_embedding.chunking import chunk_text_with_metadata
from chunking_and_embedding.dense import get_dense_embeddings
from chunking_and_embedding.sparse import create_sparse_embeddings
from core.config import settings
from parsers.file_to_text import file_to_clean_text
from storage.document_summary_collection import create_document_summary_collection
from storage.document_summary_writer import upload_document_summary
from storage.qdrant_collection import create_qdrant_collection
from storage.qdrant_writer import upload_points
from summarization.document_knowledge_extractor import summarize_document
from summarization.summary_payload_builder import build_summary_payload


def process_document(file_path: str, user_id: int | str, source: str) -> dict:
    text, file_type = file_to_clean_text(file_path)

    if not text:
        return {
            "success": False,
            "message": "Не удалось извлечь текст из файла.",
        }

    document_id = str(uuid.uuid4())

    chunks = chunk_text_with_metadata(
        text=text,
        source=source,
        file_type=file_type,
        user_id=str(user_id),
        document_id=document_id,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    if not chunks:
        return {
            "success": False,
            "message": "Не удалось разбить документ на чанки.",
        }

    chunk_texts = [chunk["text"] for chunk in chunks]

    dense_vectors = get_dense_embeddings(chunk_texts)
    sparse_vectors = create_sparse_embeddings(chunk_texts)

    create_qdrant_collection()
    upload_points(
        chunks=chunks,
        dense_vectors=dense_vectors,
        sparse_vectors=sparse_vectors,
    )

    parsed_summary = None

    if settings.ENABLE_DOCUMENT_SUMMARIZATION:
        try:
            parsed_summary = summarize_document(chunks=chunks, source=source)

            summary_payload = build_summary_payload(
                user_id=user_id,
                document_id=document_id,
                source=source,
                file_type=file_type,
                parsed_summary=parsed_summary,
                chunk_count=len(chunks),
            )

            summary_text = summary_payload["summary"].strip() or source
            summary_vector = get_dense_embeddings([summary_text])[0]

            create_document_summary_collection()
            upload_document_summary(summary_payload, summary_vector)

        except Exception as e:
            print(f"[WARN] Суммаризация не удалась для {source}: {e}")

    return {
        "success": True,
        "message": "Файл обработан и загружен в базу знаний.",
        "document_id": document_id,
        "file_type": file_type,
        "chunks_count": len(chunks),
        "summary_created": parsed_summary is not None,
    }