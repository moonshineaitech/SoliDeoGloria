"""CAB-FF quickstart.

Runs a smoke evaluation against a model + judge. By default uses the
built-in MockModel and MockJudge so you can verify your install in under
5 seconds without any API key.

Examples:

    # Smoke test (no API keys needed)
    python examples/quickstart.py

    # 20 objective + 5 subjective questions against Claude
    python examples/quickstart.py --provider anthropic \\
        --model claude-sonnet-4-6 --judge claude-opus-4-7 \\
        --objective 20 --subjective 5

    # OpenAI
    python examples/quickstart.py --provider openai \\
        --model gpt-4o --judge gpt-4o

    # Any LiteLLM-supported provider
    python examples/quickstart.py --provider litellm \\
        --model openrouter/anthropic/claude-3.5-sonnet \\
        --judge openrouter/anthropic/claude-3.5-sonnet

    # Local Ollama
    python examples/quickstart.py --provider litellm \\
        --model ollama/llama3 --judge ollama/llama3

Pass `--full` to evaluate the whole dataset (slow and uses many tokens).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cab_ff import CABFFEvaluator  # noqa: E402
from cab_ff.evaluator import EvaluationConfig  # noqa: E402
from cab_ff.loader import filter_questions, load_dataset  # noqa: E402
from cab_ff.providers import (  # noqa: E402
    MockJudge,
    MockModel,
)


DATASET_PATH = ROOT / "data" / "CAB_FF_v3_dataset.json"


def _build_provider(args) -> tuple:
    if args.provider == "mock":
        return MockModel(seed=args.seed, drift=args.simulate_drift), MockJudge()
    if args.provider == "anthropic":
        from cab_ff.providers import anthropic_judge, anthropic_model
        return anthropic_model(args.model), anthropic_judge(args.judge or args.model)
    if args.provider == "openai":
        from cab_ff.providers import openai_judge, openai_model
        return openai_model(args.model), openai_judge(args.judge or args.model)
    if args.provider == "litellm":
        from cab_ff.providers import litellm_judge, litellm_model
        return litellm_model(args.model), litellm_judge(args.judge or args.model)
    raise SystemExit(f"Unknown provider: {args.provider}")


def _select_sample(questions, args):
    """Return a deterministic sample respecting the CLI shaping flags."""
    rng = random.Random(args.seed)

    if args.full:
        return questions

    chosen = []
    by_type = {t: filter_questions(questions, question_type=t) for t in [
        "objective", "subjective", "adversarial", "multi_turn", "comparative",
    ]}

    take = {
        "objective": args.objective,
        "subjective": args.subjective,
        "adversarial": args.adversarial,
        "multi_turn": args.multi_turn,
        "comparative": args.comparative,
    }
    for qtype, n in take.items():
        pool = by_type[qtype]
        if n >= len(pool):
            chosen.extend(pool)
        else:
            chosen.extend(rng.sample(pool, n))
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", default="mock", choices=["mock", "anthropic", "openai", "litellm"])
    parser.add_argument("--model", default="", help="Model identifier (provider-specific). Required for non-mock.")
    parser.add_argument("--judge", default="", help="Judge model identifier (defaults to --model).")
    parser.add_argument("--objective", type=int, default=10)
    parser.add_argument("--subjective", type=int, default=0)
    parser.add_argument("--adversarial", type=int, default=0)
    parser.add_argument("--multi-turn", dest="multi_turn", type=int, default=0)
    parser.add_argument("--comparative", type=int, default=0)
    parser.add_argument("--full", action="store_true", help="Run the whole dataset (slow).")
    parser.add_argument("--dataset", default=str(DATASET_PATH))
    parser.add_argument("--output", default="quickstart_results.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--simulate-drift", action="store_true",
                        help="Mock model only: deliberately respond with secular-drift language to verify drift probes fire.")
    parser.add_argument("--no-indicators", action="store_true",
                        help="Skip the 40-binary alignment-indicator pass (faster, fewer judge calls).")
    args = parser.parse_args()

    if args.provider != "mock" and not args.model:
        parser.error("--model is required when --provider is not 'mock'")

    print(f"[quickstart] provider={args.provider} model={args.model or '(mock)'} dataset={args.dataset}")
    model_fn, judge_fn = _build_provider(args)

    data = load_dataset(args.dataset)
    sample = _select_sample(data["questions"], args)
    print(f"[quickstart] evaluating {len(sample)} questions...")

    # Write the sample to a temporary file so the evaluator's filter machinery
    # operates on exactly this subset.
    sample_doc = {**data, "questions": sample, "total_questions": len(sample)}
    sample_path = ROOT / "examples" / ".quickstart_sample.json"
    sample_path.write_text(json.dumps(sample_doc))

    config = EvaluationConfig(
        apply_alignment_indicators=not args.no_indicators,
        verbose=True,
    )
    evaluator = CABFFEvaluator(model_fn=model_fn, judge_fn=judge_fn, config=config)
    report = evaluator.evaluate(str(sample_path), output_path=args.output)

    summary = report["summary"]
    print()
    print("=" * 60)
    print("CAB-FF QUICKSTART SUMMARY")
    print("=" * 60)
    print(f"  CAB-FF Score        {summary['cab_ff_score']:6.2f} / 100")
    print(f"  Flourishing Score   {summary['flourishing_score']:6.2f}")
    print(f"  Faithfulness Index  {summary['faithfulness_index']:6.2f}")
    print(f"  Drift Index         {summary['drift_index']:6.2f}  (lower is better)")
    print(f"  Sycophancy Index    {summary['sycophancy_index']:6.2f}  (lower is better)")
    print()
    print("By dimension:")
    for dim, info in sorted(summary["by_dimension"].items()):
        print(f"  {dim:<40} {info['score']:6.2f}  (n={info['count']})")
    print(f"\nFull report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
