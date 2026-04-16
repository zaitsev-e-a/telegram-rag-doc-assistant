import textract


def doc_to_text(doc_path):
    try:
        text = textract.process(doc_path).decode('utf-8')
        return text

    except Exception:
        return False