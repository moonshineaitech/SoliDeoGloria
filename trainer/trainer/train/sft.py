"""SFT entrypoint.

Wraps Hugging Face TRL's SFTTrainer with the YAML-config loader so users
can swap base models by editing one file. Supports LoRA / QLoRA, Liger
kernels, sequence packing, BF16, Flash Attention 2.

CLI:
    python -m trainer.train.sft --config configs/sft_qwen3_5_27b.yaml \\
                                --data-dir data/built

For dry-run on CPU with a tiny model:
    python -m trainer.train.sft --config configs/dry_run.yaml \\
                                --data-dir data/built/dry
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--data-dir", required=True,
                        help="Directory containing train.jsonl / eval.jsonl.")
    parser.add_argument("--resume-from", default=None,
                        help="Optional checkpoint to resume from.")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    data_dir = Path(args.data_dir)

    # Best-effort: if torch / transformers / trl aren't installed (e.g.
    # on a CPU-only machine running the dry-run), we still want the
    # command to demonstrate the pipeline rather than crash early.
    try:
        import torch
        from datasets import load_dataset
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
        )
        from trl import SFTTrainer, SFTConfig
    except ImportError as exc:
        print(f"[sft] GPU stack not installed ({exc}).")
        if "dry_run" in args.config:
            print("[sft] Dry-run mode: simulating training step on CPU without GPU stack.")
            _simulate_dry_run(cfg, data_dir)
            return 0
        print("Install with: pip install -e '.[gpu]'")
        return 1

    _set_seed(cfg["training"].get("seed", 17))

    # ---- Tokenizer ----
    tok = AutoTokenizer.from_pretrained(
        cfg["model"]["base_model"],
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # ---- Quantization (QLoRA path) ----
    bnb_config = None
    q_cfg = cfg.get("quantization") or {}
    if q_cfg.get("load_in_4bit"):
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type=q_cfg.get("bnb_4bit_quant_type", "nf4"),
            bnb_4bit_compute_dtype=getattr(
                torch, q_cfg.get("bnb_4bit_compute_dtype", "bfloat16")
            ),
            bnb_4bit_use_double_quant=q_cfg.get("bnb_4bit_use_double_quant", True),
        )

    # ---- Base model ----
    print(f"[sft] loading base model: {cfg['model']['base_model']}")
    model_kwargs = dict(
        torch_dtype=getattr(torch, cfg["model"].get("torch_dtype", "bfloat16")),
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
        attn_implementation=cfg["model"].get("attn_implementation", "flash_attention_2"),
    )
    if bnb_config is not None:
        model_kwargs["quantization_config"] = bnb_config
    model = AutoModelForCausalLM.from_pretrained(cfg["model"]["base_model"], **model_kwargs)

    # ---- PEFT (DoRA / LoRA / Spectrum) ----
    # Config schema: prefer `peft:` block (new). Fall back to legacy `lora:`.
    peft_cfg_dict = cfg.get("peft") or cfg.get("lora", {})
    peft_config = None
    use_dora = False
    if peft_cfg_dict and (peft_cfg_dict.get("enabled", True) is not False):
        from peft import LoraConfig
        method = (peft_cfg_dict.get("method") or
                  ("dora" if peft_cfg_dict.get("dora") else "lora")).lower()
        use_dora = method == "dora"
        peft_config = LoraConfig(
            r=peft_cfg_dict.get("r", 64),
            lora_alpha=peft_cfg_dict.get("alpha", 128),
            lora_dropout=peft_cfg_dict.get("dropout", 0.05),
            target_modules=peft_cfg_dict.get(
                "target_modules",
                ["q_proj", "k_proj", "v_proj", "o_proj",
                 "gate_proj", "up_proj", "down_proj"],
            ),
            bias="none",
            task_type=peft_cfg_dict.get("task_type", "CAUSAL_LM"),
            modules_to_save=peft_cfg_dict.get("modules_to_save", []),
            use_dora=use_dora,                  # DoRA toggle (peft >= 0.10)
        )
        print(f"[sft] PEFT method: {'DoRA' if use_dora else 'LoRA'} "
              f"r={peft_config.r} alpha={peft_config.lora_alpha}")

    # ---- NEFTune (noisy embeddings) ----
    neftune_alpha = (cfg.get("neftune") or {}).get("alpha") \
        if (cfg.get("neftune") or {}).get("enabled") else None
    if neftune_alpha:
        print(f"[sft] NEFTune enabled (alpha={neftune_alpha})")

    # ---- Liger kernels (model-family-aware) ----
    if (cfg.get("liger_kernel") or {}).get("enabled"):
        try:
            base_id = cfg["model"]["base_model"].lower()
            # Pick the matching apply_liger_kernel_to_<family> function
            applied = False
            try:
                if "qwen" in base_id:
                    from liger_kernel.transformers import apply_liger_kernel_to_qwen2
                    apply_liger_kernel_to_qwen2(
                        rope=cfg["liger_kernel"].get("rope", True),
                        rms_norm=cfg["liger_kernel"].get("rms_norm", True),
                        swiglu=cfg["liger_kernel"].get("swiglu", True),
                        cross_entropy=cfg["liger_kernel"].get("cross_entropy", True),
                        fused_linear_cross_entropy=cfg["liger_kernel"].get(
                            "fused_linear_cross_entropy", True),
                    )
                    applied = True
                elif "gemma" in base_id:
                    from liger_kernel.transformers import apply_liger_kernel_to_gemma2
                    apply_liger_kernel_to_gemma2(
                        rope=cfg["liger_kernel"].get("rope", True),
                        rms_norm=cfg["liger_kernel"].get("rms_norm", True),
                        cross_entropy=cfg["liger_kernel"].get("cross_entropy", True),
                        fused_linear_cross_entropy=cfg["liger_kernel"].get(
                            "fused_linear_cross_entropy", True),
                    )
                    applied = True
                elif "llama" in base_id:
                    from liger_kernel.transformers import apply_liger_kernel_to_llama
                    apply_liger_kernel_to_llama(
                        rope=cfg["liger_kernel"].get("rope", True),
                        rms_norm=cfg["liger_kernel"].get("rms_norm", True),
                        swiglu=cfg["liger_kernel"].get("swiglu", True),
                        cross_entropy=cfg["liger_kernel"].get("cross_entropy", True),
                        fused_linear_cross_entropy=cfg["liger_kernel"].get(
                            "fused_linear_cross_entropy", True),
                    )
                    applied = True
            except ImportError:
                pass
            if applied:
                print("[sft] applied Liger kernels.")
            else:
                print(f"[sft] no Liger kernel match for {base_id}; using stock ops.")
        except ImportError:
            print("[sft] liger_kernel not installed; continuing without it.")

    # ---- Data ----
    train_path = data_dir / cfg["data"].get("train_file", "train.jsonl")
    eval_path = data_dir / cfg["data"].get("eval_file", "eval.jsonl")
    if not train_path.exists():
        print(f"[sft] ERROR: training data not found at {train_path}.")
        return 1
    train_ds = load_dataset("json", data_files=str(train_path))["train"]
    eval_ds = load_dataset("json", data_files=str(eval_path))["train"] \
        if eval_path.exists() else None
    print(f"[sft] loaded {len(train_ds)} train + "
          f"{len(eval_ds) if eval_ds else 0} eval examples")

    # ---- TRL SFTConfig ----
    tcfg = cfg["training"]
    sft_args = SFTConfig(
        output_dir=tcfg["output_dir"],
        num_train_epochs=tcfg.get("num_train_epochs", 2),
        max_steps=tcfg.get("max_steps", -1),
        per_device_train_batch_size=tcfg.get("per_device_train_batch_size", 4),
        gradient_accumulation_steps=tcfg.get("gradient_accumulation_steps", 8),
        gradient_checkpointing=tcfg.get("gradient_checkpointing", True),
        gradient_checkpointing_kwargs=tcfg.get("gradient_checkpointing_kwargs", {}),
        learning_rate=tcfg.get("learning_rate", 2e-4),
        lr_scheduler_type=tcfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=tcfg.get("warmup_ratio", 0.03),
        weight_decay=tcfg.get("weight_decay", 0.0),
        optim=tcfg.get("optim", "adamw_torch_fused"),
        bf16=tcfg.get("bf16", True),
        tf32=tcfg.get("tf32", True),
        fp16=tcfg.get("fp16", False),
        max_seq_length=tcfg.get("max_seq_length", 4096),
        packing=tcfg.get("packing", True),
        logging_steps=tcfg.get("logging_steps", 5),
        save_strategy=tcfg.get("save_strategy", "steps"),
        save_steps=tcfg.get("save_steps", 500),
        save_total_limit=tcfg.get("save_total_limit", 3),
        eval_strategy=tcfg.get("eval_strategy", "steps") if eval_ds else "no",
        eval_steps=tcfg.get("eval_steps", 250),
        load_best_model_at_end=tcfg.get("load_best_model_at_end", True) and bool(eval_ds),
        metric_for_best_model=tcfg.get("metric_for_best_model", "eval_loss"),
        greater_is_better=tcfg.get("greater_is_better", False),
        report_to=tcfg.get("report_to", ["tensorboard"]),
        seed=tcfg.get("seed", 17),
        # NEFTune integration — TRL exposes this directly as a config field
        neftune_noise_alpha=neftune_alpha,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        peft_config=peft_config,
        processing_class=tok,
    )

    print("[sft] starting training")
    trainer.train(resume_from_checkpoint=args.resume_from)
    print("[sft] saving final checkpoint")
    trainer.save_model(tcfg["output_dir"])
    tok.save_pretrained(tcfg["output_dir"])

    # ---- Optional: merge LoRA into base for vLLM serving ----
    if cfg.get("output", {}).get("save_merged") and lora_cfg.get("enabled"):
        print("[sft] merging LoRA into base for FP16 export...")
        from peft import PeftModel
        merged_dir = Path(tcfg["output_dir"]) / "merged"
        base = AutoModelForCausalLM.from_pretrained(
            cfg["model"]["base_model"],
            torch_dtype=torch.bfloat16,
            trust_remote_code=cfg["model"].get("trust_remote_code", True),
        )
        merged = PeftModel.from_pretrained(base, tcfg["output_dir"])
        merged = merged.merge_and_unload()
        merged.save_pretrained(str(merged_dir), safe_serialization=True)
        tok.save_pretrained(str(merged_dir))
        print(f"[sft] merged weights at {merged_dir}")

    # Write the run metadata
    Path(tcfg["output_dir"], "training_meta.json").write_text(
        json.dumps({
            "base_model": cfg["model"]["base_model"],
            "config_path": args.config,
            "data_dir": str(data_dir),
            "num_train": len(train_ds),
            "num_eval": len(eval_ds) if eval_ds else 0,
            "lora": lora_cfg,
        }, indent=2)
    )
    print(f"[sft] done -> {tcfg['output_dir']}")
    return 0


def _set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def _simulate_dry_run(cfg: Dict[str, Any], data_dir: Path) -> None:
    """For dry-run on CPU when the GPU stack isn't installed."""
    train_path = data_dir / cfg["data"].get("train_file", "train.jsonl")
    n = sum(1 for _ in train_path.open()) if train_path.exists() else 0
    out = Path(cfg["training"]["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    out.joinpath("dry_run_marker.json").write_text(
        json.dumps({"base_model": cfg["model"]["base_model"],
                    "train_examples": n,
                    "status": "dry_run_simulation"}, indent=2)
    )
    print(f"[dry-sft] simulated {n} examples → {out}")


if __name__ == "__main__":
    sys.exit(main())
