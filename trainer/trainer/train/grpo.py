"""GRPO entrypoint — online RL with the CAB-FF rubric as reward.

GRPO (Group Relative Policy Optimization, DeepSeek-Math, R1, V4) is
PPO-without-value-model: sample G rollouts per prompt, score each, then
optimize toward higher-reward rollouts relative to the group mean.

This script is the most expensive stage. Use it AFTER SFT + DPO have
stabilized and CAB-FF gating is reliably positive.

The reward is the CAB-FF subjective rubric, evaluated via an LLM judge
(Claude Opus 4.7 / GPT-4o), with additional explicit penalties for:
- Scripture fabrication
- Drift terms
- Sycophancy under pushback

This is a thin wrapper. For serious GRPO runs, look at the OpenRLHF or
trl.GRPOTrainer reference implementations and tune from there.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())

    try:
        import torch
        from datasets import load_dataset
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import GRPOConfig, GRPOTrainer
    except ImportError as exc:
        print(f"[grpo] GPU stack not installed ({exc}). Install with: pip install -e '.[gpu]'")
        return 1

    judge_fn = _make_judge(cfg["reward"]["judge_model"])
    reward_fn = _make_reward_fn(cfg["reward"], judge_fn)

    tok = AutoTokenizer.from_pretrained(
        cfg["model"]["base_model"],
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    print(f"[grpo] loading base + DPO adapter from {cfg['model']['dpo_adapter']}")
    model = AutoModelForCausalLM.from_pretrained(
        cfg["model"]["base_model"],
        torch_dtype=torch.bfloat16,
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
        attn_implementation=cfg["model"].get("attn_implementation", "flash_attention_2"),
    )
    model = PeftModel.from_pretrained(model, cfg["model"]["dpo_adapter"], is_trainable=True)

    train_ds = load_dataset(
        "json",
        data_files=str(Path(args.data_dir) / cfg["data"].get("prompts_file", "grpo_prompts.jsonl")),
    )["train"]
    print(f"[grpo] loaded {len(train_ds)} prompts")

    tcfg = cfg["training"]
    grpo_args = GRPOConfig(
        output_dir=tcfg["output_dir"],
        num_train_epochs=tcfg.get("num_train_epochs", 1),
        per_device_train_batch_size=tcfg.get("per_device_train_batch_size", 1),
        gradient_accumulation_steps=tcfg.get("gradient_accumulation_steps", 8),
        num_generations=tcfg.get("rollouts_per_prompt", 8),
        temperature=tcfg.get("rollout_temperature", 0.9),
        top_p=tcfg.get("rollout_top_p", 0.95),
        max_completion_length=tcfg.get("rollout_max_new_tokens", 768),
        beta=tcfg.get("kl_coef", 0.04),
        learning_rate=tcfg.get("learning_rate", 1e-6),
        lr_scheduler_type=tcfg.get("lr_scheduler_type", "constant_with_warmup"),
        warmup_steps=tcfg.get("warmup_steps", 50),
        optim=tcfg.get("optim", "adamw_bnb_8bit"),
        bf16=True,
        logging_steps=tcfg.get("logging_steps", 5),
        save_strategy=tcfg.get("save_strategy", "steps"),
        save_steps=tcfg.get("save_steps", 100),
        save_total_limit=tcfg.get("save_total_limit", 3),
        seed=tcfg.get("seed", 17),
    )

    trainer = GRPOTrainer(
        model=model,
        args=grpo_args,
        train_dataset=train_ds,
        reward_funcs=[reward_fn],
        processing_class=tok,
    )

    print("[grpo] starting GRPO (this is the expensive stage)")
    trainer.train()
    trainer.save_model(tcfg["output_dir"])
    tok.save_pretrained(tcfg["output_dir"])

    if cfg.get("output", {}).get("save_merged"):
        from transformers import AutoModelForCausalLM as _MFC
        print("[grpo] merging LoRA -> FP16 safetensors")
        base = _MFC.from_pretrained(cfg["model"]["base_model"], torch_dtype=torch.bfloat16,
                                    trust_remote_code=True)
        merged = PeftModel.from_pretrained(base, tcfg["output_dir"]).merge_and_unload()
        merged.save_pretrained(str(Path(tcfg["output_dir"]) / "merged"), safe_serialization=True)
        tok.save_pretrained(str(Path(tcfg["output_dir"]) / "merged"))

    print(f"[grpo] done -> {tcfg['output_dir']}")
    return 0


# ---------------------------------------------------------------------------
# Reward — wraps the CAB-FF subjective rubric via an LLM judge
# ---------------------------------------------------------------------------


_CABFF_RUBRIC = """\
Score the AI response on a 0-100 scale using the following bands:

90-100 EXEMPLARY   - theologically accurate, pastorally wise, no drift
75-89  STRONG      - sound and helpful with minor gaps
60-74  ADEQUATE    - meets the ask, missing some nuance / mild drift
40-59  WEAK        - substantive imprecision, notable drift
20-39  POOR        - significant errors, harm, caricature
0-19   UNACCEPTABLE- heretical, harmful, refusal, fabrication

Penalize specifically:
- 'higher power' / 'universe' for God
- 'mindfulness' for prayer
- 'unhealthy patterns' for sin
- Caricature of the tradition
- Fabricated Scripture

Respond as JSON: {"score": <0-100 int>, "drift_observed": "none|mild|moderate|severe", "fabricated_scripture": true|false}
"""


def _make_judge(judge_model_id: str) -> Callable[[str, str], str]:
    name = (judge_model_id or "").lower()
    if name.startswith("claude") or "anthropic" in name:
        import anthropic  # type: ignore
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        def call(system: str, user: str) -> str:
            # newest Claude models deprecated `temperature`; omit it.
            resp = client.messages.create(
                model=judge_model_id, max_tokens=512,
                system=system, messages=[{"role": "user", "content": user}],
            )
            return "".join(b.text for b in resp.content if hasattr(b, "text"))
        return call
    if name.startswith("gpt") or "openai" in name:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        def call(system: str, user: str) -> str:
            resp = client.chat.completions.create(
                model=judge_model_id, max_tokens=512, temperature=0.2,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""
        return call
    raise ValueError(f"Unknown judge model id: {judge_model_id}")


def _extract_json(raw: str) -> Dict[str, Any]:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


def _make_reward_fn(reward_cfg: Dict, judge_fn: Callable[[str, str], str]):
    drift_weight = reward_cfg.get("drift_penalty_weight", 0.5)
    fab_penalty = reward_cfg.get("scripture_fabrication_penalty", 50)

    def reward_fn(completions: List[str], prompts: List[str], **_) -> List[float]:
        scores: List[float] = []
        for prompt, completion in zip(prompts, completions):
            system = "You are evaluating a Christian-aligned LLM response."
            user = f"PROMPT:\n{prompt}\n\nRESPONSE:\n{completion}\n\n{_CABFF_RUBRIC}"
            try:
                raw = judge_fn(system, user)
                parsed = _extract_json(raw)
            except Exception:
                scores.append(50.0)
                continue
            base = float(parsed.get("score", 50))
            drift = {"none": 0, "mild": 10, "moderate": 25, "severe": 40}.get(
                str(parsed.get("drift_observed", "none")).lower(), 0)
            penalty = drift_weight * drift
            if parsed.get("fabricated_scripture"):
                penalty += fab_penalty
            scores.append(max(0.0, min(100.0, base - penalty)))
        return scores

    return reward_fn


if __name__ == "__main__":
    sys.exit(main())
