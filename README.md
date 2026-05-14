# CAB-FF: The Christian AI Benchmark — Flourishing & Faithfulness Edition

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Version](https://img.shields.io/badge/Version-3.0.0-blueviolet.svg)]()
[![Questions](https://img.shields.io/badge/Questions-820%2B-red.svg)]()
[![Dimensions](https://img.shields.io/badge/Dimensions-8-green.svg)]()
[![Axes](https://img.shields.io/badge/Faithfulness%20Axes-7-orange.svg)]()
[![Types](https://img.shields.io/badge/Question%20Types-5-blue.svg)]()
[![CI](https://github.com/moonshineaitech/SoliDeoGloria/actions/workflows/ci.yml/badge.svg)](https://github.com/moonshineaitech/SoliDeoGloria/actions/workflows/ci.yml)

> **The open, reproducible Christian AI benchmark.**
> 820+ questions · 8 dimensions · 9 tradition-aware judges · explicit
> Drift and Sycophancy indices · fully published methodology, code, and
> data under CC BY-SA 4.0.

## Why this exists

In December 2025 Gloo reported that today's leading language models
average **48/100** on the Faith dimension of their *Flourishing AI
Christian* (FAI-C) benchmark, that they readily substitute "higher
power" for God, "mindfulness" for prayer, and "values" for virtue,
and that they drop biblical categories like sin, sanctification, and
the image of God under the slightest secular pressure.

Gloo published the finding. They did not publish the questions, the
methodology, the judge prompts, or the 25 alignment indicators.

**CAB-FF is the open replicate.** Same flourishing dimensions for
direct comparability, plus an eighth distinctively Christian
dimension Gloo's framework cannot reach by construction. Three more
question types (adversarial, multi-turn, comparative) that probe
the failure modes Gloo named publicly. A nine-persona judge panel
balanced across the major historic streams of the Church — all
prompts published.

## 30-second pitch

```bash
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria
pip install -e .
python examples/quickstart.py
```

That's a complete CAB-FF run against a mock model in under 5 seconds.
No API key required. To run against your model:

```bash
python examples/quickstart.py --provider anthropic --model claude-sonnet-4-6
python examples/quickstart.py --provider openai --model gpt-4o
python examples/quickstart.py --provider litellm --model ollama/llama3
```

LiteLLM gives you ~100 providers including local Ollama. See
[`docs/FAQ.md`](docs/FAQ.md#how-long-does-a-full-run-take-how-much-does-it-cost)
for cost / time estimates.

## What you get back

Every run produces a JSON report. The summary section:

```json
{
  "cab_ff_score": 67.8,
  "flourishing_score": 71.5,
  "faithfulness_index": 64.2,
  "drift_index": 18.4,
  "sycophancy_index": 12.1,
  "by_dimension": { "Faith & Spirituality": { "score": 52.1, ... } },
  "by_axis":      { "Secular-Drift Resistance": { "score": 81.6, ... } }
}
```

Plus per-question detail with every judge's score and justification,
every alignment indicator's pass/fail, and the full transcript on
multi-turn questions.

## How CAB-FF compares to Gloo FAI-C

| | Gloo FAI-C (private) | **CAB-FF v3.0 (open)** |
|---|---|---|
| Question count | 807 | **820+** |
| Dimensions | 7 | **8** (+ Vocation & Witness) |
| Cross-cutting faithfulness axes | implicit | **7 explicit, scored** |
| Question types | obj + subj + tangential | **5** (+ adversarial, multi-turn, comparative) |
| Alignment indicators | 25 (private) | **40** (published, with detection hints) |
| Judge panel | undisclosed | **9 named tradition-aware personas** |
| Drift Index | implicit | **explicit secondary metric** |
| Sycophancy Index | not measured | **explicit secondary metric** |
| Methodology | partially private | **fully open** |
| License | proprietary | CC BY-SA 4.0 |

See [`docs/GLOO_COMPARISON.md`](docs/GLOO_COMPARISON.md) for the full
side-by-side and [`docs/ADVERSARIAL_PROBES.md`](docs/ADVERSARIAL_PROBES.md)
for the failure-mode taxonomy.

## The eight dimensions

The seven Harvard Human Flourishing Program dimensions Gloo uses, plus
one distinctively Christian dimension:

1. **Character & Virtue** (χ)
2. **Close Social Relationships** (ρ)
3. **Happiness & Life Satisfaction** (η)
4. **Meaning & Purpose** (μ)
5. **Mental & Physical Health** (ψ)
6. **Financial & Material Stewardship** (φ)
7. **Faith & Spirituality** (σ)
8. **Vocation & Witness** (ω) — *NEW*

Full descriptions in [`docs/CAB_FF_DIMENSIONS.md`](docs/CAB_FF_DIMENSIONS.md).

## The seven faithfulness axes

Scored cross-dimensionally on every subjective response:

Doctrinal Fidelity · Scriptural Grounding · Tradition Fairness ·
Pastoral Sensitivity · **Secular-Drift Resistance** ·
**Refusal Calibration** · **Sycophancy Resistance**

## The five question types

| Type | Purpose | Scoring |
|---|---|---|
| `objective` | Multiple-choice factual | 0 or 100; answer positions randomized |
| `subjective` | Open scenario, judge-panel scored | 0-100, median of 3-9 judges |
| `adversarial` | Probe a specific failure mode (drift, sycophancy, fabrication) | Pattern detection + judge fallback |
| `multi_turn` | 2-4 turn dialogue with pushback | 0.6 × final-turn judge + 0.4 × consistency |
| `comparative` | Paired Christian-vs-neutral framing | Inverse drift score |

## Scoring formula

```
Flourishing Score   = ⁸√(chi · rho · eta · mu · psi · phi · sigma · omega)
Faithfulness Index  = ⁷√(7 transverse axis scores)
CAB-FF Score        = √(Flourishing × Faithfulness)

Drift Index         = 100 − mean(drift signals)        (lower is better)
Sycophancy Index    = 100 − mean(sycophancy signals)   (lower is better)
```

Geometric means prevent compensation: a model cannot hide a weak
Faith dimension behind a strong Health score, AND cannot hide weak
Secular-Drift Resistance behind strong Pastoral Sensitivity.

## Documentation

For most readers, in order:

1. [**`docs/BENCHMARK_DESIGN.md`**](docs/BENCHMARK_DESIGN.md) — what we measure and why
2. [**`docs/ARCHITECTURE.md`**](docs/ARCHITECTURE.md) — how the pipeline works (ASCII diagram)
3. [**`docs/VALIDATION.md`**](docs/VALIDATION.md) — anti-gaming, reproducibility, validation status
4. [**`docs/GLOO_COMPARISON.md`**](docs/GLOO_COMPARISON.md) — full Gloo-vs-CAB-FF side-by-side
5. [**`docs/FAQ.md`**](docs/FAQ.md) — questions you probably have

Reference docs:

- [`docs/CAB_FF_METHODOLOGY.md`](docs/CAB_FF_METHODOLOGY.md)
- [`docs/CAB_FF_DIMENSIONS.md`](docs/CAB_FF_DIMENSIONS.md)
- [`docs/CAB_FF_SCHEMA.md`](docs/CAB_FF_SCHEMA.md)
- [`docs/ADVERSARIAL_PROBES.md`](docs/ADVERSARIAL_PROBES.md)
- [`rubrics/cab_ff_subjective_scoring.md`](rubrics/cab_ff_subjective_scoring.md)
- [`rubrics/cab_ff_alignment_indicators.md`](rubrics/cab_ff_alignment_indicators.md)

## Provider adapters (no boilerplate required)

```python
from cab_ff import CABFFEvaluator
from cab_ff.providers import anthropic_model, anthropic_judge

model_fn = anthropic_model("claude-sonnet-4-6")
judge_fn = anthropic_judge("claude-opus-4-7")

report = CABFFEvaluator(model_fn=model_fn, judge_fn=judge_fn) \
            .evaluate("data/CAB_FF_v3_dataset.json", max_questions=50)
print(report["summary"]["cab_ff_score"])
```

Adapters ship for **Anthropic**, **OpenAI**, **LiteLLM** (100+
providers including Ollama, OpenRouter, Together, Groq, Mistral,
Cohere, Vertex, Bedrock), and a **mock** model for offline CI. Adding
a new provider is ~30-60 lines — see
[`cab_ff/providers/`](cab_ff/providers/).

## CLI reference

```bash
# Smoke test (no API key)
python examples/quickstart.py

# Validate a dataset against the schema
python -m cab_ff.cli validate data/CAB_FF_v3_dataset.json

# Inspect the configuration
python -m cab_ff.cli dimensions      # 8 dimensions + 7 axes
python -m cab_ff.cli question-types  # 5 types with descriptions
python -m cab_ff.cli judges          # 9 personas, names and system prompts
python -m cab_ff.cli indicators --christian-only

# Sample some questions to read
python -m cab_ff.cli sample data/CAB_FF_v3_dataset.json -T adversarial -n 5

# Summarize a finished run
python -m cab_ff.cli summarize quickstart_results.json

# All of the above in one place
make help-targets   # via Makefile
```

## Repository layout

```
cab_ff/                          # core package
  dimensions.py / loader.py      # schema, filters, validation
  scorer.py / aggregator.py      # 5 scorers + geometric-mean composite
  alignment_indicators.py        # 40 binary YES/NO probes
  judges.py                      # 9 tradition-aware judge personas
  evaluator.py / cli.py          # orchestrator + CLI
  providers/                     # Anthropic, OpenAI, LiteLLM, mock
  banks/                         # question banks
scripts/
  build_dataset.py               # assembles seed + banks, validates, dedupes
data/
  CAB_FF_v3_dataset.json         # 820+ assembled dataset
  CAB_FF_v3_seed.json            # 80 hand-authored canonical seed
examples/
  quickstart.py                  # runs in 5s on a mock; flags real providers
  cab_ff_example.py              # minimal API stub
docs/                            # methodology, architecture, validation, FAQ
rubrics/                         # subjective scoring + indicator references
marketing/                       # launch copy (X / LinkedIn / blog / press)
tests/                           # 47 tests
.github/                         # CI, issue + PR templates
```

## Contributing

We want this to be the standard open Christian AI benchmark. Three
high-value places to plug in:

1. **Improve a question.** If a question is theologically off in your
   tradition, open an issue with the `CABFF-NNNN` id. Or open a PR
   editing the matching `cab_ff/banks/bank_*.py` and re-running
   `python scripts/build_dataset.py`.
2. **Run it against a model and publish the result.** See
   [`marketing/post_invite_baselines.md`](marketing/post_invite_baselines.md).
3. **Add a provider adapter, judge persona, or probe.** Each is a
   small, self-contained change.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Citation

```bibtex
@misc{cabff2026,
  title  = {CAB-FF: The Flourishing \& Faithfulness Benchmark for AI Alignment with Christian Faith},
  author = {Soli Deo Gloria Research Initiative},
  year   = {2026},
  url    = {https://github.com/moonshineaitech/SoliDeoGloria},
  license = {CC-BY-SA-4.0}
}
```

Or use the `CITATION.cff` at the root for GitHub's "Cite this
repository" button.

## License

**CC BY-SA 4.0.** Share, adapt, attribute, share-alike. Methodology,
code, judge prompts, alignment indicators, and the full 820+ question
dataset are all open and versioned.

## Contact

- **Website:** [SoliDeoGloria.ai](https://SoliDeoGloria.ai)
- **Publisher:** Eldest AI LLC dba GoldRock AI
- **Issues:** [GitHub Issues](https://github.com/moonshineaitech/SoliDeoGloria/issues)
- **Email:** research@solideogloria.ai

## Acknowledgments

CAB-FF builds on the Harvard Human Flourishing Program (which Gloo's
framework also draws from), the Barna Group and REVEAL research on
faith formation, the historic confessional traditions of the global
Church, and CAB v2.0 (preserved under `cab_benchmark/`).

> *"Soli Deo Gloria."* — To God alone be the glory.
