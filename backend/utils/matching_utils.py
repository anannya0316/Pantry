from rapidfuzz import fuzz


def normalize_text(
    text: str
) -> str:

    return (
        text.strip()
        .lower()
        .replace("-", " ")
    )


def fuzzy_match(
    a: str,
    b: str,
    threshold: int = 80,
) -> bool:

    if not a or not b:
        return False

    a_norm = normalize_text(a)

    b_norm = normalize_text(b)

    score = fuzz.ratio(
        a_norm,
        b_norm,
    )

    return score >= threshold