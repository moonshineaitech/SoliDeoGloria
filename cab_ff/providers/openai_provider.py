"""OpenAI adapter."""

from __future__ import annotations

import os
from typing import Callable, Optional

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - only at import time
    raise ImportError(
        "openai package not installed. Run: pip install openai"
    ) from exc


def _client(api_key: Optional[str] = None) -> "OpenAI":
    return OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))


def openai_model(
    model: str = "gpt-4o",
    *,
    api_key: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    system: Optional[str] = None,
) -> Callable[[str], str]:
    """Return a model_fn that calls OpenAI's Chat Completions API."""
    client = _client(api_key)

    def fn(prompt: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    return fn


def openai_judge(
    model: str = "gpt-4o",
    *,
    api_key: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Callable[[str, str], str]:
    """Return a judge_fn that calls OpenAI's Chat Completions API."""
    client = _client(api_key)

    def fn(system: str, user: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    return fn
