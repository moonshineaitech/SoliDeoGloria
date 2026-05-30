"""Cost estimator — tells you what a run will cost BEFORE you start.

Prices are approximate May 2026 market rates. They move; treat the
output as a planning estimate, not a quote. Override any number with a
flag.

    python -m trainer.scripts.cost_estimate --preset gemma-31b
    python -m trainer.scripts.cost_estimate --preset e4b-cheap
    python -m trainer.scripts.cost_estimate --preset frontier-moe
    python -m trainer.scripts.cost_estimate --gpu-hourly 2.49 --train-hours 6
"""

from __future__ import annotations

import argparse
import sys

# Approximate May 2026 GPU rental rates (USD/hr), cheapest reliable tier.
GPU_RATES = {
    "h100-runpod-community": 2.49,
    "h100-runpod-secure": 3.49,
    "h100-lambda": 2.99,
    "h100-vast": 1.99,          # cheapest, least reliable (spot)
    "h100-modal": 3.95,         # per-second billing
    "a100-80-runpod": 1.49,
    "rtx4090-runpod": 0.44,
    "rtx4090-vast": 0.34,
    "colab-pro-plus": 0.0,      # flat $50/mo; treat compute as "free" here
}

# Teacher LLM data-generation costs (USD per 1k generated examples,
# rough, assumes ~700 input + ~400 output tokens per example).
TEACHER_PER_1K = {
    "claude-opus-4-7": 4.5,
    "claude-sonnet-4-6": 1.2,
    "gpt-4o": 0.9,
    "deepseek-v4-pro-api": 0.4,   # cheap hosted inference
    "gpt-4o-mini": 0.15,
}

# Judge LLM cost per full 1,056-question CAB-FF eval (USD).
JUDGE_PER_EVAL = {
    "claude-opus-4-7": 12.0,
    "claude-sonnet-4-6": 3.5,
    "gpt-4o": 2.8,
    "deepseek-v4-pro-api": 1.2,
}

PRESETS = {
    "e4b-cheap": dict(
        label="Gemma 4 E4B on a single RTX 4090 (weekend-warrior path)",
        gpu="rtx4090-vast", train_hours=4.0, iterate_rounds=1,
        teacher="gpt-4o-mini", judge="gpt-4o", n_examples=15000,
        n_evals=2,
    ),
    "gemma-31b": dict(
        label="Gemma 4 31B on a single H100 (recommended default)",
        gpu="h100-runpod-community", train_hours=7.0, iterate_rounds=3,
        teacher="claude-opus-4-7", judge="claude-opus-4-7", n_examples=50000,
        n_evals=5,
    ),
    "gemma-31b-budget": dict(
        label="Gemma 4 31B on H100, cheaper teacher/judge",
        gpu="h100-vast", train_hours=7.0, iterate_rounds=2,
        teacher="gpt-4o", judge="gpt-4o", n_examples=40000,
        n_evals=3,
    ),
    "frontier-moe": dict(
        label="GLM-5.1 / Kimi K2.6 frontier MoE (8-16x H100 cluster)",
        gpu="h100-runpod-secure", train_hours=12.0, iterate_rounds=1,
        teacher="claude-opus-4-7", judge="claude-opus-4-7", n_examples=60000,
        n_evals=3, gpu_count=12,
    ),
}


