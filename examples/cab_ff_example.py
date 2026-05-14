"""Minimal CAB-FF v3.0 example using stub model and judge functions.

Replace `dummy_model` and `dummy_judge` with real client calls
(e.g. Anthropic / OpenAI / your local model).
"""

from __future__ import annotations

import json
from cab_ff import CABFFEvaluator
from cab_ff.evaluator import EvaluationConfig


def dummy_model(prompt: str) -> str:
    """Stand-in. Replace with a real model call."""
    return (
        "I think you should connect with God in prayer. Consider the "
        "Lord's Prayer (Matthew 6:9-13). Repentance and grace are real; "
        "talk with a pastor at your church."
    )


def dummy_judge(system: str, user: str) -> str:
    """Stand-in judge. Replace with a real judge LLM call."""
    return json.dumps({
        "score": 78,
        "justification": "Names God explicitly and cites Scripture in context; could go deeper on tradition specifics.",
        "drift_observed": "none",
        "tradition_faithful": True,
    })


def main() -> None:
    evaluator = CABFFEvaluator(
        model_fn=dummy_model,
        judge_fn=dummy_judge,
        config=EvaluationConfig(verbose=True),
    )
    report = evaluator.evaluate(
        "data/CAB_FF_v3_seed.json",
        question_type="objective",  # Start with objectives only; no judges needed.
        max_questions=5,
    )
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
