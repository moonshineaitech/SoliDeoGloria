#!/usr/bin/env bash
# run_all.sh — one command to build the whole model, with resume safety.
#
# Runs: preflight -> data -> sft -> dpo -> iterate -> eval -> gate ->
#       quantize -> (optional) publish.
#
# SPOT-INSTANCE SAFE: each stage writes a marker in $STATE_DIR when it
# completes. Re-running the script skips completed stages. If your cheap
# spot GPU gets reclaimed mid-run, just re-run the exact same command on
# a fresh box (with the same OUTPUT_DIR on persistent storage) and it
# picks up where it left off.
#
# Usage:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   export HF_TOKEN=hf_...
#   ./scripts/run_all.sh                          # default: Gemma 4 31B
#   CONFIG=configs/sft_gemma_4_e4b.yaml ./scripts/run_all.sh   # cheap path
#   PUBLISH=1 HF_REPO=you/sdg-31b-v0.1 ./scripts/run_all.sh    # also publish
#
# Override anything via env: CONFIG, DPO_CONFIG, TEACHER, JUDGE, ROUNDS,
# DATASET, OUTPUT_DIR, STATE_DIR, PUBLISH, HF_REPO.

set -euo pipefail
cd "$(dirname "$0")/.."          # trainer/

# ---- config (override via env) ----
CONFIG="${CONFIG:-configs/sft_gemma_4_31b.yaml}"
DPO_CONFIG="${DPO_CONFIG:-configs/dpo_gemma_4_31b.yaml}"
TEACHER="${TEACHER:-claude-opus-4-7}"
JUDGE="${JUDGE:-claude-opus-4-7}"
ROUNDS="${ROUNDS:-3}"
DATASET="${DATASET:-../data/CAB_FF_v3_dataset.json}"
DATA_OUT="${DATA_OUT:-data/built}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs}"
STATE_DIR="${STATE_DIR:-${OUTPUT_DIR}/.state}"
PUBLISH="${PUBLISH:-0}"
HF_REPO="${HF_REPO:-solideogloria/sdg-31b-v0.1}"
SKIP_ITERATE="${SKIP_ITERATE:-0}"

mkdir -p "$STATE_DIR"

stage_done() { [[ -f "$STATE_DIR/$1.done" ]]; }
mark_done()  { touch "$STATE_DIR/$1.done"; }

banner() {
  echo ""
  echo "============================================================"
  echo "  $1"
  echo "============================================================"
}

run_stage() {
  local name="$1"; shift
  if stage_done "$name"; then
    echo ">> [skip] $name already complete (delete $STATE_DIR/$name.done to redo)"
    return 0
  fi
  banner "STAGE: $name"
  "$@"
  mark_done "$name"
  echo ">> [ok] $name complete"
}

# ---- 0. preflight (always runs; never marked done) ----
banner "PREFLIGHT"
python -m trainer.scripts.preflight --config "$CONFIG" || {
  echo "Preflight failed. Fix the blockers above before continuing." >&2
  exit 1
}

# ---- 1. data ----
run_stage data \
  python -m trainer.data.pipeline.cli build \
    --dataset "$DATASET" --teacher "$TEACHER" --out "$DATA_OUT"

# ---- 2. SFT ----
run_stage sft \
  python -m trainer.train.sft --config "$CONFIG" --data-dir "$DATA_OUT"

# Derive the SFT output dir from the config
SFT_OUT="$(python -c "import yaml,sys; print(yaml.safe_load(open('$CONFIG'))['training']['output_dir'])")"

# ---- 3. DPO ----
run_stage dpo \
  python -m trainer.train.dpo --config "$DPO_CONFIG" --data-dir "$DATA_OUT"

DPO_OUT="$(python -c "import yaml,sys; print(yaml.safe_load(open('$DPO_CONFIG'))['training']['output_dir'])")"
FINAL_CKPT="$DPO_OUT"

# ---- 4. iterate (optional, the growth-hack loop) ----
if [[ "$SKIP_ITERATE" != "1" ]]; then
  run_stage iterate \
    python -m trainer.train.iterate \
      --base-checkpoint "$DPO_OUT" --rounds "$ROUNDS" --min-delta 2.0 \
      --out "${OUTPUT_DIR}/sdg-iter" --dataset "$DATASET" \
      --teacher "$TEACHER" --judge "$JUDGE"
  # iterate symlinks its best checkpoint to <out>/final
  if [[ -e "${OUTPUT_DIR}/sdg-iter/final" ]]; then
    FINAL_CKPT="${OUTPUT_DIR}/sdg-iter/final"
  fi
fi

# ---- 5. eval ----
run_stage eval \
  python -m trainer.eval.run_cab_ff \
    --checkpoint "$FINAL_CKPT" --dataset "$DATASET" --judge "$JUDGE" \
    --out "$FINAL_CKPT/cab_ff_report.json"

# ---- 6. gate ----
banner "STAGE: gate (promote-or-reject)"
if python -m trainer.eval.gating \
    --checkpoint-report "$FINAL_CKPT/cab_ff_report.json" \
    --baseline-report "baselines/$(basename "$CONFIG" .yaml)_base_report.json" 2>/dev/null; then
  echo ">> [ok] gate PASSED — model is an improvement over base."
  mark_done gate
else
  echo ">> [warn] gate did not pass (or no baseline report present)."
  echo "          Review $FINAL_CKPT/cab_ff_report.json and IMPROVEMENTS.md."
fi

# ---- 7. quantize ----
run_stage quantize \
  bash -c "python -m trainer.deploy.quantize_awq --checkpoint '$FINAL_CKPT' && \
           python -m trainer.deploy.quantize_gguf --checkpoint '$FINAL_CKPT' --quants Q4_K_M Q5_K_M || \
           echo 'quantize step needs autoawq/llama.cpp; see deploy/ docs'"

# ---- 8. publish (opt-in) ----
if [[ "$PUBLISH" == "1" ]]; then
  run_stage publish \
    python -m trainer.deploy.push_to_hub \
      --checkpoint "$FINAL_CKPT" --repo "$HF_REPO" \
      --eval-report "$FINAL_CKPT/cab_ff_report.json"
fi

banner "DONE"
echo "Final checkpoint: $FINAL_CKPT"
echo "Eval report:      $FINAL_CKPT/cab_ff_report.json"
echo ""
echo "Serve it:   bash trainer/deploy/vllm_serve.sh $FINAL_CKPT/merged"
echo "Or Ollama:  see $FINAL_CKPT/gguf/ + trainer/deploy/make_ollama_modelfile.py"
[[ "$PUBLISH" == "1" ]] && echo "Published:  https://huggingface.co/$HF_REPO"
echo ""
