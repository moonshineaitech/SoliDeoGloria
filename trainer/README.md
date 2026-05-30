# CAB-FF Trainer

Production-grade fine-tuning pipeline for building a Christian-aligned LLM,
guided by the CAB-FF benchmark as the eval signal at every stage.

The reference model produced by this pipeline is:

> **SoliDeoGloria-31B-v0.1** — based on **Gemma 4 31B Dense** (Apache 2.0)

Pipeline is **base-model-agnostic** — swap by editing one YAML.

> ## 👉 New here? Open **[`START_HERE.md`](START_HERE.md)** first.
> It's the single idiot-proof front door: a 60-second decision, an
> accounts checklist, and a 3-phase walkthrough (make data → train →
> use & share) for both the no-code AutoTrain lane and the one-command
> GPU lane. Everything else below is reference detail.

> ### ⏱️ Want to actually build this today?
> Go straight to **[`RUN_TODAY.md`](RUN_TODAY.md)** — a copy-paste,
> no-experience-required runbook with three budget paths
> (~$10 / ~$70-150 / ~$600-900), exact GPU-provider clicks, and exact
> commands. Then:
> ```bash
> python -m trainer.scripts.cost_estimate --all-presets   # see costs first
> python -m trainer.scripts.preflight --config configs/sft_gemma_4_31b.yaml  # don't waste money
> ./scripts/run_all.sh                                     # one command, resume-safe
> ```
>
> ### 🖱️ Don't want to touch a GPU or the CLI at all?
> See **[`AUTOTRAIN.md`](AUTOTRAIN.md)** — generate the data once (no GPU),
> then upload two files to HuggingFace AutoTrain (or Together / OpenPipe)
> and click Train. Trades ~10-15 CAB-FF points for zero infra.

## Base model picks (May 29 2026 — verified)

The May 2026 frontier of open weights is genuinely exceptional. Pick by
serving constraint and license preference:

| Tier | Model | Params | License | HF repo | Trainable on |
|---|---|---|---|---|---|
| **Default — production sweet spot** | **Gemma 4 31B Dense** | 31B dense | **Apache 2.0** | `google/gemma-4-31b` | 1× H100 80GB |
| Apache 32B alt | Qwen 3.6-27B | 27B dense | Apache 2.0 | `Qwen/Qwen3.6-27B` | 1× H100 80GB |
| MIT reasoning | DeepSeek-R1-Distill-Qwen-32B | 32B dense | MIT | `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` | 1× H100 80GB |
| On-device / multimodal | **Gemma 4 E4B** | 4B effective | Apache 2.0 | `google/gemma-4-e4b` | 1× 16GB GPU + native multimodal (text/image/audio) |
| Frontier reasoning | **Kimi K2.6** | 1T / 32B active MoE | Modified MIT | `moonshotai/Kimi-K2.6` | 16+× H100 |
| Frontier agentic | **GLM-5.1** | 744B / 40B active MoE | MIT | `zai-org/GLM-5.1` | 8-16× H100 |
| Frontier general | **DeepSeek V4-Pro** | 1.6T / 49B active MoE | MIT | `deepseek-ai/DeepSeek-V4-Pro` | full cluster (1M ctx, agentic SOTA) |
| Frontier smallest | DeepSeek V4-Flash | 284B / 13B active MoE | MIT | `deepseek-ai/DeepSeek-V4-Flash` | 4-8× H100 |
| Long-context (10M) | Llama 4 Scout | varies | Llama 4 | `meta-llama/Llama-4-Scout` | 1-2× H100 |

**Reality check:** for solo fine-tuning, Gemma 4 31B Dense is the sweet
spot — beats 400B-class rivals on Arena AI per Google's own announcement,
runs on a single H100 for LoRA training, and ships on Apache 2.0 with
zero usage restrictions. Train it for $50-100, serve it on a 4090 after
quantization.

The frontier MoEs (GLM-5.1, Kimi K2.6, DeepSeek V4-Pro) are genuinely
top-of-the-line but require cluster access. If your budget can absorb
multi-node H100 rental, those configs are in `configs/` ready to go.

## Why Gemma 4 31B is the new default

| Property | Why it matters here |
|---|---|
| **31B dense** (not MoE) | No expert-routing complexity, no per-expert LoRA explosion. Standard PEFT methods work cleanly. |
| Apache 2.0 (no usage caps) | Unlike old Gemma license; ministries and businesses can ship without restriction. |
| Trains on 1× H100 80GB w/ LoRA | $7-13 of compute for a full SFT run. |
| Serves on 1× 4090 after AWQ | Self-hosting cost is one consumer GPU. |
| Multimodal architecture (text + image) | Future-proofs the model for image-based Scripture / icon questions. |
| Day-one support across the ecosystem | Transformers, TRL, PEFT, Unsloth, vLLM, llama.cpp, Ollama, MLX, LM Studio. |

## What's new in this trainer (May 2026 best practices)

We've upgraded from "LoRA + SFT + DPO" to incorporate the techniques that
emerged through 2025-2026:

