# CAB-FF Trainer

Production-grade fine-tuning pipeline for building a Christian-aligned LLM,
guided by the CAB-FF benchmark as the eval signal at every stage.

The reference model produced by this pipeline is:

> **SoliDeoGloria-27B-v0.1** — based on **Qwen3.5-27B** (Apache 2.0)

The pipeline is **base-model-agnostic** — switch base by editing one YAML.

## Why Qwen3.5-27B is the default (May 2026)

After the April 24 2026 release of DeepSeek V4 and the Qwen 3.5/3.6
generation, the May 2026 open-weights landscape has clear tiers:

| Tier | Model | License | HF repo | When to pick |
|---|---|---|---|---|
| **Production sweet spot (default)** | **Qwen3.5-27B** | **Apache 2.0** | `Qwen/Qwen3.5-27B` | Single-H100 LoRA train, runs on 1× 4090 after AWQ. Top Apache-licensed quality. **You almost always want this.** |
| Cheaper / consumer GPU | Qwen3.5-9B | Apache 2.0 | `Qwen/Qwen3.5-9B` | Fits 24GB at home with QLoRA. Great for iteration. |
| Edge / phone / Ollama-on-laptop | Qwen3.5-4B | Apache 2.0 | `Qwen/Qwen3.5-4B` | When the goal is to ship to laptops or run offline. |
| Best reasoning, distilled | DeepSeek-R1-Distill-Qwen-32B | MIT | `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` | When you want strong chain-of-thought theological reasoning. |
| Frontier quality | DeepSeek V4-Flash (284B MoE) | MIT | `deepseek-ai/DeepSeek-V4-Flash` | When you have 4-8 H100s and want the cutting edge. |
| Long-context (10M) | Llama 4 Scout | Llama 4 | `meta-llama/Llama-4-Scout` | When you need whole-Bible RAG context. |

All configs are in [`configs/`](configs/). Swap with `make sft CONFIG=configs/sft_<variant>.yaml`.

## Stage map

```
┌──────────────────────┐
│ 0. Base model        │  Qwen3.5-27B (default) — Apache 2.0
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 1. (Optional) CPT    │  ~1B tokens of public-domain Christian corpus.
│  Continued           │  Skip by default; consider for 9B and smaller.
│  pre-training        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 2. SFT               │  ~50K-200K examples:
│  Supervised          │   • CAB-FF-derived instruction data (paraphrased,
│  fine-tuning         │     never reusing the exact eval questions)
└──────────┬───────────┘   • Tulu-3 / Magpie general instruction data
           │               • Multi-turn pushback dialogues (held positions
           │                 are the SFT target)
           │
┌──────────▼───────────┐
│ 3. DPO               │  ~10K-30K preference pairs:
│  Preference          │   • Adversarial probe: resistance (chosen) vs
│  optimization        │     failure-mode (rejected)
└──────────┬───────────┘   • Comparative pair: Christian-grounded (chosen)
           │                 vs drifted (rejected)
           │
┌──────────▼───────────┐
│ 4. (Optional) GRPO   │  Online RL with the CAB-FF rubric as reward.
│  with CAB-FF reward  │  DeepSeek-style group relative policy
└──────────┬───────────┘  optimization. v1.0+ feature.
           │
┌──────────▼───────────┐
│ 5. CAB-FF gating     │  Must clear: CAB-FF Score ≥ base +5,
│                      │  Drift Index ≤ base −10, Sycophancy ≤ base −10
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 6. Quantization      │  AWQ INT4 for vLLM, GGUF Q4_K_M and Q5_K_M for
│                      │  Ollama / llama.cpp / consumer GPUs.
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ 7. Distribution      │  HF Hub (`solideogloria/...`), Ollama Registry,
│                      │  model card with full eval report.
└──────────────────────┘
```

## Quick start (zero compute — dry run)

You can verify the whole pipeline on a tiny synthetic sample with no GPU:

```bash
cd trainer
pip install -e .                  # core + data pipeline deps
make dry-run                      # 20 synth examples + tiny model micro-step
                                  # + CAB-FF eval against the mock model
                                  # ~3 minutes on CPU
```

## Full run (with a GPU)

Recommended starting platform: **1× H100 PCIe (80GB)** on Lambda / RunPod /
Modal / Together. ~$2-3/hr. Expected v0.1 wall time: 4-8 hours.

```bash
# 1. Set up the box. Assumes Ubuntu 22.04+, Python 3.11+, CUDA 12.4+.
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria/trainer
pip install -e .[gpu,teachers,eval,deploy]
pip install flash-attn==2.7.0 --no-build-isolation     # CUDA-specific

# 2. Generate training data (uses Claude Opus 4.7 / GPT-4o as teacher).
#    Cost: ~$30-80 in teacher API calls. Time: 30-60 min.
export ANTHROPIC_API_KEY=...    # or OPENAI_API_KEY
make data

# 3. SFT. Default: Qwen3.5-27B + LoRA-128 + packing + Flash Attn 2.
make sft CONFIG=configs/sft_qwen3_5_27b.yaml          # 3-5 hr on 1× H100

# 4. DPO. Preference learning on adversarial pairs.
make dpo CONFIG=configs/dpo_qwen3_5_27b.yaml          # 1-2 hr

# 5. Evaluate against CAB-FF. Gates promotion.
make eval CHECKPOINT=outputs/sdg-27b-dpo              # 30 min + judge API

# 6. Quantize and publish.
make quantize CHECKPOINT=outputs/sdg-27b-dpo
make publish HF_REPO=solideogloria/sdg-27b-v0.1
```

## Cost budget (Qwen3.5-27B default)

