.PHONY: help dry-run data sft dpo grpo eval gate quantize publish clean install gpu-install
.DEFAULT_GOAL := help

# Defaults — override on the command line, e.g. `make sft CONFIG=...`
CONFIG       ?= configs/sft_qwen3_5_27b.yaml
DPO_CONFIG   ?= configs/dpo_qwen3_5_27b.yaml
GRPO_CONFIG  ?= configs/grpo_qwen3_5_27b.yaml
CHECKPOINT   ?= outputs/sdg-27b-dpo
HF_REPO      ?= solideogloria/sdg-27b-v0.1
TEACHER      ?= claude-opus-4-7
DATA_OUT     ?= data/built
DATASET      ?= ../data/CAB_FF_v3_dataset.json

help:
	@echo "CAB-FF Trainer — common tasks"
	@echo ""
	@echo "  make install        Install core (data pipeline only, no GPU deps)"
	@echo "  make gpu-install    Install full GPU stack (Torch, TRL, PEFT, Liger)"
	@echo "  make dry-run        Verify the whole pipeline on tiny synthetic data"
	@echo "                      (~3 min, no GPU, no API key required)"
	@echo ""
	@echo "  make data           Generate SFT + DPO training data from CAB-FF"
	@echo "                      schema (uses TEACHER=\$$TEACHER, default $(TEACHER))"
	@echo "  make sft            Run SFT  (default: CONFIG=$(CONFIG))"
	@echo "  make dpo            Run DPO  (default: CONFIG=$(DPO_CONFIG))"
	@echo "  make grpo           Run GRPO (default: CONFIG=$(GRPO_CONFIG))"
	@echo "  make eval           Run CAB-FF against CHECKPOINT=$(CHECKPOINT)"
	@echo "  make gate           Compare CHECKPOINT to base model, gate promotion"
	@echo "  make quantize       Produce AWQ INT4 + GGUF Q4_K_M from CHECKPOINT"
	@echo "  make publish        Push CHECKPOINT to HF Hub (HF_REPO=$(HF_REPO))"
	@echo ""
	@echo "  make clean          Remove caches, intermediates, dry-run artifacts"

install:
	pip install -e .

gpu-install:
	pip install -e ".[gpu,teachers,eval,deploy]"
	@echo ""
	@echo "Now install flash-attn for your CUDA build:"
	@echo "  pip install flash-attn==2.7.0 --no-build-isolation"

dry-run:
	@echo "[dry-run] generating 20 synthetic SFT examples..."
	python -m trainer.data.pipeline.cli dry-run --out $(DATA_OUT)/dry
	@echo "[dry-run] running tiny-model micro-SFT..."
	python -m trainer.train.sft --config configs/dry_run.yaml --data-dir $(DATA_OUT)/dry
	@echo "[dry-run] running CAB-FF against mock model..."
	python -m trainer.eval.run_cab_ff --mock --dataset $(DATASET) --max-questions 5
	@echo "[dry-run] OK — pipeline is wired correctly."

data:
	python -m trainer.data.pipeline.cli build \
	    --dataset $(DATASET) \
	    --teacher $(TEACHER) \
	    --out $(DATA_OUT)

sft:
	python -m trainer.train.sft --config $(CONFIG) --data-dir $(DATA_OUT)

dpo:
	python -m trainer.train.dpo --config $(DPO_CONFIG) --data-dir $(DATA_OUT)

grpo:
	python -m trainer.train.grpo --config $(GRPO_CONFIG) --data-dir $(DATA_OUT)

eval:
	python -m trainer.eval.run_cab_ff \
	    --checkpoint $(CHECKPOINT) \
	    --dataset $(DATASET) \
	    --judge $(TEACHER) \
	    --out $(CHECKPOINT)/cab_ff_report.json

gate:
	python -m trainer.eval.gating \
	    --checkpoint-report $(CHECKPOINT)/cab_ff_report.json \
	    --baseline-report baselines/qwen3_5_27b_base_report.json

quantize:
	python -m trainer.deploy.quantize_awq --checkpoint $(CHECKPOINT)
	python -m trainer.deploy.quantize_gguf --checkpoint $(CHECKPOINT) --quants Q4_K_M Q5_K_M

publish:
	python -m trainer.deploy.push_to_hub \
	    --checkpoint $(CHECKPOINT) \
	    --repo $(HF_REPO) \
	    --eval-report $(CHECKPOINT)/cab_ff_report.json

clean:
	rm -rf $(DATA_OUT)/dry outputs/dry-run __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
