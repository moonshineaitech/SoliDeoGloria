"""DPO entrypoint.

Wraps TRL's DPOTrainer. Stacks on top of the SFT adapter by default
(continues training the same LoRA at a much lower LR).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    data_dir = Path(args.data_dir)

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import DPOConfig, DPOTrainer
    except ImportError as exc:
        print(f"[dpo] GPU stack not installed ({exc}). Install with: pip install -e '.[gpu]'")
        return 1

    tok = AutoTokenizer.from_pretrained(
        cfg["model"]["base_model"],
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    print(f"[dpo] loading base + SFT adapter from {cfg['model']['sft_adapter']}")
    model = AutoModelForCausalLM.from_pretrained(
        cfg["model"]["base_model"],
        torch_dtype=getattr(torch, cfg["model"].get("torch_dtype", "bfloat16")),
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
        attn_implementation=cfg["model"].get("attn_implementation", "flash_attention_2"),
    )
    # Load SFT LoRA
    model = PeftModel.from_pretrained(model, cfg["model"]["sft_adapter"], is_trainable=True)

    # Load preference data
    train_path = data_dir / cfg["data"].get("train_file", "pref_train.jsonl")
    eval_path = data_dir / cfg["data"].get("eval_file", "pref_eval.jsonl")
    train_ds = load_dataset("json", data_files=str(train_path))["train"]
    eval_ds = load_dataset("json", data_files=str(eval_path))["train"] \
        if eval_path.exists() else None
    print(f"[dpo] loaded {len(train_ds)} train + "
          f"{len(eval_ds) if eval_ds else 0} eval pairs")

    tcfg = cfg["training"]
    dpo_args = DPOConfig(
        output_dir=tcfg["output_dir"],
        beta=tcfg.get("beta", 0.1),
        loss_type=tcfg.get("loss_type", "sigmoid"),
        num_train_epochs=tcfg.get("num_train_epochs", 1),
        per_device_train_batch_size=tcfg.get("per_device_train_batch_size", 2),
        gradient_accumulation_steps=tcfg.get("gradient_accumulation_steps", 16),
        gradient_checkpointing=tcfg.get("gradient_checkpointing", True),
        learning_rate=tcfg.get("learning_rate", 5e-6),
        lr_scheduler_type=tcfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=tcfg.get("warmup_ratio", 0.05),
        optim=tcfg.get("optim", "adamw_bnb_8bit"),
        bf16=tcfg.get("bf16", True),
        tf32=tcfg.get("tf32", True),
        max_length=tcfg.get("max_length", 4096),
        max_prompt_length=tcfg.get("max_prompt_length", 2048),
        logging_steps=tcfg.get("logging_steps", 5),
        save_strategy=tcfg.get("save_strategy", "steps"),
        save_steps=tcfg.get("save_steps", 200),
        save_total_limit=tcfg.get("save_total_limit", 3),
        eval_strategy=tcfg.get("eval_strategy", "steps") if eval_ds else "no",
        eval_steps=tcfg.get("eval_steps", 100),
        load_best_model_at_end=tcfg.get("load_best_model_at_end", True) and bool(eval_ds),
        metric_for_best_model=tcfg.get("metric_for_best_model", "eval_loss"),
        greater_is_better=tcfg.get("greater_is_better", False),
        report_to=tcfg.get("report_to", ["tensorboard"]),
        seed=tcfg.get("seed", 17),
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=None,    # using the SFT model as implicit reference via PEFT
        args=dpo_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        processing_class=tok,
    )

    print("[dpo] starting DPO")
    trainer.train()
    print("[dpo] saving")
    trainer.save_model(tcfg["output_dir"])
    tok.save_pretrained(tcfg["output_dir"])

    # Merge for serving
    if cfg.get("output", {}).get("save_merged"):
        print("[dpo] merging LoRA into base for FP16 export...")
        base = AutoModelForCausalLM.from_pretrained(
            cfg["model"]["base_model"],
            torch_dtype=torch.bfloat16,
            trust_remote_code=cfg["model"].get("trust_remote_code", True),
        )
        merged = PeftModel.from_pretrained(base, tcfg["output_dir"])
        merged = merged.merge_and_unload()
        merged_dir = Path(tcfg["output_dir"]) / "merged"
        merged.save_pretrained(str(merged_dir), safe_serialization=True)
        tok.save_pretrained(str(merged_dir))
        print(f"[dpo] merged weights at {merged_dir}")

    print(f"[dpo] done -> {tcfg['output_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