def estimate(p: dict) -> dict:
    rate = GPU_RATES[p["gpu"]]
    gpu_count = p.get("gpu_count", 1)
    train_hours = p["train_hours"]
    iterate_rounds = p.get("iterate_rounds", 0)
    # Each iterate round ~= 1.5 hr train + 1 eval
    iterate_hours = iterate_rounds * 1.5
    total_gpu_hours = (train_hours + iterate_hours) * gpu_count

    compute_cost = total_gpu_hours * rate

    teacher_cost = (p["n_examples"] / 1000.0) * TEACHER_PER_1K[p["teacher"]]
    # iterate rounds generate ~2k extra examples each
    teacher_cost += iterate_rounds * 2.0 * TEACHER_PER_1K[p["teacher"]]

    judge_cost = p["n_evals"] * JUDGE_PER_EVAL[p["judge"]]

    return {
        "compute_cost": compute_cost,
        "teacher_cost": teacher_cost,
        "judge_cost": judge_cost,
        "total": compute_cost + teacher_cost + judge_cost,
        "gpu_hours": total_gpu_hours,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=list(PRESETS.keys()), default=None)
    parser.add_argument("--gpu", choices=list(GPU_RATES.keys()), default=None)
    parser.add_argument("--gpu-hourly", type=float, default=None,
                        help="Override GPU rate (USD/hr).")
    parser.add_argument("--gpu-count", type=int, default=1)
    parser.add_argument("--train-hours", type=float, default=None)
    parser.add_argument("--iterate-rounds", type=int, default=None)
    parser.add_argument("--teacher", choices=list(TEACHER_PER_1K.keys()), default=None)
    parser.add_argument("--judge", choices=list(JUDGE_PER_EVAL.keys()), default=None)
    parser.add_argument("--n-examples", type=int, default=None)
    parser.add_argument("--n-evals", type=int, default=None)
    parser.add_argument("--all-presets", action="store_true")
    args = parser.parse_args()

    if args.all_presets or (not args.preset and not args.gpu and not args.gpu_hourly):
        print("\nCAB-FF Trainer — cost estimates (approx May 2026 rates)\n")
        for name, p in PRESETS.items():
            e = estimate(p)
            print(f"  {name:<18} {p['label']}")
            print(f"  {'':18} compute ${e['compute_cost']:6.0f}  "
                  f"teacher ${e['teacher_cost']:5.0f}  "
                  f"judge ${e['judge_cost']:5.0f}  "
                  f"= {chr(0x1b)}[1mTOTAL ${e['total']:6.0f}{chr(0x1b)}[0m  "
                  f"({e['gpu_hours']:.0f} GPU-hr)")
            print()
        print("  Tip: `--preset e4b-cheap` is the cheapest real model; "
              "`--preset gemma-31b` is the recommended default.\n")
        return 0

    if args.preset:
        p = dict(PRESETS[args.preset])
    else:
        p = dict(PRESETS["gemma-31b"])

    # Apply overrides
    if args.gpu:
        p["gpu"] = args.gpu
    if args.gpu_hourly is not None:
        GPU_RATES["__custom__"] = args.gpu_hourly
        p["gpu"] = "__custom__"
    if args.gpu_count:
        p["gpu_count"] = args.gpu_count
    if args.train_hours is not None:
        p["train_hours"] = args.train_hours
    if args.iterate_rounds is not None:
        p["iterate_rounds"] = args.iterate_rounds
    if args.teacher:
        p["teacher"] = args.teacher
    if args.judge:
        p["judge"] = args.judge
    if args.n_examples:
        p["n_examples"] = args.n_examples
    if args.n_evals:
        p["n_evals"] = args.n_evals

    e = estimate(p)
    print(f"\n{p.get('label', 'custom run')}\n")
    print(f"  GPU:               {p['gpu']} × {p.get('gpu_count', 1)}")
    print(f"  GPU-hours:         {e['gpu_hours']:.1f}")
    print(f"  Compute cost:      ${e['compute_cost']:.0f}")
    print(f"  Teacher data cost: ${e['teacher_cost']:.0f}  "
          f"({p['n_examples']:,} examples via {p['teacher']})")
    print(f"  Judge eval cost:   ${e['judge_cost']:.0f}  "
          f"({p['n_evals']} full evals via {p['judge']})")
    print(f"  {'-'*40}")
    print(f"  \033[1mTOTAL ESTIMATE:   ${e['total']:.0f}\033[0m")
    print(f"\n  (Add ~30-50% buffer for retries and hyperparameter iteration.)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
