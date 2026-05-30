# Build your Christian AI model TODAY — idiot-proof guide

This is the no-prior-experience, copy-paste guide to going from nothing
to a published, downloadable, Christian-aligned LLM **today**.

> **Want zero infra — no GPU rental, no CLI?** See
> **[`AUTOTRAIN.md`](AUTOTRAIN.md)** instead: generate the data once (no
> GPU), then upload two files to HuggingFace AutoTrain and click Train.
> The three paths below give a better score, but AutoTrain is the easiest.

There are three paths. Pick ONE based on your budget. All three produce
a real, usable, shareable model.

| Path | Model | GPU | Time | Total cost | Result |
|------|-------|-----|------|-----------|--------|
| **A — Cheapest** | Gemma 4 E4B | 1× RTX 4090 | ~3-4 hr | **~$10-20** | Runs on a laptop/phone, Ollama-ready |
| **B — Recommended** | Gemma 4 31B | 1× H100 | ~6-10 hr | **~$70-150** | Production-grade, runs on a 4090 after quantizing |
| **C — Best money can buy** | GLM-5.1 / Kimi K2.6 | 8-16× H100 | ~12-24 hr | **~$600-900** | Frontier quality, needs a cluster |

**Recommendation: do Path A first (it's basically free and proves the
whole thing works end-to-end), then do Path B once you trust it.**

Before you spend a cent, see the exact numbers for your choice:

```bash
python -m trainer.scripts.cost_estimate --all-presets
```

---

## What you need before starting (5 minutes)

1. **A credit card** for the GPU rental and API usage.
2. **An Anthropic API key** (teacher for data generation).
   - Go to https://console.anthropic.com → API Keys → Create Key.
   - Put ~$30 of credit on it (Settings → Billing). For Path A you can
     use a cheaper teacher and spend ~$3.
   - (Or an OpenAI key from https://platform.openai.com/api-keys —
     either works.)
3. **A Hugging Face account + token** (to download Gemma and publish your
   model).
   - https://huggingface.co/join → then https://huggingface.co/settings/tokens
     → New token → type "Write".
4. **Accept the Gemma 4 license** (one click, free):
   - Visit https://huggingface.co/google/gemma-4-31b (or `-e4b` for Path A)
     → click "Acknowledge license".

That's everything. Now pick your path.

---

# PATH A — Cheapest (~$10-20, ~4 hours)

Trains **Gemma 4 E4B** on a single RTX 4090. The result runs on a laptop
via Ollama. This is the "prove it works without spending real money" path.

### A1. Rent the GPU (RunPod, ~$0.44/hr)

1. Go to https://runpod.io → sign up → add $15 of credit.
2. Click **Deploy** → **Pods** → pick **RTX 4090**.
3. For the template, choose **"RunPod PyTorch 2.4"** (or any CUDA 12.4+
   PyTorch image).
4. Set **Container Disk** to **80 GB** and **Volume Disk** to **40 GB**.
5. Click **Deploy**. Wait ~60 seconds. Click **Connect → Start Web
   Terminal** (or use SSH).

### A2. Set up (copy-paste this whole block)

```bash
# Clone the repo
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer

# Install everything
pip install -e ".[gpu,teachers,eval,deploy]"
pip install flash-attn==2.7.0 --no-build-isolation
pip install liger-kernel

# Paste YOUR keys here (replace the ... parts)
export ANTHROPIC_API_KEY=sk-ant-...        # or use OPENAI_API_KEY
export HF_TOKEN=hf_...
huggingface-cli login --token $HF_TOKEN
```

### A3. Preflight — catch problems before spending money

```bash
python -m trainer.scripts.preflight --config configs/sft_gemma_4_e4b.yaml \
    --min-vram-gb 16 --min-disk-gb 60
```

If it says **PREFLIGHT PASSED** (or OK with warnings), continue. If it
says **FAILED**, fix the blockers it lists — they're each one command.

### A4. Build the model (one command, cheap teacher)

```bash
CONFIG=configs/sft_gemma_4_e4b.yaml \
DPO_CONFIG=configs/dpo_gemma_4_31b.yaml \
TEACHER=gpt-4o-mini \
JUDGE=gpt-4o \
SKIP_ITERATE=1 \
./scripts/run_all.sh
```

