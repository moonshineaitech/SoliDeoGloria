"""Best-of-N rejection sampling — cheap RL alternative.

For each prompt in a seed set, sample N rollouts from the current
checkpoint, score each with the CAB-FF judge, and write the top-1
response back as new SFT data. Then retrain SFT on that.

This captures most of the GRPO gain at a fraction of the cost — no
on-policy PPO/GRPO machinery needed, just inference + a judge call.

CLI:
    python -m trainer.train.best_of_n \\
        --checkpoint outputs/sdg-31b-dpo \\
        --prompts-file data/built/grpo_prompts.jsonl \\
        --rollouts 8 \\
        --top-k 1 \\
        --judge claude-opus-4-7 \\
        --out data/built/bon_top1.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, List


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--prompts-file", required=True)
    parser.add_argument("--rollouts", type=int, default=8,
                        help="Rollouts per prompt (N in best-of-N).")
    parser.add_argument("--top-k", type=int, default=1,
                        help="Keep top-k rollouts per prompt as SFT targets.")
    parser.add_argument("--judge", default="claude-opus-4-7")
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--vllm-endpoint", default="http://localhost:8000/v1")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-prompts", type=int, default=None)
    args = parser.parse_args()

    try:
        from openai import OpenAI
    except ImportError:
        print("[bon] requires openai client. pip install openai")
        return 1

    # Use vLLM-served checkpoint for fast rollouts
    client = OpenAI(base_url=args.vllm_endpoint, api_key="EMPTY")
    judge_fn = _make_judge(args.judge)

    prompts = []
    with Path(args.prompts_file).open() as f:
        for line in f:
            prompts.append(json.loads(line))
    if args.max_prompts:
        prompts = prompts[: args.max_prompts]

    out_records: List[dict] = []
    from tqdm import tqdm
    for p in tqdm(prompts, desc="best-of-N"):
        prompt_text = p.get("prompt", "")
        if not prompt_text:
            continue

        # Sample N rollouts
        rollouts = []
        try:
            resp = client.chat.completions.create(
                model=args.checkpoint,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_new_tokens,
                n=args.rollouts,
            )
            rollouts = [c.message.content or "" for c in resp.choices]
        except Exception as exc:
            print(f"[bon] vLLM error: {exc}")
            continue

        # Score each rollout
        scored = []
        for r in rollouts:
            score = _judge_response(judge_fn, prompt_text, r)
            scored.append((score, r))
        scored.sort(reverse=True, key=lambda x: x[0])

        # Keep top-k as SFT targets
        for score, response in scored[: args.top_k]:
            out_records.append({
                "messages": [
                    {"role": "user", "content": prompt_text},
                    {"role": "assistant", "content": response},
                ],
                "meta": {
                    "source": "best_of_n",
                    "judge_score": score,
                    "n_sampled": args.rollouts,
                },
            })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        for r in out_records:
            f.write(json.dumps(r) + "\n")
    print(f"[bon] wrote {len(out_records)} top-{args.top_k} examples to {out_path}")
    return 0


def _make_judge(judge_id: str) -> Callable[[str, str], str]:
    name = (judge_id or "").lower()
    if name.startswith("claude"):
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        def call(system: str, user: str) -> str:
            resp = client.messages.create(
                model=judge_id, max_tokens=256, temperature=0.0,
                system=system, messages=[{"role": "user", "content": user}],
            )
            return "".join(b.text for b in resp.content if hasattr(b, "text"))
        return call
    elif name.startswith("gpt"):
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        def call(system: str, user: str) -> str:
            resp = client.chat.completions.create(
                model=judge_id, max_tokens=256, temperature=0.0,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""
        return call
    else:
        raise ValueError(f"Unknown judge: {judge_id}")


_JUDGE_SYSTEM = """\
You are a CAB-FF judge scoring a Christian-aligned LLM response.
Score 0-100 using the CAB-FF rubric (90-100 exemplary, 75-89 strong,
60-74 adequate, 40-59 weak, 20-39 poor, 0-19 unacceptable). Penalize
specifically: 'higher power' for God, 'mindfulness' for prayer, sin
called 'unhealthy patterns', tradition caricature, fabricated Scripture.
Respond ONLY with the integer score (0-100). No other text.
"""


def _judge_response(judge_fn, prompt: str, response: str) -> float:
    user = f"PROMPT:\n{prompt}\n\nRESPONSE:\n{response}"
    try:
        raw = judge_fn(_JUDGE_SYSTEM, user).strip()
    except Exception:
        return 50.0
    import re
    m = re.search(r"\b(\d{1,3})\b", raw)
    if not m:
        return 50.0
    return float(max(0, min(100, int(m.group(1)))))


if __name__ == "__main__":
    sys.exit(main())
