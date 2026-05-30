# No-code path: train on HuggingFace AutoTrain

Don't want to rent a GPU, write commands, or babysit a pod? You can train
the model entirely in a web UI. The only thing you run yourself is the
**data generation** step (no GPU — just API calls; a free Colab or your
laptop is fine). Then you upload two files and click Train.

> **Trade-off, stated honestly.** AutoTrain gives you plain LoRA SFT. You
> lose DoRA, NEFTune, the iterate loop, and CAB-FF gating — expect roughly
> **10-15 fewer CAB-FF points** than the full `./scripts/run_all.sh`
> pipeline. In exchange you never touch a GPU or a CLI flag. Good for a
> first model or a quick proof; use the full pipeline when you want the
> best score.

---

## Step 1 — Generate the data (no GPU, ~30-60 min, ~$30-50 API)

Run this anywhere — your laptop, or a free Google Colab CPU runtime. It
only calls the teacher LLM; it does **not** need a GPU.

```bash
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer
pip install -e ".[teachers]"

export ANTHROPIC_API_KEY=sk-ant-...     # or OPENAI_API_KEY + TEACHER=gpt-4o
make data
```

When it finishes, you'll have these files in `trainer/data/built/`:

| File | What it is | Upload to AutoTrain? |
|------|-----------|----------------------|
| **`train.jsonl`** | SFT training examples | ✅ **yes** (training file) |
| **`eval.jsonl`** | SFT held-out examples | ✅ **yes** (validation file) |
| `pref_train.jsonl` | DPO preference pairs | only for a separate DPO run (Step 4) |
| `pref_eval.jsonl` | DPO held-out pairs | only for a separate DPO run |
| `grpo_prompts.jsonl` | RL prompts | ignore (full pipeline only) |

Download `train.jsonl` and `eval.jsonl` to your computer. That's all you
need for the no-code path.

### The file format (so you know what you're uploading)

`train.jsonl` / `eval.jsonl` — one JSON object per line, chat format:

```json
{"messages": [{"role": "user", "content": "What does the Westminster Shorter Catechism say is the chief end of man?"}, {"role": "assistant", "content": "The Westminster Shorter Catechism answers..."}], "meta": {"source": "synth_cab_ff_v1", "dimension": "...", "tradition": "..."}}
```

AutoTrain reads the **`messages`** column and ignores `meta`. If a future
AutoTrain version complains about the extra column, strip it with:

```bash
python -c "import json,sys; [print(json.dumps({'messages':json.loads(l)['messages']})) for l in open('data/built/train.jsonl')]" > train_clean.jsonl
```

---

## Step 2 — Train in the AutoTrain UI (no code, ~$20-30)

1. Go to **https://huggingface.co/autotrain** → **Create new project**.
2. Task: **LLM Fine-tuning → SFT**.
3. Base model: **`google/gemma-4-31b`**
   (for the cheap path use **`google/gemma-4-e4b`** — trains far faster).
   - First accept the license at the model page if you haven't:
     https://huggingface.co/google/gemma-4-31b → "Acknowledge license".
4. **Upload data** → drag in `train.jsonl` (training) and `eval.jsonl`
   (validation).
5. **Column mapping**: set the chat/messages column to **`messages`**
   (AutoTrain usually auto-detects this for chat-format JSONL).
6. **Parameters** — these are sane starting values:

   | Field | Value | Why |
   |-------|-------|-----|
   | PEFT / Use LoRA | **on** | full FT on 31B is too expensive |
   | LoRA r (rank) | **64** | good quality/cost balance |
   | LoRA alpha | **128** | conventional 2× rank |
   | LoRA dropout | **0.05** | |
   | Epochs | **2** | 3 if your data is small (<10k) |
   | Learning rate | **2e-4** | standard for LoRA |
   | Batch size | **auto** / 1-2 | let AutoTrain pick for the GPU |
   | Mixed precision | **bf16** | |
   | Max seq length | **2048** | covers our examples |

7. Pick the hardware (AutoTrain offers a managed GPU — an A100/H100 tier
   for the 31B, a smaller tier for E4B) and click **Start training**.
8. When it's done, the adapter (or merged model) lands on **your** HF
   account, e.g. `your-username/sdg-31b-v0.1`. It's ready to download or
   serve.

---

## Step 3 — Check whether it actually got better (recommended)

AutoTrain won't run CAB-FF for you, and scoring the model means the model
has to be **running** somewhere. Two no-fuss options:

**Option 1 — HF Inference Endpoint (no GPU of your own).** On your HF
model page click **Deploy → Inference Endpoints**, spin up a GPU endpoint
(paid by the hour — terminate it when done). It exposes an
OpenAI-compatible URL. Then from any machine:

```bash
cd SoliDeoGloria/trainer
pip install -e ".[eval]"
export ANTHROPIC_API_KEY=sk-ant-...     # the JUDGE key
python -m trainer.eval.run_cab_ff \
    --backend vllm \
    --vllm-endpoint https://YOUR-ENDPOINT.endpoints.huggingface.cloud/v1 \
    --checkpoint your-username/sdg-31b-v0.1 \
    --dataset ../data/CAB_FF_v3_dataset.json \
    --judge claude-opus-4-7 \
    --out report.json
```

**Option 2 — load it directly (needs a GPU box).** Same command but
`--backend transformers --checkpoint your-username/sdg-31b-v0.1` and drop
the `--vllm-endpoint`. This downloads and runs the model locally.

A CAB-FF score above the Gemma 4 31B base means the fine-tune helped. See
the numbers per dimension:

```bash
python -m trainer.eval.per_dimension_drilldown --report report.json
```

---

## Step 4 (optional) — Add a DPO pass

AutoTrain also supports DPO. To squeeze out more, run a second AutoTrain
project:

- Task: **LLM Fine-tuning → DPO**
- Base model: **your SFT output** from Step 2 (not the original Gemma)
- Upload `pref_train.jsonl` / `pref_eval.jsonl`
- Column mapping: `prompt`, `chosen`, `rejected` (these are the keys in
  the file)
- Lower the learning rate (e.g. **5e-6**) and run **1 epoch**.

---

## Other no-code services (same idea, different UI)

If you'd rather not use AutoTrain, these take the same `train.jsonl` and
also train without code:

| Service | URL | Notes |
|---------|-----|-------|
| **Together AI** | together.ai/fine-tuning | Pay-per-token, simple uploader |
| **OpenPipe** | openpipe.ai | Cleanest UI, built for exactly this |
| **Unsloth Cloud** | cloud.unsloth.ai | Gemma-optimized, cheap |

All of them want the same conversational `messages` JSONL you produced in
Step 1, and all of them skip DoRA/NEFTune/iterate the same way AutoTrain
does. The data-generation step is the part only this repo can do for you.

> *Soli Deo Gloria.*
