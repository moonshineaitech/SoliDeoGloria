"""LiteLLM adapter — one interface, ~100 providers (OpenAI, Anthropic,
Google, Mistral, Cohere, Together, Groq, OpenRouter, local Ollama, etc.).

Lets users say `litellm_model("openrouter/meta-llama/llama-3.1-70b-instruct")`
or `litellm_model("ollama/llama3")` and have it just work.

See: https://docs.litellm.ai/docs/providers
"""

from __future__ import annotations

import os
from typing import Callable, Optional

try:
    import litellm
except ImportError as exc:  # pragma: no cover - only at import time
    raise ImportError(
        "litellm package not installed. Run: pip install litellm"
    ) from exc


def litellm_model(
    model: str,
    *,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    system: Optional[str] = None,
) -> Callable[[str], str]:
    """Return a model_fn routed through LiteLLM."""

    def fn(prompt: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if api_key is not None:
            kwargs["api_key"] = api_key
        if api_base is not None:
            kwargs["api_base"] = api_base
        resp = litellm.completion(**kwargs)
        return resp["choices"][0]["message"]["content"] or ""

    return fn


def litellm_judge(
    model: str,
    *,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Callable[[str, str], str]:
    """Return a judge_fn routed through LiteLLM."""

    def fn(system: str, user: str) -> str:
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if api_key is not None:
            kwargs["api_key"] = api_key
        if api_base is not None:
            kwargs["api_base"] = api_base
        resp = litellm.completion(**kwargs)
        return resp["choices"][0]["message"]["content"] or ""

    return fn
