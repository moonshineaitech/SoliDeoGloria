#!/usr/bin/env bash
# Serve a CAB-FF-trained checkpoint via vLLM's OpenAI-compatible server.
#
# Usage:
#   ./vllm_serve.sh outputs/sdg-27b-dpo/merged           # serve BF16
#   ./vllm_serve.sh outputs/sdg-27b-dpo/awq              # serve AWQ INT4
#   ./vllm_serve.sh solideogloria/sdg-27b-v0.1           # serve from HF Hub
#
# Then run CAB-FF eval against it:
#   python -m trainer.eval.run_cab_ff --backend vllm --checkpoint <model-id>

set -euo pipefail

MODEL="${1:?Pass a checkpoint dir or HF Hub repo id}"
PORT="${PORT:-8000}"
DTYPE="${DTYPE:-auto}"
MAX_LEN="${MAX_LEN:-8192}"
GPU_MEM="${GPU_MEM:-0.9}"
EXTRA_ARGS="${EXTRA_ARGS:-}"

# Auto-detect AWQ quantization
QUANT_FLAG=""
if [[ -d "$MODEL" && -f "$MODEL/quant_config.json" ]] || [[ "$MODEL" == *awq* ]]; then
  QUANT_FLAG="--quantization awq"
fi

echo "[vllm] serving $MODEL on port $PORT"
exec python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --port "$PORT" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_LEN" \
  --gpu-memory-utilization "$GPU_MEM" \
  --trust-remote-code \
  --enable-prefix-caching \
  $QUANT_FLAG \
  $EXTRA_ARGS