- **DoRA by default** — Weight-Decomposed LoRA from NVIDIA Research.
  Closes ~half the gap between LoRA and full FT for ~5-10% extra VRAM.
  Particularly strong on instruction-following at low rank.
- **NEFTune** — noisy-embedding fine-tuning. Roughly +5-10 points on
  instruction-following benchmarks for free. We default to alpha=5.
- **Spectrum** — for the rare case where DoRA isn't enough. Identifies
  high-SNR layers and trains only those; ~42% wall-time reduction vs
  full FT with full-FT quality on dense models.
- **NEFTune + DoRA stacked** — they compose; the gains are roughly
  additive on our internal SFT runs.
- **SimPO loss** as DPO upgrade — length-normalized log-ratio,
  more stable than vanilla DPO on adversarial preference pairs.
- **Online DPO + best-of-N rejection sampling** — generate K rollouts
  per prompt with the SFT model, judge with the CAB-FF rubric, train
  the top-1 as SFT and (top-1 vs bottom-1) as a DPO pair. This is
  cheaper than full GRPO and recovers most of the quality.
- **Iterative refinement loop** (`make iterate`) — three rounds of
  data-gen → train → eval → targeted-data-gen-for-weak-dimensions.
- **Hard-negative mining** — failed adversarial probes become
  next-iteration DPO negatives.
- **Tradition-specialist adapters** — train base+general LoRA, then
  separate adapters per tradition (Catholic, Reformed, etc.) that
  can be loaded at inference based on the user's stated tradition.
- **CAB-FF as continuous training-time signal**, not just final gate.

See [`IMPROVEMENTS.md`](IMPROVEMENTS.md) for the full pitfall + growth-hack
playbook — it's the most important doc in this trainer beyond the README.

## Stage map

```
┌──────────────────────┐
│ 0. Base model        │  Gemma 4 31B Dense (default) — Apache 2.0
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 1. (opt) CPT         │  ~500M-1B tokens of public-domain Christian
│  Continued           │  corpus. Optional but recommended for E2B/E4B/9B.
│  pre-training        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 2. SFT               │  DoRA-128 + NEFTune α=5 + Liger kernels +
│  Supervised          │  Flash Attn 2 + packing. ~50K-200K examples
│  fine-tuning         │  blending CAB-FF synth, multi-turn pushback,
└──────────┬───────────┘  Tulu-3 general, Christian-corpus QA.
           │
┌──────────▼───────────┐
│ 3. DPO (SimPO)       │  ~10K-30K preference pairs from CAB-FF
│  Preference learning │  adversarial taxonomy. Length-normalized,
└──────────┬───────────┘  stable on hard-negative pairs.
           │
┌──────────▼───────────┐
│ 4. ITERATE LOOP      │  ← THIS IS THE GROWTH-HACK STAGE
│   ① eval CAB-FF      │  Identify weakest dimension and axis
│   ② targeted gen     │  Generate fresh data for that dimension
│   ③ SFT+DPO delta    │  Quick adapter update (~30 min on H100)
│   ④ promote if Δ ≥ 2 │  Loop or exit; usually 2-3 rounds settles
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 5. (opt) GRPO        │  Online RL with CAB-FF rubric as reward.
│  with CAB-FF reward  │  v1.0+ feature; most expensive stage.
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 6. CAB-FF gating     │  Must clear: CAB-FF Score ≥ base+5,
│                      │  Drift ≤ base-10, Sycophancy ≤ base-10,
└──────────┬───────────┘  no dim regression > 3.
           │
┌──────────▼───────────┐
│ 7. Quantize          │  AWQ INT4 (vLLM), GGUF Q4_K_M / Q5_K_M
└──────────┬───────────┘  (Ollama, llama.cpp, consumer GPUs).
           │
┌──────────▼───────────┐
│ 8. Distribution      │  HF Hub + Ollama Registry, model card +
│                      │  eval report.
└──────────────────────┘
```

## Quick start (zero compute — dry run)

```bash
cd trainer
pip install -e .                  # core, no GPU deps
make dry-run                      # ~3 min on CPU; no API key needed
```

## Full run (with a GPU)

```bash
# On a rented H100 box (Lambda/RunPod/Modal/Together):
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer
pip install -e ".[gpu,teachers,eval,deploy]"
pip install flash-attn==2.7.0 --no-build-isolation

# 1. Generate training data (teacher API; ~$30-80; 30-60 min)
export ANTHROPIC_API_KEY=...
make data

# 2. SFT (default = Gemma 4 31B Dense, DoRA + NEFTune; ~3-5 hr; $7-13)
make sft CONFIG=configs/sft_gemma_4_31b.yaml

# 3. DPO with SimPO loss (~1-2 hr; $3-5)
make dpo CONFIG=configs/dpo_gemma_4_31b.yaml

# 4. NEW: iterative refinement (~2-3 rounds; auto-targets weak dims)
make iterate ROUNDS=3 BASE_CHECKPOINT=outputs/sdg-31b-dpo

# 5. Evaluate against CAB-FF
make eval CHECKPOINT=outputs/sdg-31b-iter-final

# 6. Quantize and publish
make quantize CHECKPOINT=outputs/sdg-31b-iter-final
make publish HF_REPO=solideogloria/sdg-31b-v0.1
```

