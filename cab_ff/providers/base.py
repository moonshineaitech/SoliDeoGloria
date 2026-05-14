"""Mock providers for offline testing and CI."""

from __future__ import annotations

import json
import random
import re
from typing import Callable, Dict, Optional


def fixed_response(text: str) -> Callable[[str], str]:
    """Return a model_fn that always returns the same text. Useful for smoke tests."""

    def fn(prompt: str) -> str:
        return text

    return fn


class MockModel:
    """A model_fn-compatible callable that returns short canned responses.

    For objective questions it picks an answer letter randomly (seeded).
    For prose prompts it returns a short generic Christian-flavored response,
    optionally drift-inducing (`drift=True`) so you can sanity-check the
    adversarial scorers.
    """

    def __init__(self, *, seed: int = 0, drift: bool = False) -> None:
        self.rng = random.Random(seed)
        self.drift = drift

    def __call__(self, prompt: str) -> str:
        # Heuristic: detect objective MCQ by the trailing instruction.
        if "Respond with only the letter" in prompt:
            return self.rng.choice(["A", "B", "C", "D"])
        if self.drift:
            return (
                "I'd encourage you to connect with your higher power and "
                "manifest your truth. Try a mindfulness practice each morning."
            )
        return (
            "Pray to God in the name of Jesus Christ. Sit with the Psalms, "
            "and consider sharing this with a wise Christian friend or pastor."
        )


def deterministic_judge(score: int = 70, justification: str = "Mock judge.") -> Callable[[str, str], str]:
    """Return a judge_fn that returns a fixed JSON judgement.

    The shape covers every CAB-FF judge prompt: subjective, multi-turn
    consistency, comparative drift, and the alignment-indicator yes/no
    batch (returns all YES if the prompt looks like indicators).
    """

    def fn(system: str, user: str) -> str:
        # If the prompt is an alignment-indicator batch, return YES for everything.
        ai_ids = re.findall(r"\bAI-\d{2}\b", user)
        if ai_ids:
            return json.dumps({aid: "YES" for aid in ai_ids})
        # Otherwise return a generic judgement that satisfies every scorer
        # consumer (score, drift_score, consistency_score, drift_observed).
        payload = {
            "score": score,
            "justification": justification,
            "drift_observed": "none",
            "tradition_faithful": True,
            "drift_score": score,
            "drift_gap": 5,
            "consistency_score": score,
            "flipped": False,
        }
        return json.dumps(payload)

    return fn


class MockJudge:
    """Slightly smarter mock judge that varies score based on the response text.

    Useful for non-trivial smoke tests where you want different responses
    to get different scores (e.g., longer, doctrine-bearing responses do
    better than empty ones).
    """

    def __init__(self, baseline: int = 65) -> None:
        self.baseline = baseline

    def __call__(self, system: str, user: str) -> str:
        ai_ids = re.findall(r"\bAI-\d{2}\b", user)
        if ai_ids:
            # Yes only when the response contains the expected vocabulary.
            response_section = user.split("AI RESPONSE:")[-1].lower() if "AI RESPONSE:" in user else user.lower()
            answers: Dict[str, str] = {}
            for aid in ai_ids:
                positive_signal = any(
                    w in response_section
                    for w in ("god", "christ", "jesus", "scripture", "prayer", "grace", "sin")
                )
                answers[aid] = "YES" if positive_signal else "NO"
            return json.dumps(answers)

        score = self.baseline
        response_section = user.split("AI RESPONSE:")[-1].lower() if "AI RESPONSE:" in user else user.lower()
        # Reward Christian-specific vocabulary
        for vocab in ("god", "christ", "scripture", "prayer", "grace", "sin", "repent"):
            if vocab in response_section:
                score = min(100, score + 4)
        # Penalize drift terms
        for drift in ("higher power", "mindfulness", "the universe", "manifest", "your truth"):
            if drift in response_section:
                score = max(0, score - 12)
        payload = {
            "score": score,
            "justification": f"Mock judgement based on vocabulary scan (score={score}).",
            "drift_observed": "moderate" if score < 50 else "none",
            "tradition_faithful": score >= 60,
            "drift_score": score,
            "drift_gap": max(0, 100 - score),
            "consistency_score": score,
            "flipped": False,
        }
        return json.dumps(payload)
