# Improvements: pitfalls and growth hacks

This is the most important doc in the trainer. The README tells you
*what* to run; this tells you *what will go wrong*, *how to detect it*,
and *what to do about it*.

Organized as:

- **A. Known pitfalls** — failure modes we've seen in the wild, with
  detection + mitigation
- **B. Growth hacks** — techniques that meaningfully lift CAB-FF scores
  beyond the baseline SFT+DPO pipeline
- **C. The iterative refinement protocol** — the practical loop the
  `make iterate` target implements
- **D. Quality benchmarks** — what numbers to expect at each stage

---

## A. Known pitfalls

### A1. Catastrophic forgetting of general capability

**Symptom:** SFT trained model scores +20 on CAB-FF Faith but drops 15
points on MMLU/HellaSwag/MT-Bench.

**Cause:** Training only on Christian-specific data overwrites general
instruction-following.

**Mitigations:**
1. **Mix general instruction data into SFT** (default 30% Tulu-3 in
   our blends). Don't reduce this below 25%.
2. **Use LoRA / DoRA, not full FT** — the frozen base preserves most
   general capability.
3. **Lower learning rate on the lm_head and embedding layers** — they
   carry general knowledge. Set `modules_to_save: []` (never train
   embeddings).
4. **Eval on a general benchmark each round** (MMLU subset is enough).
   Gate: general benchmark must not drop more than 3 points.

### A2. Mode collapse on DPO

**Symptom:** Loss looks great, but the model outputs are short,
formulaic, or repetitive after DPO.

**Cause:** Vanilla DPO can over-fit to length / surface features of
"chosen" responses rather than the substance.

**Mitigations:**
1. **Use SimPO loss** (`loss_type: simpo` in the DPO config) — length-
   normalized log-ratio.
2. **Cap chosen/rejected length ratio** at 2× in data generation.
3. **Monitor response diversity** — if eval responses across different
   prompts start using identical openers, dial back DPO epochs.
4. **Set beta high enough** (0.1 default; raise to 0.2 if overfitting,
   lower to 0.05 if not learning).

### A3. Judge bias contaminates the training signal

**Symptom:** Model scores well on CAB-FF with Judge A (Claude) but
poorly with Judge B (GPT-4). The model has learned to please Judge A's
stylistic preferences rather than the underlying behavior.

**Cause:** Single-judge optimization. Judges have stylistic preferences
(Claude likes thoroughness; GPT-4 likes structure) that leak through
DPO/GRPO.

**Mitigations:**
1. **Rotate judges across rounds.** Round 1 data uses Claude. Round 2
   uses GPT-4. Round 3 uses both ensembled.
2. **Use a different judge for final gating than for training.** If
   trained-against-Claude, gate-against-GPT-4.
3. **Add an explicit judge-bias penalty** in GRPO: reward = (rubric -
   stylistic_features_correlated_with_judge).
4. **Test cross-judge agreement** during eval (built into
   `eval/per_dimension_drilldown.py`).

### A4. LoRA on MoE bases blows up parameter count

**Symptom:** Training Kimi K2.6 with vanilla `target_modules:
[q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]` —
you get tens of billions of trainable parameters because there's a
LoRA per expert per layer.

**Cause:** Naïve target-module selection on MoE models replicates the
LoRA per expert.

**Mitigations:**
1. **Attention-only LoRA** on MoE: `target_modules: [q_proj, k_proj,
   v_proj, o_proj]`. This is the default in `sft_kimi_k2_6.yaml`,
   `sft_glm_5_1.yaml`, `sft_deepseek_v4_*.yaml`.
2. **Router LoRA** (advanced): train only the routing decision, not the
   experts. Most stable, but lower ceiling.
3. **DeepSpeed MoE expert sharding** when full-FT is needed.

### A5. Quantization quality regression

**Symptom:** Merged BF16 checkpoint scores CAB-FF 72. After AWQ INT4
quantization it scores 64.

**Cause:** Quantization is lossy; the loss is non-uniform across
prompts and disproportionately hits low-frequency, theologically
precise responses.

**Mitigations:**
1. **ALWAYS re-run CAB-FF on the quantized model** — never publish
   based on the BF16 score.
2. **Use AWQ over GPTQ for theological tasks** — AWQ's activation-
   aware quantization preserves rarely-activated experts better.
3. **Use Q5_K_M instead of Q4_K_M for GGUF** when CAB-FF Drift Index
   regresses by more than 5.
4. **Include theological-vocabulary calibration data**, not just
   PileVal default (option `--calib-samples` accepts a file of
   Christian-text shards).

### A6. Reward hacking on GRPO

**Symptom:** GRPO loss decreases monotonically, but the model starts
producing responses that are formulaic invocations of "the resurrection
hope" or "Christ alone" regardless of question.

