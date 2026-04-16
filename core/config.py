import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    MIME_TYPE_MAPPING = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.ms-word": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
    }

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    MEDIA_GROUP_DEBOUNCE_SECONDS = 1.5

    TMP_DIR = Path(os.getenv("TMP_DIR", "./data/tmp"))

    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

    DOCUMENTS_COLLECTION_NAME = os.getenv(
        "DOCUMENTS_COLLECTION_NAME",
        "documents_collection",
    )
    DOCUMENT_SUMMARIES_COLLECTION_NAME = os.getenv(
        "DOCUMENT_SUMMARIES_COLLECTION_NAME",
        "document_summaries",
    )

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "220"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "40"))

    PDF_DPI = int(os.getenv("PDF_DPI", "300"))
    PDF_LANG = os.getenv("PDF_LANG", "rus+eng")

    REDIS_HISTORY_LIMIT = int(os.getenv("REDIS_HISTORY_LIMIT", "10"))
    RAG_CHUNK_LIMIT = int(os.getenv("RAG_CHUNK_LIMIT", "5"))
    RAG_SUMMARY_LIMIT = int(os.getenv("RAG_SUMMARY_LIMIT", "3"))

    ENABLE_DOCUMENT_SUMMARIZATION = (
        os.getenv("ENABLE_DOCUMENT_SUMMARIZATION", "true").lower() == "true"
    )

    DENSE_MODEL_NAME = os.getenv(
        "DENSE_MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    DENSE_VECTOR_SIZE = int(os.getenv("DENSE_VECTOR_SIZE", "384"))

    SPARSE_EMBEDDING_MODEL_NAME = os.getenv(
        "SPARSE_EMBEDDING_MODEL_NAME",
        "Qdrant/bm25",
    )

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_API_MODEL = os.getenv("LLM_API_MODEL", "")

    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

    LLM_MODEL_NAME = os.getenv(
        "LLM_MODEL_NAME",
        "Qwen/Qwen3-8B",
    )
    LLM_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "200"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    RERANKER_MODEL_NAME = os.getenv(
        "RERANKER_MODEL_NAME",
        "jinaai/jina-reranker-v2-base-multilingual",
    )

    RERANK_ENABLED = os.getenv("RERANK_ENABLED", "true").lower() == "true"
    RERANK_CANDIDATES = int(os.getenv("RERANK_CANDIDATES", "20"))
    RERANK_LIMIT = int(os.getenv("RERANK_LIMIT", "5"))


settings = Settings()
settings.TMP_DIR.mkdir(parents=True, exist_ok=True)