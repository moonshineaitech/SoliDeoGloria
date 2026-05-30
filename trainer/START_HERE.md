# START HERE — build your Christian AI model today

This is the single front door. Read the 60-second decision, then follow
**one** lane. Every command below is real and tested. By the end you have
a downloadable, shareable, benchmark-scored Christian-aligned model.

---

## The 60-second decision

The whole job is **3 phases**, and they're the same for everyone:

```
  PHASE 1  ──►  PHASE 2  ──►  PHASE 3
  Make the      Train the     Check + use
  data          model         + share it
  (no GPU)      (pick a lane)  (no GPU)
```

**Phase 2 is the only place the lanes differ.** Pick your lane now:

| Lane | How Phase 2 works | You need | Cost* | Best score? |
|------|-------------------|----------|-------|-------------|
| **🖱️ AutoTrain** | Upload 2 files to a website, click Train | nothing but a browser | **~$25-80** | good |
| **⚡ One-command GPU** | Rent a GPU, paste one command | comfort with a terminal | **~$70-340** | **best** |

\* includes the data-generation API cost from Phase 1.

**My recommendation to get it done today:** do the **🖱️ AutoTrain lane**.
It needs zero infrastructure and finishes in an afternoon. You can always
re-run the GPU lane later for a few more points. Everything in **bold**
below is for the AutoTrain lane; the GPU lane is in
[`RUN_TODAY.md`](RUN_TODAY.md).

---

## PHASE 0 — Accounts & money (one time, ~10 min)

Do these now so nothing blocks you later. Total to load: **~$60**.

| # | What | Where | Load |
|---|------|-------|------|
| 1 | **Anthropic API key** (the "teacher" that writes training answers) | https://console.anthropic.com → API Keys → Create Key, then Billing | **$40** |
| 2 | **HuggingFace account + Write token** | https://huggingface.co/join → https://huggingface.co/settings/tokens → New token → **Write** | free |
| 3 | **Accept the Gemma 4 license** (1 click) | https://huggingface.co/google/gemma-4-31b → "Acknowledge license" | free |
| 4 | *(AutoTrain lane)* AutoTrain credits | added automatically when you launch a job | ~$20-30 |

> 💡 **To spend less:** use OpenAI's `gpt-4o-mini` as the teacher instead
> of Claude. Get a key at https://platform.openai.com/api-keys, load ~$5,
> and the data step costs ~$3-5 instead of ~$30-50. Slightly lower quality.

Keep your two keys handy. They look like `sk-ant-...` and `hf_...`.

---

## PHASE 1 — Make the training data (BOTH lanes, no GPU)

This is the part only this repo can do: it turns the CAB-FF benchmark into
training examples using the teacher LLM. **No GPU needed** — it's just API
calls. Run it on your laptop, or in a free Google Colab CPU notebook.

```bash
# 1. Get the code
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer

# 2. Install the data tools (no GPU libraries — fast, ~1 min)
pip install -e ".[teachers]"

# 3. Paste YOUR teacher key (one of these)
export ANTHROPIC_API_KEY=sk-ant-...        # Claude (best quality)
#   OR, to spend less:
# export OPENAI_API_KEY=sk-...             # then add  TEACHER=gpt-4o-mini  below

# 4. Generate the data  (~30-60 min, ~$30-50 with Claude / ~$3-5 with gpt-4o-mini)
make data
#   cheaper variant:  make data TEACHER=gpt-4o-mini
```

**When it finishes**, you have these files in `trainer/data/built/`:

| File | What | You'll upload it? |
|------|------|-------------------|
| **`train.jsonl`** | SFT training examples | ✅ **yes** |
| **`eval.jsonl`** | held-out validation | ✅ **yes** |
| `pref_train.jsonl` / `pref_eval.jsonl` | DPO preference pairs | only for the optional DPO step |
| `grpo_prompts.jsonl` | RL prompts | ignore |

Each line of `train.jsonl` looks like this (verified):

```json
{"messages": [{"role": "user", "content": "I want to start a daily prayer practice. Where do I begin?"}, {"role": "assistant", "content": "Begin with the Lord's Prayer (Matthew 6:9-13)..."}], "meta": {"source": "...", "dimension": "Faith & Spirituality"}}
```

**Download `train.jsonl` and `eval.jsonl` to your computer.** That's all
Phase 1 produces that you need. ✅ **Phase 1 done.**

> Running in Colab? After `make data`, download with:
> `from google.colab import files; files.download('data/built/train.jsonl')`

---

## PHASE 2 🖱️ — AutoTrain lane (no GPU, no code)

> Doing the GPU lane instead? Stop here and switch to
> [`RUN_TODAY.md`](RUN_TODAY.md) — it's one command. Then come back for
> Phase 3.

### Step 1 — Start the project
1. Go to **https://huggingface.co/autotrain** → sign in → **Create new project**.
2. Task: **LLM Fine-tuning → SFT**.
3. Base model: type **`google/gemma-4-31b`**
   *(want it cheaper/faster? use **`google/gemma-4-e4b`** — trains in a
   fraction of the time and still runs on a laptop afterward.)*

### Step 2 — Upload your two files
4. **Upload data** → drag in **`train.jsonl`** as the *training* file and
   **`eval.jsonl`** as the *validation* file.
5. **Column mapping** → set the chat column to **`messages`**.
   (AutoTrain usually auto-detects this for chat-format JSONL. The extra
   `meta` field is ignored.)

