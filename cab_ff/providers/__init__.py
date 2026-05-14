"""Model and judge provider adapters.

Saves CAB-FF users from having to write `model_fn` / `judge_fn` boilerplate
for every backend. Each adapter returns the two callables the evaluator
expects:

    model_fn(prompt: str) -> str
    judge_fn(system: str, user: str) -> str

Usage:

    from cab_ff.providers import anthropic_model, anthropic_judge

    model_fn = anthropic_model("claude-sonnet-4-6")
    judge_fn = anthropic_judge("claude-opus-4-7")

    evaluator = CABFFEvaluator(model_fn=model_fn, judge_fn=judge_fn)
"""

from .base import MockModel, MockJudge, fixed_response, deterministic_judge

try:
    from .anthropic_provider import anthropic_model, anthropic_judge
except ImportError:  # anthropic SDK not installed
    anthropic_model = anthropic_judge = None  # type: ignore

try:
    from .openai_provider import openai_model, openai_judge
except ImportError:  # openai SDK not installed
    openai_model = openai_judge = None  # type: ignore

try:
    from .litellm_provider import litellm_model, litellm_judge
except ImportError:  # litellm not installed
    litellm_model = litellm_judge = None  # type: ignore


__all__ = [
    # Mocks (no install required)
    "MockModel",
    "MockJudge",
    "fixed_response",
    "deterministic_judge",
    # Anthropic
    "anthropic_model",
    "anthropic_judge",
    # OpenAI
    "openai_model",
    "openai_judge",
    # LiteLLM (multi-provider routing)
    "litellm_model",
    "litellm_judge",
]
