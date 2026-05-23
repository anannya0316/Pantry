from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(
    relative_path: str
) -> str:

    prompt_path = (
        PROMPTS_DIR / relative_path
    )

    if not prompt_path.exists():

        raise FileNotFoundError(
            f"Prompt not found: "
            f"{prompt_path}"
        )

    return prompt_path.read_text(
        encoding="utf-8"
    )