# SoliDeoGloria v2 — the whole run, one page

Three Colab notebooks + Together. Do the steps in order. Total cost ≈ **$40-110**.

| # | Step | Tool | Output | Cost |
|---|------|------|--------|------|
| 1 | Make SFT data | `make_data_simple.ipynb` | `train.jsonl` + `eval.jsonl` | ~$10-40 (data-gen API) |
| 2 | SFT train | Together | your SFT model | ~$15-30 |
| 3 | Make DPO data | `make_dpo_data.ipynb` | `dpo_train.jsonl` | ~$8-25 |
| 4 | DPO train | Together | your final model | ~$10-20 |
| 5 | Eval | `eval_model.ipynb` | a score | ~$2-5 |
| 6 | Local (optional) | gguf-my-repo | GGUF for LM Studio | free |

---

## STEP 1 — SFT data (`make_data_simple.ipynb`)
Paste key → pick model (`deepseek-v4-pro`, or `claude-sonnet-4-6`) → Run all → download `train.jsonl` + `eval.jsonl`.

## STEP 2 — SFT on Together
New fine-tuning job:
- Source: **From base model**
- Base model: **`google/gemma-4-31B-it`** (dense — best for quality)
  - *MoE option:* `google/gemma-4-26B-A4B-it` (cheaper to serve; if a "target modules" field shows, set **attention-only**)
- Training file `train.jsonl`, validation `eval.jsonl`
- Training type **LoRA**, method **SFT**
- **Epochs 3** · **LR 1e-4** · scheduler cosine · **warmup 0.03** · **max seq len 2048** · packing on
- Checkpoints **3**, Evaluations **3** (watch val loss drop each epoch)
- LoRA rank/alpha (if shown): **32 / 64**
- HF output repo: `moonshineai/solideo-gemma31b-v2`
- HF token: your **Write** token → **Start**

## STEP 3 — DPO data (`make_dpo_data.ipynb`)
Run after SFT finishes. Same key/model → download `dpo_train.jsonl`.

## STEP 4 — DPO on Together
New job:
- Source: **From previous run** → pick your **SFT** model from Step 2
- Training method: **DPO**
- Training file: **`dpo_train.jsonl`**
- **LR 5e-7** · **Epochs 1**
- HF output repo: `moonshineai/solideo-gemma31b-v2-dpo` → **Start**

This is the alignment layer — teaches "don't drift, don't cave." Biggest quality jump after SFT.

## STEP 5 — Eval (`eval_model.ipynb`)
Run it on the **base** model and your **final** model; compare the faithfulness scores. Higher = it worked.

## STEP 6 — Run it locally (optional)
1. On Together, **download the merged checkpoint** (or push to HF).
2. HF Spaces → **`gguf-my-repo`** → paste your model repo → quant **Q4_K_M**.
3. Search the new GGUF repo in **LM Studio** → download → chat.

---

## Order & tips
- **Do 1→2 first, test it, then 3→4.** Don't run everything blind — eval after SFT, then add DPO.
- **Teacher choice:** `deepseek-v4-pro` or `claude-sonnet-4-6` — both excellent; check the smoke-test sample and pick the one you like. You do **not** need Opus.
- **One model size in = same size out.** 31B in → 31B out. (No shrinking after the fact.)
- **Don't reuse GLM-5.1 here** — it can't run locally and costs 10-30×; the 31B is your deployable model.

*Soli Deo Gloria.*