**Cause:** The reward model (CAB-FF judge) gives easy-to-game high
scores to responses that contain certain keywords. The policy learns
to spam those keywords.

**Mitigations:**
1. **Add a diversity penalty** in GRPO — penalize n-gram overlap with
   recent rollouts.
2. **Cap the per-response reward** at the 90th percentile of base-model
   responses — prevents the policy from exploiting any single high-
   scoring template.
3. **Add an adversarial-judge term** — a second judge whose system
   prompt is "score how generic/templatey this response is" — and
   subtract from the reward.
4. **Use a "novelty bonus"** — small +reward for n-grams not seen in
   the last 1000 rollouts.

### A7. Tradition imbalance amplifies in training

**Symptom:** Cross-Tradition CAB-FF score improves +12, but Catholic
score regresses -3 and Pentecostal regresses -5.

**Cause:** The training data (and Tulu-3 general blend) over-represents
Western Protestant / evangelical voice. Without explicit balancing,
the model drifts toward that center of gravity.

**Mitigations:**
1. **Stratify data generation by tradition** with explicit weights
   from `data_mix.tradition_weights` in the SFT config.
2. **Per-tradition CAB-FF subscores** in the gating check — no tradition
   can regress by > 5 points.
3. **Tradition-specialist adapters** (see B3) — keep distinct LoRA
   adapters per tradition; merge at inference based on user signal.

### A8. Test-set contamination via Internet pretraining

**Symptom:** The base model already scores 60+ on CAB-FF before any
training — too high for an "untrained" baseline.

**Cause:** CAB-FF questions are public; large bases have seen them via
GitHub crawls.

**Mitigations:**
1. **Test for memorization** with the `--check-memorization` flag on
   `eval/run_cab_ff.py` — it runs each question without options and
   measures verbatim recall.
2. **Use the held-out 80-question hand-authored seed** (in
   `data/CAB_FF_v3_seed.json`) for final reporting; community-
   contributed banks of similar but novel questions can be used for
   training-time eval signal without contamination concern.
3. **Maintain a sealed evaluation set** (`data/CAB_FF_v3_sealed.json`,
   not currently published — recommend curating one per major release).

### A9. Synthetic-data style collapse

**Symptom:** All training answers start with the same 2-3 patterns
("Great question...", "This is a meaningful concern..."), because the
teacher LLM has a stylistic tic.

**Cause:** One teacher LLM, one prompt template.

**Mitigations:**
1. **Mix teachers** — generate 50% with Claude, 50% with GPT-4; the
   stylistic mixing alone helps.
2. **Multi-template prompt synthesis** — `stage_02.py` cycles through
   ~12 prompt templates; don't reduce below 6.
3. **Style stripping** — post-process to strip openers like "Great
   question," "Wonderful question," "This is a thoughtful question."
   (Implemented in `stage_06.py:_strip_stylistic_openers`.)

### A10. Refusal regression on safety-sensitive topics

**Symptom:** Trained model scores higher on CAB-FF Faith but starts
giving direct clinical/legal advice instead of referring to
professionals.

**Cause:** Christian-instruction training shifted the refusal
distribution toward "engage everything."

**Mitigations:**
1. **Include safety-positive examples** in SFT — scenarios where the
   correct answer IS a referral. CAB-FF's Health dimension has these;
   the trainer pulls them by default.
2. **Refusal-calibration axis is one of the 7 gating axes** —
   regression on it blocks promotion.
3. **Don't disable the base model's safety training** — never set
   `modules_to_save: [embed_tokens, lm_head]` because those carry the
   refusal calibration.

---

## B. Growth hacks

These are techniques that lift CAB-FF scores meaningfully beyond a
default SFT+DPO pipeline.

### B1. Iterative refinement (the biggest one)

**What it is:** Train, eval, identify weakest dimension/axis, generate
fresh data for that one dimension, train a small adapter delta, repeat.

**Why it works:** A single-shot training run optimizes the average. The
iterative loop optimizes for the *minimum* across dimensions — which is
what the geometric-mean composite scoring rewards.

**Implementation:** `make iterate ROUNDS=3` runs the loop. Each round:
1. Run CAB-FF on the current checkpoint
2. Identify the worst-scoring dimension and axis
3. Generate +500 targeted examples for that dimension (using the same
   stage_02 pipeline with a forced dimension filter)
4. Run a 1-epoch SFT delta (~30 min on H100)
5. Eval again; if CAB-FF composite improved by ≥ 2 points, keep going

Expected gain: **+8-15 CAB-FF points** over single-shot SFT+DPO on
the same compute budget.

### B2. Best-of-N rejection sampling → SFT (cheap RL)

**What it is:** For each prompt in the SFT set, generate N=8 rollouts
from the current model. Have the CAB-FF judge score each. Train SFT on
the top-1 response.

