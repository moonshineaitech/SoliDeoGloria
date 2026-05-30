"""Run CAB-FF against a fine-tuned checkpoint.

Bridges the trainer to the CAB-FF Python package by constructing a
`model_fn` and `judge_fn` and invoking `CABFFEvaluator`.

Two backends are supported:
  --backend transformers   : direct HF generate. Slow but no extra deps.
  --backend vllm           : OpenAI-compatible vLLM server (default,
                             recommended). Start vLLM in another shell
                             first: ./trainer/deploy/vllm_serve.sh CKPT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, Optional


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", default=None,
                        help="Path to merged checkpoint dir, or HF Hub repo id.")
    parser.add_argument("--mock", action="store_true",
                        help="Use the CAB-FF MockModel + MockJudge (zero cost, smoke test).")
    parser.add_argument("--dataset", required=True,
                        help="Path to CAB-FF dataset JSON.")
    parser.add_argument("--backend", default="vllm", choices=["vllm", "transformers", "mock"])
    parser.add_argument("--vllm-endpoint", default="http://localhost:8000/v1",
                        help="vLLM OpenAI-compatible endpoint.")
    parser.add_argument("--judge", default="claude-opus-4-7",
                        help="Judge LLM identifier (claude-* or gpt-*).")
    parser.add_argument("--max-questions", type=int, default=None)
    parser.add_argument("--out", default=None,
                        help="Output report JSON path.")
    args = parser.parse_args()

    # The trainer's parent repo IS the CAB-FF repo. Add it to the path.
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from cab_ff import CABFFEvaluator
    from cab_ff.evaluator import EvaluationConfig

    if args.mock or args.backend == "mock":
        from cab_ff.providers import MockModel, MockJudge
        model_fn = MockModel(seed=0)
        judge_fn = MockJudge()
    elif args.backend == "vllm":
        if not args.checkpoint:
            print("[eval] --checkpoint required for --backend vllm "
                  "(used as the served-model identifier).")
            return 1
        model_fn = _make_vllm_model(args.vllm_endpoint, args.checkpoint)
        judge_fn = _make_judge(args.judge)
    elif args.backend == "transformers":
        if not args.checkpoint:
            print("[eval] --checkpoint required for --backend transformers")
            return 1
        model_fn = _make_transformers_model(args.checkpoint)
        judge_fn = _make_judge(args.judge)
    else:
        print(f"[eval] unknown backend: {args.backend}")
        return 1

    evaluator = CABFFEvaluator(
        model_fn=model_fn,
        judge_fn=judge_fn,
        config=EvaluationConfig(verbose=True),
    )
    out_path = args.out or (
        f"{args.checkpoint}/cab_ff_report.json"
        if args.checkpoint and Path(args.checkpoint).is_dir()
        else "cab_ff_report.json"
    )
    report = evaluator.evaluate(
        args.dataset, max_questions=args.max_questions, output_path=out_path,
    )
    summary = report["summary"]
    print("\n" + "=" * 60)
    print(f"CAB-FF report (checkpoint={args.checkpoint or 'mock'})")
    print("=" * 60)
    print(f"  CAB-FF Score        {summary['cab_ff_score']:6.2f}")
    print(f"  Flourishing Score   {summary['flourishing_score']:6.2f}")
    print(f"  Faithfulness Index  {summary['faithfulness_index']:6.2f}")
    print(f"  Drift Index         {summary['drift_index']:6.2f}  (lower better)")
    print(f"  Sycophancy Index    {summary['sycophancy_index']:6.2f}  (lower better)")
    print(f"\n  full report: {out_path}")
    return 0


def _make_vllm_model(endpoint: str, model_id: str) -> Callable[[str], str]:
    """OpenAI-compatible request to a local vLLM serving the checkpoint."""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise ImportError("openai package required for vLLM client. "
                          "Install: pip install openai") from exc
    client = OpenAI(base_url=endpoint, api_key="EMPTY")

    def fn(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.0,
        )
        return resp.choices[0].message.content or ""
    return fn


def _make_transformers_model(checkpoint: str) -> Callable[[str], str]:
    """Direct HF generate. Slow, but no vLLM dependency."""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise ImportError("transformers required. Install: pip install -e '.[gpu]'") from exc
    tok = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint, torch_dtype=torch.bfloat16,
        device_map="auto", trust_remote_code=True,
    )

    def fn(prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        inputs = tok.apply_chat_template(messages, add_generation_prompt=True,
                                          return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(inputs, max_new_tokens=1024,
                                 do_sample=False, temperature=0.0,
                                 pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)
    return fn


def _make_judge(judge_model_id: str) -> Callable[[str, str], str]:
    name = (judge_model_id or "").lower()
    if name.startswith("claude") or "anthropic" in name:
        from cab_ff.providers import anthropic_judge
        if anthropic_judge is None:
            raise ImportError("anthropic SDK required. pip install anthropic")
        return anthropic_judge(judge_model_id)
    if name.startswith("gpt") or "openai" in name:
        from cab_ff.providers import openai_judge
        if openai_judge is None:
            raise ImportError("openai SDK required. pip install openai")
        return openai_judge(judge_model_id)
    raise ValueError(f"Unknown judge: {judge_model_id}")


if __name__ == "__main__":
    sys.exit(main())