(We use the cheap `gpt-4o-mini` teacher and skip the iterate loop to keep
Path A under $20. Set `OPENAI_API_KEY` instead of Anthropic if using
gpt-4o-mini.)

This runs: preflight → data generation → SFT → DPO → eval → quantize.
Watch it. It takes ~3-4 hours. **If the pod dies, just re-run the exact
same command** — it skips finished stages.

### A5. Get your model out (do this BEFORE you stop the pod!)

```bash
# Publish to Hugging Face (recommended — then you can delete the pod)
python -m trainer.deploy.push_to_hub \
    --checkpoint outputs/sdg-31b-dpo \
    --repo YOUR_HF_USERNAME/sdg-e4b-v0.1 \
    --eval-report outputs/sdg-31b-dpo/cab_ff_report.json
```

### A6. Run it on your own laptop (Ollama)

On your laptop (not the pod):

```bash
# Install Ollama from https://ollama.com, then:
ollama run hf.co/YOUR_HF_USERNAME/sdg-e4b-v0.1
```

### A7. STOP THE POD

Go back to RunPod → your pod → **Terminate**. **Do this or you keep
paying.** (~$0.44/hr adds up.)

**Total for Path A: ~$2 GPU + ~$3 teacher + ~$6 judge = ~$10-15.**

---

# PATH B — Recommended (~$70-150, ~6-10 hours)

Trains **Gemma 4 31B Dense** on a single H100. Production-grade. This is
the model you'd actually deploy for a ministry or product.

### B1. Rent the GPU (RunPod H100, ~$2.49/hr)

1. https://runpod.io → **Deploy → Pods → H100 PCIe 80GB**.
2. Template: **RunPod PyTorch 2.4** (CUDA 12.4+).
3. **Container Disk: 100 GB**, **Volume Disk: 200 GB** (the 31B base +
   checkpoints are big).
4. **IMPORTANT:** mount the Volume at `/workspace` so it persists if the
   pod restarts.
5. Deploy → Connect → Web Terminal.

### B2. Set up

```bash
cd /workspace
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer

pip install -e ".[gpu,teachers,eval,deploy]"
pip install flash-attn==2.7.0 --no-build-isolation
pip install liger-kernel

export ANTHROPIC_API_KEY=sk-ant-...
export HF_TOKEN=hf_...
huggingface-cli login --token $HF_TOKEN
```

### B3. Preflight

```bash
python -m trainer.scripts.preflight --config configs/sft_gemma_4_31b.yaml
```

Must say **PASSED** (or OK with warnings).

### B4. Build the model — the full pipeline with the iterate growth-hack

```bash
OUTPUT_DIR=/workspace/outputs \
./scripts/run_all.sh
```

Defaults to Gemma 4 31B, Claude Opus teacher/judge, 3 iterate rounds.
This is the highest-quality path. Takes ~6-10 hours. Re-runnable if
interrupted (uses `/workspace` persistent storage).

**Cheaper variant** (cuts teacher cost ~5x, slightly lower quality):

```bash
OUTPUT_DIR=/workspace/outputs \
TEACHER=gpt-4o JUDGE=gpt-4o ROUNDS=2 \
./scripts/run_all.sh
```

### B5. Publish (BEFORE stopping the pod)

```bash
python -m trainer.deploy.push_to_hub \
    --checkpoint /workspace/outputs/sdg-iter/final \
    --repo YOUR_HF_USERNAME/sdg-31b-v0.1 \
    --eval-report /workspace/outputs/sdg-iter/final/cab_ff_report.json
```

### B6. Look at your scores

```bash
python -m trainer.eval.per_dimension_drilldown \
    --report /workspace/outputs/sdg-iter/final/cab_ff_report.json
```

A CAB-FF score of **75+** is state-of-the-art Christian AI. **80+**
exceeds any known closed model.

### B7. TERMINATE THE POD.

**Total for Path B: ~$25 GPU + ~$40-250 teacher (depends on teacher
choice) + ~$30-60 judge = ~$70-340.** Use the GPT-4o variant in B4 to
land near $70.

