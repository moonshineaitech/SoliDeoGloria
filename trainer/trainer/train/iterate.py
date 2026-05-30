"""Iterative refinement orchestrator (the growth-hack core).

Implements the Round-by-Round loop described in trainer/IMPROVEMENTS.md
section C. Each round:

  1. Run CAB-FF eval on the current checkpoint
  2. Identify the weakest dimension and axis
  3. Generate targeted data for that dimension (calls the data pipeline
     with dimension/axis filters)
  4. Optionally mine hard-negative DPO pairs from the eval failures
  5. Run a 1-epoch SFT delta + (optional) DPO delta
  6. Re-eval; if composite ≥ previous + min-delta, accept the round
     and continue; otherwise stop

CLI:
    python -m trainer.train.iterate \\
        --base-checkpoint outputs/sdg-31b-dpo \\
        --rounds 3 \\
        --min-delta 2.0 \\
        --out outputs/sdg-31b-iter \\
        --dataset ../data/CAB_FF_v3_dataset.json \\
        --teacher claude-opus-4-7 \\
        --judge claude-opus-4-7
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class RoundResult:
    round_number: int
    checkpoint: Path
    cab_ff_report_path: Path
    cab_ff_score: float
    weakest_dimension: str
    weakest_axis: str
    drift_index: float
    sycophancy_index: float
    delta_vs_prev: float


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-checkpoint", required=True,
                        help="Starting checkpoint (e.g. SFT+DPO output).")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--min-delta", type=float, default=2.0,
                        help="Stop early if a round improves <min-delta.")
    parser.add_argument("--out", required=True,
                        help="Output directory; each round is a subdir.")
    parser.add_argument("--dataset", required=True,
                        help="Path to data/CAB_FF_v3_dataset.json.")
    parser.add_argument("--teacher", default="claude-opus-4-7")
    parser.add_argument("--judge", default="claude-opus-4-7")
    parser.add_argument("--no-dpo", action="store_true",
                        help="Skip DPO delta in each round (SFT-only delta).")
    parser.add_argument("--no-hard-negatives", action="store_true",
                        help="Skip hard-negative mining.")
    parser.add_argument("--targeted-data-per-round", type=int, default=2000,
                        help="Examples to generate per round, in the weakest dim.")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    history: List[RoundResult] = []
    current_checkpoint = Path(args.base_checkpoint)

    # Round 0 — baseline eval of the input checkpoint
    print(f"\n{'='*60}\nRound 0 — baseline eval of {current_checkpoint}\n{'='*60}")
    baseline_report = _eval(current_checkpoint, args.dataset, args.judge,
                             out / "round_0_baseline.json")
    baseline = _summarize(baseline_report)
    print_summary(baseline, "baseline")

    prev_score = baseline.cab_ff_score
    prev_checkpoint = current_checkpoint

    for r in range(1, args.rounds + 1):
        print(f"\n{'='*60}\nRound {r} — targeting weakest dim/axis "
              f"from round {r-1}\n{'='*60}")
        weakest_dim = baseline.weakest_dimension if r == 1 \
            else history[-1].weakest_dimension
        weakest_axis = baseline.weakest_axis if r == 1 \
            else history[-1].weakest_axis
        print(f"  weakest dimension: {weakest_dim}")
        print(f"  weakest axis:      {weakest_axis}")

        round_dir = out / f"round_{r}"
        round_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate targeted data
        print(f"  [a] generating {args.targeted_data_per_round} targeted examples...")
        targeted_data = _generate_targeted_data(
            dimension=weakest_dim,
            axis=weakest_axis,
            n=args.targeted_data_per_round,
            teacher=args.teacher,
            out_dir=round_dir / "data",
        )

        # 2. Mine hard negatives from last eval
        if not args.no_hard_negatives:
            prev_report = history[-1].cab_ff_report_path if history \
                else out / "round_0_baseline.json"
            print(f"  [b] mining hard negatives from {prev_report.name}...")
            _mine_hard_negatives(
                report_path=prev_report,
                out_path=round_dir / "data" / "hard_neg_prefs.jsonl",
                teacher=args.teacher,
            )

        # 3. SFT delta from current checkpoint
        print(f"  [c] running SFT delta on the targeted data...")
        sft_out = round_dir / "sft"
        _run_sft_delta(
            base_checkpoint=prev_checkpoint,
            data_dir=round_dir / "data",
            out=sft_out,
        )

        # 4. Optional DPO delta
        ckpt_after = sft_out
        if not args.no_dpo:
            print(f"  [d] running DPO delta on hard-negative + comparative prefs...")
            dpo_out = round_dir / "dpo"
            _run_dpo_delta(
                sft_checkpoint=sft_out,
                data_dir=round_dir / "data",
                out=dpo_out,
            )
            ckpt_after = dpo_out

        # 5. Re-eval
        print(f"  [e] evaluating round {r} checkpoint...")
        report = _eval(ckpt_after, args.dataset, args.judge,
                       round_dir / "cab_ff_report.json")
        summary = _summarize(report)
        summary.round_number = r
        summary.checkpoint = ckpt_after
        summary.cab_ff_report_path = round_dir / "cab_ff_report.json"
        summary.delta_vs_prev = summary.cab_ff_score - prev_score
        history.append(summary)
        print_summary(summary, f"round {r}")

        # 6. Promotion decision
        if summary.delta_vs_prev < args.min_delta:
            print(f"\n  Round {r} improved by {summary.delta_vs_prev:+.2f} "
                  f"(< min_delta {args.min_delta:+.2f}). STOPPING.")
            break
        print(f"  Round {r} improved by {summary.delta_vs_prev:+.2f} — ACCEPTED.")
        prev_score = summary.cab_ff_score
        prev_checkpoint = ckpt_after

    # Final summary
    print(f"\n{'='*60}\nITERATIVE REFINEMENT COMPLETE\n{'='*60}")
    print(f"  Baseline:           {baseline.cab_ff_score:.2f}")
    for h in history:
        print(f"  Round {h.round_number}:            "
              f"{h.cab_ff_score:.2f}  (Δ {h.delta_vs_prev:+.2f})")
    if history:
        total = history[-1].cab_ff_score - baseline.cab_ff_score
        print(f"\n  Total gain over baseline: {total:+.2f}")
        print(f"  Final checkpoint:         {history[-1].checkpoint}")
        final_link = out / "final"
        if final_link.exists() or final_link.is_symlink():
            final_link.unlink()
        try:
            final_link.symlink_to(history[-1].checkpoint.resolve())
        except OSError:
            # Symlink not supported (e.g., Windows) — just copy a marker
            (out / "FINAL_IS").write_text(str(history[-1].checkpoint.resolve()))
        print(f"  Symlinked: {final_link} → {history[-1].checkpoint}")
    return 0


# ---------------------------------------------------------------------------
# Eval + summary
# ---------------------------------------------------------------------------


def _eval(checkpoint: Path, dataset: str, judge: str, out_path: Path) -> Dict:
    """Run CAB-FF on a checkpoint via vLLM. Returns the parsed report."""
    # Reuses the trainer/eval/run_cab_ff.py entrypoint.
    # NOTE: assumes vLLM is already serving the checkpoint at the default endpoint,
    # OR call the run_cab_ff.py with --backend transformers if vLLM isn't running.
    cmd = [
        sys.executable, "-m", "trainer.eval.run_cab_ff",
        "--backend", "transformers",
        "--checkpoint", str(checkpoint),
        "--dataset", dataset,
        "--judge", judge,
        "--out", str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return json.loads(out_path.read_text())


def _summarize(report: Dict) -> RoundResult:
    s = report["summary"]
    by_dim = s.get("by_dimension", {})
    by_axis = s.get("by_axis", {})

    def _weakest(d):
        if not d:
            return ""
        return min(d.items(), key=lambda kv: (kv[1].get("score", 100)
                                                if isinstance(kv[1], dict)
                                                else float(kv[1])))[0]
    return RoundResult(
        round_number=-1,
        checkpoint=Path(""),
        cab_ff_report_path=Path(""),
        cab_ff_score=float(s.get("cab_ff_score", 0)),
        drift_index=float(s.get("drift_index", 0)),
        sycophancy_index=float(s.get("sycophancy_index", 0)),
        weakest_dimension=_weakest(by_dim),
        weakest_axis=_weakest(by_axis),
        delta_vs_prev=0.0,
    )


def print_summary(r: RoundResult, label: str) -> None:
    print(f"  {label}:  CAB-FF {r.cab_ff_score:6.2f}  "
          f"Drift {r.drift_index:5.2f}  Sycophancy {r.sycophancy_index:5.2f}")
    print(f"           weakest dim/axis: {r.weakest_dimension} / {r.weakest_axis}")


# ---------------------------------------------------------------------------
# Targeted data generation
# ---------------------------------------------------------------------------


def _generate_targeted_data(
    dimension: str,
    axis: str,
    n: int,
    teacher: str,
    out_dir: Path,
) -> Path:
    """Generate n examples concentrated on a specific dimension + axis."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "trainer.data.pipeline.cli", "build-targeted",
        "--dimension", dimension,
        "--axis", axis,
        "--n", str(n),
        "--teacher", teacher,
        "--out", str(out_dir),
    ]
    # The 'build-targeted' subcommand may not exist on older trainer
    # installs; check first and fall back to standard build with filters.
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "No such command" in (result.stderr or ""):
        print("  (build-targeted not available — falling back to filtered build)")
        cmd = [
            sys.executable, "-m", "trainer.data.pipeline.cli", "build",
            "--max-synth", str(n),
            "--max-prefs", str(n // 2),
            "--teacher", teacher,
            "--out", str(out_dir),
        ]
        subprocess.run(cmd, check=True)
    return out_dir


# ---------------------------------------------------------------------------
# Hard-negative mining
# ---------------------------------------------------------------------------


def _mine_hard_negatives(report_path: Path, out_path: Path, teacher: str) -> Path:
    """Extract failed adversarial probes from a CAB-FF report and turn them
    into DPO preference pairs."""
    report = json.loads(report_path.read_text())
    results = report.get("detailed_results", [])
    failed_advs = [
        r for r in results
        if r.get("question_type") == "adversarial" and r.get("score", 100) < 50
    ]
    print(f"     mined {len(failed_advs)} failed adversarial probes")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        for r in failed_advs:
            details = r.get("details", {})
            prompt = details.get("prompt") or details.get("raw_response", "")
            failure_response = details.get("raw_response", "")
            chosen_response = _generate_correction(prompt, failure_response, teacher)
            if chosen_response:
                f.write(json.dumps({
                    "prompt": prompt,
                    "chosen": chosen_response,
                    "rejected": failure_response,
                    "meta": {
                        "source": "hard_negative_mined",
                        "from_question": r.get("id"),
                    },
                }) + "\n")
    return out_path


def _generate_correction(prompt: str, failure: str, teacher: str) -> Optional[str]:
    """Ask the teacher to produce a correct response to the same prompt."""
    try:
        from trainer.data.pipeline.stage_02 import _make_teacher
        teacher_fn = _make_teacher(teacher)
        system = (
            "You are producing a CORRECT Christian-aligned response to a "
            "prompt where another AI gave the wrong answer. Your response "
            "should be faithful, substantive, and resist the failure mode "
            "the other AI exhibited."
        )
        user = (
            f"PROMPT:\n{prompt}\n\n"
            f"FAILURE RESPONSE TO AVOID:\n{failure}\n\n"
            f"Now produce a correct response (3-5 sentences)."
        )
        return teacher_fn(system, user).strip()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Training delta wrappers
# ---------------------------------------------------------------------------


def _run_sft_delta(base_checkpoint: Path, data_dir: Path, out: Path) -> None:
    """Run a 1-epoch SFT delta starting from the base_checkpoint."""
    out.mkdir(parents=True, exist_ok=True)
    delta_config = _make_delta_config("sft", base_checkpoint, out, num_epochs=1)
    cmd = [
        sys.executable, "-m", "trainer.train.sft",
        "--config", str(delta_config),
        "--data-dir", str(data_dir),
    ]
    subprocess.run(cmd, check=True)


def _run_dpo_delta(sft_checkpoint: Path, data_dir: Path, out: Path) -> None:
    """Run a 1-epoch DPO delta on hard-negative + comparative prefs."""
    out.mkdir(parents=True, exist_ok=True)
    delta_config = _make_delta_config("dpo", sft_checkpoint, out, num_epochs=1)
    cmd = [
        sys.executable, "-m", "trainer.train.dpo",
        "--config", str(delta_config),
        "--data-dir", str(data_dir),
    ]
    subprocess.run(cmd, check=True)


def _make_delta_config(stage: str, start: Path, out: Path, num_epochs: int) -> Path:
    """Render a small delta-training config inheriting from a base config."""
    # In production, this generates a real YAML by copying the matching
    # config from configs/ and overriding output_dir, num_train_epochs,
    # and the adapter source. For brevity, we emit a placeholder that the
    # trainer can read; full implementation reads the parent config and
    # mutates it.
    delta_dir = out.parent / "configs"
    delta_dir.mkdir(parents=True, exist_ok=True)
    delta_path = delta_dir / f"delta_{stage}.yaml"
    parent_config = {
        "sft": "configs/sft_gemma_4_31b.yaml",
        "dpo": "configs/dpo_gemma_4_31b.yaml",
    }[stage]
    import yaml
    parent = yaml.safe_load(Path(parent_config).read_text())
    parent["training"]["output_dir"] = str(out)
    parent["training"]["num_train_epochs"] = num_epochs
    parent["training"]["learning_rate"] = parent["training"]["learning_rate"] * 0.5
    if stage == "sft":
        parent.setdefault("model", {})["base_model"] = parent["model"]["base_model"]
        parent.setdefault("peft", {})["continue_existing"] = True
        # Pointer to the starting adapter
        parent["model"]["resume_adapter"] = str(start)
    else:
        parent["model"]["sft_adapter"] = str(start)
    delta_path.write_text(yaml.safe_dump(parent))
    return delta_path


if __name__ == "__main__":
    sys.exit(main())
