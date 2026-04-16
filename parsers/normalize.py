import re


def merge_lines(prev_line: str, next_line: str) -> str:
    if not prev_line:
        return next_line
    if not next_line:
        return prev_line

    prev_line = prev_line.rstrip()
    next_line = next_line.lstrip()

    if prev_line.endswith("-"):
        return prev_line[:-1] + next_line

    return prev_line + " " + next_line


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    text = re.sub(r"[ \t]+", " ", text)

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "\u00A0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    lines = [line.strip() for line in text.split("\n")]

    fixed_lines = []
    buffer = ""

    for line in lines:
        if not line:
            if buffer:
                fixed_lines.append(buffer)
                buffer = ""
            fixed_lines.append("")
            continue

        if buffer:
            buffer = merge_lines(buffer, line)
        else:
            buffer = line

    if buffer:
        fixed_lines.append(buffer)

    text = "\n".join(fixed_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()