---

# PATH C — Best money can buy (~$600-900, ~12-24 hours)

Trains a frontier MoE (GLM-5.1 or Kimi K2.6). Only do this if you have a
real budget and want the absolute best. Requires a multi-GPU cluster.

### C1. Rent a cluster

- RunPod / Lambda / Coreweave → **8× H100 80GB** (for GLM-5.1) or
  **16× H100** (for Kimi K2.6).
- Same PyTorch image, **500 GB+ volume**.

### C2-C5. Same as Path B but:

```bash
OUTPUT_DIR=/workspace/outputs \
CONFIG=configs/sft_glm_5_1.yaml \
DPO_CONFIG=configs/dpo_gemma_4_31b.yaml \
SKIP_ITERATE=1 \
./scripts/run_all.sh
```

(The frontier configs use DeepSpeed ZeRO-3; the run_all script handles
the launch. Iterate is skipped because each round is very expensive at
this scale.)

**Total for Path C: ~$565 GPU + ~$280 teacher + ~$36 judge = ~$880.**

---

# Even cheaper: the FREE Google Colab path (Path A-zero)

If you have **zero** budget for GPU rental, you can train Gemma 4 E4B on
a free Colab T4 (slower, smaller data):

1. Go to https://colab.research.google.com → New Notebook.
2. Runtime → Change runtime type → **T4 GPU**.
3. In a cell:

```python
!git clone https://github.com/moonshineaitech/SoliDeoGloria
%cd SoliDeoGloria/trainer
!pip install -e ".[gpu,teachers,eval,deploy]" -q
import os
os.environ["OPENAI_API_KEY"] = "sk-..."   # ~$3 of gpt-4o-mini
os.environ["HF_TOKEN"] = "hf_..."
!python -m trainer.scripts.preflight --config configs/sft_gemma_4_e4b.yaml --min-vram-gb 14 --min-disk-gb 40
!CONFIG=configs/sft_gemma_4_e4b.yaml TEACHER=gpt-4o-mini JUDGE=gpt-4o-mini SKIP_ITERATE=1 ./scripts/run_all.sh
```

Free Colab disconnects after a few hours; the run_all resume markers let
you reconnect and continue. **Total: ~$3-6 (API only, GPU is free).**
The result is lower quality than the paid paths but it's a real model.

---

# Troubleshooting

| Symptom | Fix |
|---|---|
| `CUDA out of memory` | Use a smaller base (E4B) or add `per_device_train_batch_size: 1` to the config. |
| `403 / cannot access google/gemma-4-31b` | You didn't accept the license. Visit the HF model page and click acknowledge. |
| `flash-attn` install fails | Skip it — `pip install` without it. Training is ~2x slower but works. |
| Pod died mid-run | Re-run the SAME `./scripts/run_all.sh` command. It resumes from the last finished stage (if OUTPUT_DIR is on persistent storage). |
| Teacher API "rate limit" | Add more credit, or use a cheaper teacher: `TEACHER=gpt-4o-mini`. |
| `make data` is slow | Normal — it's calling the teacher LLM thousands of times. ~30-60 min. |
| Score didn't beat base | Run more iterate rounds (`ROUNDS=4`), or read `IMPROVEMENTS.md` section A for the pitfall checklist. |

# What you end up with

- A model on Hugging Face under your username (e.g.
  `you/sdg-31b-v0.1`) with a full model card and CAB-FF eval report.
- GGUF files for Ollama / llama.cpp (runs on consumer hardware).
- An AWQ INT4 version for fast vLLM serving.
- A reproducible recipe anyone can verify.

# The honest caveats

- **You're paying for compute and API calls, not us.** All costs above
  are yours, on your own accounts.
- **First runs rarely hit the best score.** Budget for 1-2 retries while
  you learn the knobs. The cost estimates include a buffer note for this.
- **Quantized models score slightly lower** than the full model. Always
  re-run `make eval` on the quantized version before trusting its score.
- **This is a tool, not magic.** A good model still needs your judgment
  about where and how to deploy it. Don't put it in front of vulnerable
  people without human oversight.

> *Soli Deo Gloria.*
