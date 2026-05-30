"""Continued pre-training (CPT) entrypoint.

Optional stage to absorb the Christian corpus (Scripture, confessions,
classical theology) directly into the base model weights before SFT.
Recommended only for smaller bases (≤9B); for 27B+ the SFT stage's
corpus_qa mix is usually enough.

Usage:
    python -m trainer.train.continued_pretrain --config configs/cpt_qwen3_5_9b.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--corpus-dir", required=True,
                        help="Directory of text files to use as CPT corpus.")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer,
            DataCollatorForLanguageModeling, Trainer, TrainingArguments,
        )
    except ImportError as exc:
        print(f"[cpt] GPU stack not installed ({exc}). Install: pip install -e '.[gpu]'")
        return 1

    tok = AutoTokenizer.from_pretrained(
        cfg["model"]["base_model"], trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg["model"]["base_model"],
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        attn_implementation=cfg["model"].get("attn_implementation", "flash_attention_2"),
    )

    if cfg.get("lora", {}).get("enabled"):
        from peft import get_peft_model
        peft_cfg = LoraConfig(
            r=cfg["lora"].get("r", 32),
            lora_alpha=cfg["lora"].get("alpha", 64),
            lora_dropout=0.0,
            target_modules=cfg["lora"].get("target_modules",
                ["q_proj", "k_proj", "v_proj", "o_proj"]),
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, peft_cfg)

    ds = load_dataset("text", data_files={"train": f"{args.corpus_dir}/*.txt"})

    def _tokenize(batch):
        return tok(batch["text"], truncation=True, max_length=cfg["training"].get("max_seq_length", 2048))

    ds_tok = ds.map(_tokenize, batched=True, remove_columns=["text"])
    collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)

    args_ = TrainingArguments(
        output_dir=cfg["training"]["output_dir"],
        num_train_epochs=cfg["training"].get("num_train_epochs", 1),
        per_device_train_batch_size=cfg["training"].get("per_device_train_batch_size", 1),
        gradient_accumulation_steps=cfg["training"].get("gradient_accumulation_steps", 16),
        gradient_checkpointing=True,
        learning_rate=cfg["training"].get("learning_rate", 5e-5),
        warmup_ratio=0.03,
        bf16=True,
        save_total_limit=2,
        logging_steps=10,
        save_steps=500,
        report_to=["tensorboard"],
        seed=17,
    )
    trainer = Trainer(model=model, args=args_, train_dataset=ds_tok["train"],
                      data_collator=collator)
    trainer.train()
    trainer.save_model(cfg["training"]["output_dir"])
    tok.save_pretrained(cfg["training"]["output_dir"])
    print(f"[cpt] done -> {cfg['training']['output_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
