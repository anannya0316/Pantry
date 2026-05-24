import os

import requests as http_requests
from openai import OpenAI

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"


def _get_config():
    return _OPENROUTER_BASE_URL, os.getenv("OPEN_ROUTER_KEY"), _OPENROUTER_MODEL


def get_api_key() -> str | None:
    _, key, _ = _get_config()
    return key


def get_openai_client() -> OpenAI:
    base_url, api_key, _ = _get_config()
    return OpenAI(base_url=base_url, api_key=api_key)


def get_model() -> str:
    _, _, model = _get_config()
    return model


def call_llm(
    prompt: str,
    temperature: float = 0,
    timeout: int = 15,
    max_tokens: int = 1500,
) -> str:
    base_url, api_key, model = _get_config()

    if not api_key:
        raise ValueError("No LLM API key configured")

    response = http_requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LLM error {response.status_code}: {response.text}"
        )

    return response.json()["choices"][0]["message"]["content"].strip()
