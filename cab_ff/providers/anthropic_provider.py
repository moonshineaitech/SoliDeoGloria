"""Anthropic Claude adapter."""

from __future__ import annotations

import os
from typing import Callable, Optional

try:
    import anthropic
except ImportError as exc:  # pragma: no cover - only at import time
    raise ImportError(
        "anthropic package not installed. Run: pip install anthropic"
    ) from exc


def _client(api_key: Optional[str] = None) -> "anthropic.Anthropic":
    return anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))


def anthropic_model(
    model: str = "claude-sonnet-4-6",
    *,
    api_key: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    system: Optional[str] = None,
) -> Callable[[str], str]:
    """Return a model_fn that calls Anthropic's Messages API."""
    client = _client(api_key)

    def fn(prompt: str) -> str:
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        # Concatenate any text blocks the model returned.
        return "".join(b.text for b in resp.content if hasattr(b, "text"))

    return fn


def anthropic_judge(
    model: str = "claude-opus-4-7",
    *,
    api_key: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Callable[[str, str], str]:
    """Return a judge_fn that calls Anthropic's Messages API.

    CAB-FF prompts judges with a system + user pair. We pass system to
    Anthropic's `system` parameter and the user content as the single
    user message.
    """
    client = _client(api_key)

    def fn(system: str, user: str) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if hasattr(b, "text"))

    return fn