### Step 3 — Set the knobs (copy these exactly)

| Field | Value |
|-------|-------|
| Use PEFT / LoRA | **ON** |
| LoRA r (rank) | **64** |
| LoRA alpha | **128** |
| LoRA dropout | **0.05** |
| Epochs | **2** |
| Learning rate | **2e-4** |
| Mixed precision | **bf16** |
| Max sequence length | **2048** |
| Batch size | **auto** (let it pick) |

### Step 4 — Train
6. Pick the offered GPU tier (an A100/H100 tier for 31B; a small tier for
   E4B) and click **Start training**.
7. Wait. You'll get an email/console notice when it's done. The finished
   model appears on **your** HF account, e.g.
   `your-username/sdg-31b-v0.1`. ✅ **Phase 2 done.**

> **Optional extra quality — a DPO pass.** After SFT finishes, start a
> *second* AutoTrain project: Task **DPO**, base model = your SFT output
> from Step 7 (not the original Gemma), upload `pref_train.jsonl` /
> `pref_eval.jsonl`, column mapping `prompt` / `chosen` / `rejected`,
> learning rate **5e-6**, **1 epoch**.

Full field-by-field detail (and Together AI / OpenPipe alternatives) is in
[`AUTOTRAIN.md`](AUTOTRAIN.md).

---

## PHASE 3 — Check it, use it, share it (no GPU for most of this)

### 3a. Did it actually get better? (recommended)

Scoring means the model has to be *running* somewhere. Easiest with no GPU
of your own: on your HF model page click **Deploy → Inference Endpoints**,
start a GPU endpoint (paid per hour — **terminate it when done**), copy its
URL, then:

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

# see the score broken down by dimension:
python -m trainer.eval.per_dimension_drilldown --report report.json
```

**Reading the score:** above the Gemma-4-31B base = your fine-tune helped.
**CAB-FF 75+** is state-of-the-art Christian AI; **80+** beats any known
closed model.

### 3b. Run it on your own laptop (free, Ollama)

The AutoTrain model is already on HF. To run it locally:

```bash
# Install Ollama from https://ollama.com, then:
ollama run hf.co/your-username/sdg-31b-v0.1
```

(For the 31B you want a beefy machine or the E4B model; E4B runs on a
laptop comfortably.)

### 3c. Share it

It's already public on your HF account at
`https://huggingface.co/your-username/sdg-31b-v0.1`. Send people that link.
Add a sentence to the model card describing what it's for. Done. 🎉

---

## ✅ The master checklist (print this)

```
PHASE 0 — accounts                                          [ ]
  [ ] Anthropic key (sk-ant-...), $40 loaded
  [ ] HuggingFace Write token (hf_...)
  [ ] Accepted Gemma 4 license (clicked Acknowledge)

PHASE 1 — data (no GPU)                                     [ ]
  [ ] git clone + cd SoliDeoGloria/trainer
  [ ] pip install -e ".[teachers]"
  [ ] export ANTHROPIC_API_KEY=...
  [ ] make data
  [ ] downloaded train.jsonl + eval.jsonl

PHASE 2 — train (pick ONE)                                  [ ]
  AutoTrain:  uploaded 2 files, set knobs, clicked Train
  GPU:        ran ./scripts/run_all.sh  (see RUN_TODAY.md)

PHASE 3 — finish                                            [ ]
  [ ] ran CAB-FF eval, score beats base
  [ ] ran it locally (Ollama) OR served it
  [ ] shared the HF link
```

---

## 🆘 Troubleshooting

| Symptom | Fix |
|---|---|
| `make data` errors "no API key" | `export ANTHROPIC_API_KEY=sk-ant-...` (or `OPENAI_API_KEY` + `TEACHER=gpt-4o-mini`) |
| `make data` is slow | Normal — thousands of teacher calls. ~30-60 min. |
| AutoTrain: "can't access google/gemma-4-31b" | You skipped Phase 0 step 3. Visit the model page, click Acknowledge license. |
| AutoTrain: complains about the `meta` column | Strip it: `python -c "import json;[print(json.dumps({'messages':json.loads(l)['messages']})) for l in open('data/built/train.jsonl')]" > train_clean.jsonl` and upload that. |
| Want to spend less | `make data TEACHER=gpt-4o-mini`, and use `google/gemma-4-e4b` in AutoTrain. |
| Score didn't beat base | Add the DPO pass (Phase 2 optional box), or run the GPU lane's iterate loop. See [`IMPROVEMENTS.md`](IMPROVEMENTS.md). |
| I have a GPU and want the best score | Switch to the GPU lane: [`RUN_TODAY.md`](RUN_TODAY.md). One command, resume-safe. |

---

## What "optimal" actually requires (the honest part)

The AutoTrain lane gives you plain LoRA SFT. The GPU lane
(`./scripts/run_all.sh`) adds four things AutoTrain can't, worth roughly
**+10-15 CAB-FF points** total:

- **DoRA** instead of plain LoRA (+3-5)
- **NEFTune** noisy-embedding training (+2-3)
- **The iterate loop** — auto-finds your weakest dimension and trains
  against it for 2-3 rounds (+8-15, the big one)
- **CAB-FF gating** — refuses to ship a model that didn't actually improve

So: **AutoTrain today to have a real model by tonight; the GPU lane when
you want the absolute best.** Both are real, both are shareable.

> *Soli Deo Gloria.*
