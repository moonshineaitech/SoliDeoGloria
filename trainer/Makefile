.PHONY: help dry-run data sft dpo grpo iterate best-of-n eval drilldown gate quantize publish clean install gpu-install
.DEFAULT_GOAL := help

# Defaults — override on the command line, e.g. `make sft CONFIG=...`
CONFIG       ?= configs/sft_gemma_4_31b.yaml
DPO_CONFIG   ?= configs/dpo_gemma_4_31b.yaml
GRPO_CONFIG  ?= configs/grpo_gemma_4_31b.yaml
CHECKPOINT   ?= outputs/sdg-31b-dpo
HF_REPO      ?= solideogloria/sdg-31b-v0.1
TEACHER      ?= claude-opus-4-7
JUDGE        ?= claude-opus-4-7
DATA_OUT     ?= data/built
DATASET      ?= ../data/CAB_FF_v3_dataset.json
ROUNDS       ?= 3
BASE_CKPT    ?= outputs/sdg-31b-dpo
ITER_OUT     ?= outputs/sdg-31b-iter

help:
	@echo "CAB-FF Trainer — common tasks"
	@echo ""
	@echo "  SETUP"
	@echo "    make install        Install core (data pipeline only, no GPU)"
	@echo "    make gpu-install    Install GPU stack (Torch, TRL, PEFT, Liger)"
	@echo ""
	@echo "  DRY RUN (no GPU, no API key — ~3 min sanity check)"
	@echo "    make dry-run"
	@echo ""
	@echo "  BASIC PIPELINE"
	@echo "    make data           Generate SFT + DPO training data from CAB-FF"
	@echo "                          (uses TEACHER=$(TEACHER))"
	@echo "    make sft            SFT  (default: $(CONFIG))"
	@echo "    make dpo            DPO with SimPO loss"
	@echo "    make eval           Run CAB-FF on CHECKPOINT=$(CHECKPOINT)"
	@echo "    make gate           Compare CHECKPOINT to base, gate promotion"
	@echo "    make quantize       AWQ INT4 + GGUF Q4_K_M from CHECKPOINT"
	@echo "    make publish        Push CHECKPOINT to HF Hub"
	@echo ""
	@echo "  GROWTH-HACK TARGETS (see IMPROVEMENTS.md)"
	@echo "    make iterate        Multi-round refinement (ROUNDS=$(ROUNDS))"
	@echo "                          targets weakest dim/axis each round"
	@echo "    make best-of-n      Best-of-N rejection sampling -> SFT data"
	@echo "    make drilldown      Per-dimension/axis drilldown of a report"
	@echo "    make grpo           Online RL with CAB-FF reward (most expensive)"
	@echo ""
	@echo "  Override base model:"
	@echo "    make sft CONFIG=configs/sft_gemma_4_e4b.yaml      # consumer GPU"
	@echo "    make sft CONFIG=configs/sft_qwen3_6_27b.yaml      # Qwen alternative"
	@echo "    make sft CONFIG=configs/sft_deepseek_v4_flash.yaml # frontier MoE (4-8x H100)"
	@echo "    make sft CONFIG=configs/sft_glm_5_1.yaml           # frontier agentic"
	@echo "    make sft CONFIG=configs/sft_kimi_k2_6.yaml         # frontier reasoning"

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

iterate:
	python -m trainer.train.iterate \
	    --base-checkpoint $(BASE_CKPT) \
	    --rounds $(ROUNDS) \
	    --min-delta 2.0 \
	    --out $(ITER_OUT) \
	    --dataset $(DATASET) \
	    --teacher $(TEACHER) \
	    --judge $(JUDGE)

best-of-n:
	python -m trainer.train.best_of_n \
	    --checkpoint $(CHECKPOINT) \
	    --prompts-file $(DATA_OUT)/grpo_prompts.jsonl \
	    --rollouts 8 --top-k 1 \
	    --judge $(JUDGE) \
	    --out $(DATA_OUT)/bon_top1.jsonl

eval:
	python -m trainer.eval.run_cab_ff \
	    --checkpoint $(CHECKPOINT) \
	    --dataset $(DATASET) \
	    --judge $(JUDGE) \
	    --out $(CHECKPOINT)/cab_ff_report.json

drilldown:
	python -m trainer.eval.per_dimension_drilldown \
	    --report $(CHECKPOINT)/cab_ff_report.json

gate:
	python -m trainer.eval.gating \
	    --checkpoint-report $(CHECKPOINT)/cab_ff_report.json \
	    --baseline-report baselines/gemma_4_31b_base_report.json

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