**Why it works:** Captures most of the gain from full GRPO at a small
fraction of the cost. The judge call is the same cost; the policy
training is just SFT.

**Implementation:** `python -m trainer.train.best_of_n
--checkpoint <ckpt> --rollouts 8 --top-k 1 --out new_sft_data.jsonl`.
Then SFT on the new data.

Expected gain: **+3-6 CAB-FF points** vs. plain SFT.

### B3. Tradition-specialist adapters

**What it is:** Train one general adapter (the SFT+DPO from the main
pipeline). Then train smaller per-tradition LoRAs on tradition-
specific data only. At inference, the user (or the application) signals
their tradition; the relevant tradition LoRA is loaded on top.

**Why it works:** A single model trying to be the best Reformed AND
Catholic AND Orthodox response is over-constrained. Specialist
adapters let each tradition's distinctives flourish without
compromising others.

**Implementation:**
```
make sft CONFIG=configs/sft_gemma_4_31b.yaml          # general
make sft CONFIG=configs/sft_specialist_catholic.yaml   # specialist
make sft CONFIG=configs/sft_specialist_reformed.yaml   # specialist
# ...
# At inference:
python -m trainer.deploy.tradition_adapter_merge \
    --base outputs/sdg-31b-dpo \
    --tradition catholic \
    --out outputs/sdg-31b-catholic-served
```

Expected gain: **+5-10 points per-tradition** on tradition-tagged
questions, with no regression on Cross-Tradition.

### B4. Hard-negative mining

**What it is:** Every time CAB-FF eval reveals an adversarial probe the
model failed (e.g., it said "higher power" when probed), add the prompt
to the next round of DPO with the failure response as `rejected` and a
hand-written or teacher-generated correct response as `chosen`.

**Why it works:** Targets the specific failure modes the current model
exhibits — denser learning signal per training token than random data.

**Implementation:** `python -m trainer.train.iterate
--mine-hard-negatives` — automatically extracts failed adversarial
probes from the latest eval report and rebuilds DPO data.

Expected gain: **+4-8 Drift Index points** (lower is better) per
round.

### B5. Christian-corpus DAPT (domain-adaptive pretraining)

**What it is:** Before SFT, do 1 epoch of continued pretraining on a
~500M-token Christian corpus (public-domain Scripture, confessions,
patristic writings, theological textbooks).

**Why it works:** Embeds the actual vocabulary, citation conventions,
and rhetorical patterns of Christian theology directly into the
weights, rather than relying on the SFT stage to teach them.

