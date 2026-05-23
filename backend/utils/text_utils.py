import re


def clean_markdown(text: str) -> str:
    """Strip markdown formatting from LLM output before sending to the UI."""
    if not text:
        return text

    # Code blocks (``` ... ```)
    text = re.sub(r"```[^\n]*\n?(.*?)```", r"\1", text, flags=re.DOTALL)

    # Inline code (`code`)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Bold+italic (***text*** or ___text___)
    text = re.sub(r"\*{3}(.+?)\*{3}", r"\1", text)
    text = re.sub(r"_{3}(.+?)_{3}", r"\1", text)

    # Bold (**text** or __text__)
    text = re.sub(r"\*{2}(.+?)\*{2}", r"\1", text)
    text = re.sub(r"_{2}(.+?)_{2}", r"\1", text)

    # Italic (*text* or _text_)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Headers (# H1, ## H2, etc.)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Horizontal rules (--- or ***)
    text = re.sub(r"^[-*]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Collapse 3+ blank lines down to two
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
