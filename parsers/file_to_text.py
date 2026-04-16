from pathlib import Path

import magic

from core.config import settings
from parsers.doc_to_text import doc_to_text
from parsers.docx_to_text import docx_to_text
from parsers.normalize import normalize_text
from parsers.pdf_to_text import pdf_to_text
from parsers.txt_to_text import txt_to_text


def detect_file_type(file_path):
    path = Path(file_path)

    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        return False

    mime_type = magic.from_file(str(path), mime=True)

    if mime_type not in settings.MIME_TYPE_MAPPING:
        return False

    return settings.MIME_TYPE_MAPPING[mime_type]


def file_to_text(file_path):
    file_type = detect_file_type(file_path)

    if file_type == "pdf":
        return pdf_to_text(file_path)
    if file_type == "docx":
        return docx_to_text(file_path)
    if file_type == "doc":
        return doc_to_text(file_path)
    if file_type == "txt":
        return txt_to_text(file_path)

    return False


def file_to_clean_text(file_path):
    text = file_to_text(file_path)
    if not text:
        return "", ""

    file_type = detect_file_type(file_path)
    clean_text = normalize_text(text)

    return clean_text, file_type