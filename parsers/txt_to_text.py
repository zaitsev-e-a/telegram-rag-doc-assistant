from pathlib import Path


def validate_txt(txt_path):
    path = Path(txt_path)

    try:
        if not path.exists() or not path.is_file() or path.stat().st_size == 0:
            return False
    except Exception:
        return False

    return True


def txt_to_text(txt_path):
    if not validate_txt(txt_path):
        return False

    try:
        for encoding in ("utf-8", "cp1251", "latin-1"):
            try:
                with open(txt_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        return False

    except Exception:
        return False