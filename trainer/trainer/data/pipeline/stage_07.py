"""Stage 07 — Split, mix, and format for the trainer."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List


def split_and_format(
    out_dir: Path,
    sft: List[Dict],
    prefs: List[Dict],
    multi: List[Dict],
    corpus: Dict[str, List[Dict]],
    seed: int = 17,
    eval_frac: float = 0.02,
) -> None:
    rng = random.Random(seed)

    # ---- SFT split ----
    # All SFT-shaped sources get combined (the YAML data_mix governs
    # WEIGHTING during the training step via TRL's interleave/concatenate
    # APIs; here we just write source-labelled files plus a single
    # `train.jsonl` / `eval.jsonl` for the trainer to read.)
    sft_pool: List[Dict] = []
    sft_pool.extend(sft)
    sft_pool.extend(multi)
    for bucket, records in corpus.items():
        sft_pool.extend(records)
    rng.shuffle(sft_pool)
    # Hold out eval_frac for eval, but never take more than 20% and always
    # leave at least one example for training (small runs must still work).
    n_eval = max(1, min(int(round(len(sft_pool) * eval_frac)), len(sft_pool) // 5))
    eval_set = sft_pool[:n_eval]
    train_set = sft_pool[n_eval:]
    _write_jsonl(out_dir / "train.jsonl", train_set)
    _write_jsonl(out_dir / "eval.jsonl", eval_set)

    # Also write source-labelled subsets for inspection / re-weighting
    _write_jsonl(out_dir / "sft_synth_only.jsonl", sft)
    _write_jsonl(out_dir / "multi_turn_only.jsonl", multi)
    for bucket, records in corpus.items():
        _write_jsonl(out_dir / f"corpus_{bucket}.jsonl", records)

    # ---- Preference split ----
    rng.shuffle(prefs)
    n_pref_eval = max(1, min(int(round(len(prefs) * eval_frac)), len(prefs) // 5))
    _write_jsonl(out_dir / "pref_train.jsonl", prefs[n_pref_eval:])
    _write_jsonl(out_dir / "pref_eval.jsonl", prefs[:n_pref_eval])

    # ---- GRPO prompts ----
    # Reuse the prompts from SFT and pref data as GRPO seed prompts.
    # We strip assistant turns so the policy has to generate them.
    grpo_prompts: List[Dict] = []
    for r in sft:
        msgs = r.get("messages", [])
        if not msgs:
            continue
        grpo_prompts.append({
            "prompt": msgs[0].get("content", ""),
            "meta": r.get("meta", {}),
        })
    for r in prefs:
        grpo_prompts.append({
            "prompt": r["prompt"],
            "meta": r.get("meta", {}),
        })
    rng.shuffle(grpo_prompts)
    _write_jsonl(out_dir / "grpo_prompts.jsonl", grpo_prompts[:5000])


def _write_jsonl(path: Path, records: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