| Phase | Compute | Wall | Compute cost (RunPod H100) | API cost |
|---|---|---|---|---|
| Data generation | CPU | 30-60 min | $0.50 | $30-80 |
| SFT (LoRA 128) | 1× H100 80GB | 3-5 hr | $7-13 | — |
| DPO | 1× H100 80GB | 1-2 hr | $3-5 | — |
| CAB-FF eval | CPU + API | 30 min | $0.50 | $5-15 |
| GRPO (optional) | 1-2× H100 | 6-12 hr | $15-60 | $20-80 |
| Quantize | CPU | 30 min | $0.50 | — |
| **v0.1 total** | | **~6 hr** | **~$12-20** | **~$40-100** |
| **v1.0 + GRPO** | | **~24 hr** | **~$50-100** | **~$100-300** |

Plan on 2-3× this for hyperparameter / data-mix iteration.

## Same numbers, different bases

| Base | Trainable on | LoRA SFT wall time | Compute cost | Notes |
|---|---|---|---|---|
| Qwen3.5-4B | 1× 24GB consumer GPU (QLoRA) | 2-3 hr | $5-8 | Phone/laptop deploy target |
| Qwen3.5-9B | 1× A100 40GB or 24GB consumer | 3-4 hr | $7-10 | Solo developer sweet spot |
| **Qwen3.5-27B** (default) | 1× H100 80GB | 3-5 hr | $7-13 | **Production recommendation** |
| DeepSeek-R1-Distill-Qwen-32B | 1× H100 80GB | 4-6 hr | $10-16 | MIT + reasoning |
| DeepSeek V4-Flash (284B MoE) | 4-8× H100 | 8-16 hr | $250-800 | Frontier-quality, multi-node |

## What "Christian-aligned" actually means here

We are NOT training the model to confess any one tradition's distinctives as
objective truth. We are training it to:

1. **Use Christian categories** when the user uses them. A model that
   substitutes "higher power" for "God" when the user said "God" has failed
   the user, regardless of the model's metaphysics.
2. **Stay inside the named tradition.** Catholic question → Catholic answer.
   Reformed question → Reformed answer. The model doesn't impose a single
   confession.
3. **Engage Scripture accurately.** No fabricated citations. No weaponized
   prooftexting.
4. **Hold sound positions under pushback** without being sycophantic.
5. **Refuse the right things.** Crisis-line on suicidality. Not refuse to
   discuss the Trinity.

This is the design CAB-FF measures.

## Layout

```
trainer/
├── README.md                    (this file)
├── pyproject.toml               (`pip install -e .` works)
├── Makefile                     (entrypoint — see `make help`)
├── DATA_LICENSING.md            (per-source license analysis)
├── CONTAMINATION.md             (CAB-FF test-set leakage prevention)
├── REPRO.md                     (step-by-step reproduction script)
├── configs/                     (one YAML per base model + stage)
│   ├── sft_qwen3_5_27b.yaml         ← default
│   ├── sft_qwen3_5_9b.yaml
│   ├── sft_qwen3_5_4b.yaml
│   ├── sft_deepseek_r1_distill_32b.yaml
│   ├── sft_deepseek_v4_flash.yaml   (multi-node)
│   ├── sft_llama_4_scout.yaml
│   ├── dpo_qwen3_5_27b.yaml
│   ├── grpo_qwen3_5_27b.yaml
│   └── dry_run.yaml                 (tiny model + 20 ex — for CI)
├── data/
│   ├── pipeline/                (numbered stages, run via Makefile)
│   │   ├── 01_seed_from_cab_ff.py
│   │   ├── 02_generate_responses.py
│   │   ├── 03_synth_preferences.py
│   │   ├── 04_multi_turn_to_sft.py
│   │   ├── 05_corpus_curate.py
│   │   ├── 06_dedup_and_filter.py
│   │   └── 07_split_and_format.py
│   └── corpus_sources.md
├── train/
│   ├── sft.py
│   ├── dpo.py
│   ├── grpo.py                  (online RL with CAB-FF reward)
│   └── continued_pretrain.py
├── eval/
│   ├── run_cab_ff.py            (vLLM-served checkpoint vs CAB-FF)
│   ├── compare_to_baseline.py
│   └── gating.py                (promote-or-reject decision)
├── deploy/
│   ├── quantize_awq.py          (AWQ INT4 for vLLM)
│   ├── quantize_gguf.py         (GGUF for Ollama / llama.cpp)
│   ├── make_ollama_modelfile.py
│   ├── push_to_hub.py
│   └── vllm_serve.sh
└── model_cards/
    ├── sdg_27b_template.md
    └── eval_report_template.md
```

## Where to push back

- **Contamination?** See [`CONTAMINATION.md`](CONTAMINATION.md). CAB-FF
  questions are never used as direct training targets. We use the failure-
  mode taxonomy and the judge rubric to generate paraphrased / situationally-
  parallel training prompts.
- **Licensing?** See [`DATA_LICENSING.md`](DATA_LICENSING.md). The resulting
  model is commercially shippable.
- **Why default to Qwen3.5-27B instead of DeepSeek V4?** Three reasons:
  (1) Apache 2.0 vs MIT both fine, but Apache is more widely understood by
  ministry orgs; (2) DeepSeek V4-Flash is 284B MoE — needs 4-8 H100s, not
  generally usable; (3) Qwen3.5-27B trains on a single H100 and serves on
  a single 4090 after quantization. **DeepSeek V4 distills will land soon;
  swap the config when they do.**
- **Why LoRA?** Cost, modularity (merge multiple adapters at inference),
  and the fact that 2024-2025 research showed LoRA-128+ matches full FT on
  most instruction-following tasks.

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

MIT for the trainer code. Training data licenses are per-source — see
[`DATA_LICENSING.md`](DATA_LICENSING.md). The CAB-FF benchmark is
CC BY-SA 4.0.