## Cost budget (Gemma 4 31B default)

| Phase | Compute | Wall | Compute cost | API cost |
|---|---|---|---|---|
| Data generation | CPU | 30-60 min | $0.50 | $30-80 |
| SFT (DoRA-128 + NEFTune) | 1× H100 80GB | 3-5 hr | $7-13 | — |
| DPO (SimPO) | 1× H100 80GB | 1-2 hr | $3-5 | — |
| Iterate loop (2-3 rounds) | 1× H100 80GB | 1-3 hr per round | $3-8 per round | $5-15 per round |
| CAB-FF eval | CPU + API | 30 min | $0.50 | $5-15 |
| GRPO (optional) | 1-2× H100 | 6-12 hr | $15-60 | $20-80 |
| Quantize | CPU | 30 min | $0.50 | — |
| **v0.1 with iterate** | | **~10 hr** | **~$25-50** | **~$60-150** |
| **v1.0 with GRPO** | | **~24 hr** | **~$80-150** | **~$150-350** |

Frontier MoE bases (GLM-5.1 / Kimi K2.6 / DeepSeek V4-Pro) multiply
these by ~5-15×.

## What "Christian-aligned" means here

We are NOT training the model to confess any tradition's distinctives as
objective truth. We are training it to:

1. **Use Christian categories** when the user does. Name God (not
   "higher power"), prayer (not "mindfulness"), virtue (not "values"),
   sin (not "unhealthy patterns").
2. **Stay inside the named tradition.** Catholic question → Catholic
   answer; Reformed → Reformed; the model doesn't impose a single
   confession.
3. **Engage Scripture accurately.** No fabricated citations.
4. **Hold sound positions under pushback** without sycophancy.
5. **Refuse the right things.** Crisis-line on suicidality; not refuse
   to discuss the Trinity.

CAB-FF measures these. Training against CAB-FF means training toward
those behaviors.

## Layout

```
trainer/
├── README.md                     (this file)
├── IMPROVEMENTS.md               ← read this — pitfalls + growth hacks
├── REPRO.md                      step-by-step reproduction
├── CONTAMINATION.md              CAB-FF test-set leakage prevention
├── DATA_LICENSING.md             per-source license analysis
├── pyproject.toml
├── Makefile
├── configs/
│   ├── sft_gemma_4_31b.yaml         ← default
│   ├── sft_gemma_4_e4b.yaml         edge / on-device target
│   ├── sft_qwen3_6_27b.yaml         Apache alternative
│   ├── sft_deepseek_r1_distill_32b.yaml
│   ├── sft_deepseek_v4_flash.yaml   frontier MoE (4-8× H100)
│   ├── sft_deepseek_v4_pro.yaml     frontier MoE (cluster)
│   ├── sft_glm_5_1.yaml             frontier MoE (8-16× H100)
│   ├── sft_kimi_k2_6.yaml           frontier MoE (16+× H100)
│   ├── sft_llama_4_scout.yaml       long-context (10M)
│   ├── dpo_gemma_4_31b.yaml
│   ├── grpo_gemma_4_31b.yaml
│   └── dry_run.yaml
├── data/
│   ├── pipeline/                 numbered stages 01-07
│   └── corpus_sources.md
├── train/
│   ├── sft.py                    DoRA + NEFTune + Liger + packing
│   ├── dpo.py                    SimPO-stable DPO
│   ├── grpo.py                   online RL with CAB-FF reward
│   ├── iterate.py                ← new: multi-round refinement loop
│   ├── best_of_n.py              ← new: rejection-sampling for cheap RL
│   └── continued_pretrain.py
├── eval/
│   ├── run_cab_ff.py
│   ├── compare_to_baseline.py
│   ├── per_dimension_drilldown.py  ← new: which dims regressed?
│   └── gating.py
├── deploy/
│   ├── quantize_awq.py
│   ├── quantize_gguf.py
│   ├── make_ollama_modelfile.py
│   ├── push_to_hub.py
│   ├── tradition_adapter_merge.py  ← new: runtime tradition selection
│   └── vllm_serve.sh
└── model_cards/
    ├── sdg_31b_template.md
    └── eval_report_template.md
```

## Citation

```bibtex
@misc{cabff-trainer-2026,
  title  = {CAB-FF Trainer: Reproducible Pipeline for Christian-Aligned LLMs},
  author = {Soli Deo Gloria Research Initiative},
  year   = {2026},
  url    = {https://github.com/moonshineaitech/SoliDeoGloria/tree/main/trainer}
}
```

## License

MIT for the trainer code. Training data licenses per-source — see
[`DATA_LICENSING.md`](DATA_LICENSING.md). The CAB-FF benchmark is
CC BY-SA 4.0.