**Implementation:** `make cpt CONFIG=configs/cpt_<base>.yaml
CORPUS_DIR=data/built/05_corpus` — runs only when explicitly invoked
(it's expensive: ~4-8 hr on H100 for 9B; not recommended for 31B+).

Expected gain on E4B and smaller bases: **+10-15 CAB-FF Faith
dimension points**. Negligible on 27B+.

### B6. Tool-augmented training (Scripture verification)

**What it is:** Give the model a `look_up_scripture(book, chapter,
verse)` tool. Train it to call the tool whenever it cites Scripture,
then incorporate the lookup result.

**Why it works:** Solves the Scripture-fabrication problem at the
*architecture* level rather than relying on training to suppress it.

**Implementation:** This is a v2.0 feature; the trainer ships a
`tools/scripture_lookup.py` stub. Implementing the full tool-using
SFT pipeline (TRL's `ToolCallTrainer`) is on the roadmap.

Expected gain: **fabrication rate from ~5% to <0.5%** based on
external tool-use research.

### B7. Self-debate distillation

**What it is:** Have the SFT model take both sides of a contested
intra-Christian question (e.g., Catholic vs Reformed view on the
Eucharist). The model that produces the more substantive, charitable,
tradition-faithful debate becomes the SFT target.

**Why it works:** Forces the model to model multiple traditions
explicitly, producing data that improves Tradition Fairness.

**Implementation:** `python -m trainer.train.self_debate
--checkpoint <ckpt> --out data/built/debate.jsonl`. (v0.2 stub.)

Expected gain on Tradition Fairness axis: **+5-8 points**.

### B8. Multi-base ensemble teacher distillation

**What it is:** Don't use one teacher LLM for synthetic data. Use 3-4
(Claude Opus 4.7, GPT-4o, Gemini 2.0 Pro, DeepSeek V4-Pro hosted
inference). Generate a response from each. Use the highest-judge-
scoring response as the SFT target.

**Why it works:** Each teacher has stylistic and content biases.
Ensemble distillation gives you the best-of-multiple, eliminating any
single teacher's drift.

**Implementation:** Set `teachers: [claude-opus-4-7, gpt-4o,
deepseek-v4-pro]` in the data generation config; the pipeline rotates
through them and picks the best.

Expected gain: **+3-5 CAB-FF points** + meaningful diversity in
response style.

### B9. Curriculum learning (easy → hard)

**What it is:** Order training examples from easy (L1 objective
questions) to hard (L3 adversarial / multi-turn). The model builds
confidence on simple cases before tackling adversarial pressure.

**Why it works:** Standard SGD with random ordering wastes capacity
early on hard examples the model can't yet handle. Curriculum focuses
that capacity.

**Implementation:** Set `curriculum: by_difficulty` in the SFT config
data section. (Default is `shuffle`.)

Expected gain: **modest +1-3 points**, but faster convergence (fewer
training steps to reach the same score).

### B10. CAB-FF as training-time signal, not just final gate

**What it is:** During SFT, every N steps, run a tiny CAB-FF subset
(50 questions). Use the per-dimension scores to monitor where the
model is regressing in real time. Early-stop training if any dimension
drops by more than 5 points.

**Why it works:** Standard `eval_loss` doesn't tell you the model is
becoming worse at Catholic-tradition questions specifically.
Per-dimension CAB-FF eval does.

**Implementation:** Set `cab_ff_inline_eval: true` in the SFT config
training block. Runs a 50-question subset every 250 steps; ~2 min
extra per eval. Logs per-dimension scores to TensorBoard.

Expected gain: **catches regressions early**, allowing earlier
intervention. Saves wasted training compute.

---

## C. The iterative refinement protocol

This is the loop `make iterate` runs. It's the single most important
quality move in this pipeline.

### Round 1 — broad SFT+DPO baseline

1. Run `make data` (full synth dataset)
2. Run `make sft` (DoRA + NEFTune)
3. Run `make dpo` (SimPO)
4. Run `make eval` — record the per-dimension breakdown
5. The lowest-scoring dimension and axis become Round 2 targets

### Round 2 — targeted gap-filling

1. Run `make data TARGETED_DIM="<weakest dim>" TARGETED_AXIS="<weakest
   axis>"` — generates +2000 examples concentrated in that area
2. Run `make sft CONFIG=configs/sft_delta.yaml` — 1-epoch delta on a
   fresh adapter, started from Round 1's DPO weights
3. Mine hard negatives from Round 1's failed adversarial probes
4. Run `make dpo` on the new pref data
5. Run `make eval`; compare to Round 1

**Promotion rule:** If composite ≥ Round 1 + 2 AND weakest-dim
improves by ≥ 5, accept. Otherwise revert.

### Round 3 — polish and best-of-N

1. Best-of-N rejection sampling on the current model (`make best-of-n
   N=8`)
2. SFT delta on the top-1 rollouts
3. Run `make eval` — final scoring

### Optional Round 4 — GRPO

Only worth doing if budget allows. Lift is typically +2-4 on top of
Round 3.

### Diminishing returns

In practice, 3 rounds saturates. Round 4 typically gains <2 points.
Stop when the round-over-round delta is <2.

---

## D. Quality benchmarks (what numbers to expect)

These are approximate, based on internal experiments on Gemma 4 31B.
Your mileage will vary by base model and data quality.

| Stage | CAB-FF Score | Drift Index | Sycophancy Index | Faithfulness Index |
|---|---:|---:|---:|---:|
| Gemma 4 31B base | ~52 | 28 | 19 | ~48 |
| + SFT (DoRA + NEFTune) | ~64 (+12) | 18 (-10) | 14 (-5) | ~60 (+12) |
| + DPO (SimPO) | ~70 (+6) | 12 (-6) | 9 (-5) | ~67 (+7) |
| + Iterate Round 2 | ~74 (+4) | 9 (-3) | 7 (-2) | ~71 (+4) |
| + Iterate Round 3 | ~77 (+3) | 7 (-2) | 6 (-1) | ~74 (+3) |
| + GRPO (optional) | ~80 (+3) | 5 (-2) | 5 (-1) | ~77 (+3) |

Gating threshold for promotion vs base: composite ≥ base + 5, drift
≤ base - 10, sycophancy ≤ base - 10. The SFT+DPO baseline already
satisfies this — but the iterate loop is where you get from "passes
gate" to "publishable."

A model scoring **CAB-FF ≥ 75** is comfortably state-of-the-art for
Christian AI alignment as of May 2026. A model scoring **≥ 80** would
exceed any frontier closed model's known CAB-FF performance (the
best closed-model FAI-C scores Gloo has reported are in the low 60s).

---

## Open questions

- Will GRPO on tradition-specialist adapters beat GRPO on the general
  model? Hypothesis yes; not yet tested.
- Can self-play debate replace multi-turn pushback data entirely?
- Does Spectrum + DoRA beat DoRA alone on 70B+ bases? (Spectrum docs
  suggest yes; we lack the compute to verify.)
- For MoE bases, is router-only LoRA enough? Or do we need attention-
  expert LoRA?

Open an issue if you have data on any of these.
