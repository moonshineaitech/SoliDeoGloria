<h1 align="center">CAB-FF</h1>
<p align="center"><strong>The open Christian AI benchmark.</strong><br>
1,056 questions · 8 dimensions · 9 tradition-aware judges · drift & sycophancy indices · fully reproducible.</p>

<p align="center">
  <a href="https://creativecommons.org/licenses/by-sa/4.0/"><img src="https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg" alt="License: CC BY-SA 4.0"></a>
  <img src="https://img.shields.io/badge/Version-3.0.1-blueviolet.svg" alt="Version 3.0.1">
  <img src="https://img.shields.io/badge/Questions-1056-red.svg" alt="1,056 questions">
  <img src="https://img.shields.io/badge/Dimensions-8-green.svg" alt="8 dimensions">
  <img src="https://img.shields.io/badge/Judges-9%20personas-orange.svg" alt="9 judge personas">
  <img src="https://img.shields.io/badge/Tests-47%20passing-success.svg" alt="47 tests passing">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success.svg" alt="Production ready">
  <a href="https://github.com/moonshineaitech/SoliDeoGloria/actions/workflows/ci.yml"><img src="https://github.com/moonshineaitech/SoliDeoGloria/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

---

## What CAB-FF measures

Today's leading language models drift quietly toward secular framings when Christians use them: they substitute *"higher power"* for **God**, *"mindfulness"* for **prayer**, *"values"* for **virtue**, and *"unhealthy patterns"* for **sin**. They fabricate Bible verses. They caricature historic traditions. They cave under sycophantic pressure.

CAB-FF measures all of this — across **8 flourishing dimensions**, **7 transverse faithfulness axes**, and **5 question types** including adversarial drift probes, multi-turn pushback dialogues, and Christian-vs-neutral comparative pairs that detect drift directly. A **9-persona judge panel** balanced across the major historic streams of the Church (Reformed, Catholic, Orthodox, Wesleyan, Pentecostal, Anglican, Baptist, plus a pastoral counselor and an academic theologian) scores responses on a 0–100 scale.

This is the open, reproducible counterpart to Gloo's privately-held FAI-C benchmark (December 2025). Methodology, code, prompts, judges, and 1,056 questions are all published under CC BY-SA 4.0.

## See it in action

A single CAB-FF run produces a JSON report like this:

```json
{
  "cab_ff_score": 67.8,
  "flourishing_score": 71.5,
  "faithfulness_index": 64.2,
  "drift_index": 18.4,
  "sycophancy_index": 12.1,
  "by_dimension": {
    "Faith & Spirituality":         { "score": 52.1, "count": 312 },
    "Vocation & Witness":           { "score": 65.4, "count":  88 },
    "Character & Virtue":           { "score": 78.2, "count":  84 }
  },
  "by_axis": {
    "Secular-Drift Resistance":     { "score": 81.6, "count": 240 },
    "Sycophancy Resistance":        { "score": 87.9, "count":  42 }
  }
}
```

Plus per-question detail with every judge's score and justification, every alignment indicator's pass/fail, and the full transcript on multi-turn questions.

## Quickstart

CAB-FF runs end-to-end against a built-in mock model in ~5 seconds — **no API key required**. This is the fastest way to verify your install works.

```bash
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria
pip install -e .
python examples/quickstart.py
```

You should see a JSON summary like the one above. If you see that, you're ready to run against a real model.

### Run against your model

Install the appropriate provider SDK, then point quickstart at it:

<table>
<thead>
<tr><th>Provider</th><th>Install</th><th>Run</th></tr>
</thead>
<tbody>
<tr>
<td>Anthropic</td>
<td><code>pip install -e ".[anthropic]"</code></td>
<td><code>python examples/quickstart.py --provider anthropic --model claude-sonnet-4-6</code></td>
</tr>
<tr>
<td>OpenAI</td>
<td><code>pip install -e ".[openai]"</code></td>
<td><code>python examples/quickstart.py --provider openai --model gpt-4o</code></td>
</tr>
<tr>
<td>~100 others via LiteLLM</td>
<td><code>pip install -e ".[litellm]"</code></td>
<td><code>python examples/quickstart.py --provider litellm --model ollama/llama3</code></td>
</tr>
<tr>
<td>Everything</td>
<td><code>pip install -e ".[all-providers]"</code></td>
<td>any of the above</td>
</tr>
</tbody>
</table>

Set `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` in your shell environment first. LiteLLM gives you OpenRouter, Together, Groq, Mistral, Cohere, Bedrock, Vertex, **and local Ollama**. See [`docs/FAQ.md`](docs/FAQ.md#how-long-does-a-full-run-take-how-much-does-it-cost) for cost and time estimates.

By default, quickstart runs 10 objective questions. To do a more thorough run:

```bash
python examples/quickstart.py \
  --provider anthropic --model claude-sonnet-4-6 \
  --judge claude-opus-4-7 \
  --objective 100 --subjective 30 --adversarial 30 \
  --multi-turn 10 --comparative 15 \
  --output my-run.json
```

Full CLI options: `python examples/quickstart.py --help`.

## Who CAB-FF is for

<table>
<tr>
<td width="50%" valign="top">

**🤖 Model maintainers and AI labs**
Run CAB-FF against your model before shipping. Get a single CAB-FF score, plus per-dimension breakdowns, drift index, and sycophancy index. The judge panel, indicators, and prompts are open — your eval is fully reproducible.

</td>
<td width="50%" valign="top">

**⛪ Christian institutions and ministries**
Evaluate which AI tools are safe to recommend, deploy, or build on. Reproducible numbers across denominations, with tradition-aware judging so a Catholic-context question gets a Catholic-aware judgment.

</td>
</tr>
<tr>
<td width="50%" valign="top">

**🛠️ Faith-tech founders and developers**
Build defensible evaluation into your product pipeline. Plug-and-play provider adapters, JSON output, CI-friendly mock provider.

</td>
<td width="50%" valign="top">

**🔬 AI alignment researchers**
A real, hand-curated, theology-aware benchmark for the underexplored intersection of Christian thought and LLM behavior. Probes specific named failure modes (drift, sycophancy, fabrication, refusal miscalibration).

</td>
</tr>
</table>

**Not for:** measuring any human's spiritual state, asserting confessional orthodoxy, or as a substitute for human pastoral discernment.

## How CAB-FF compares to Gloo FAI-C

|                                       | Gloo FAI-C (private)        | **CAB-FF v3.0 (open)**                                |
|---------------------------------------|-----------------------------|-------------------------------------------------------|
| Question count                        | 807                         | **1,056** (CC BY-SA, in the repo)                     |
| Dimensions                            | 7                           | **8** (+ Vocation & Witness)                          |
| Cross-cutting faithfulness axes       | implicit                    | **7 explicit, scored**                                |
| Question types                        | obj + subj + tangential     | **5** (+ adversarial, multi-turn, comparative)        |
| Alignment indicators                  | 25 (private)                | **40** (published, with detection hints)              |
| Judge panel                           | undisclosed                 | **9 named, tradition-aware personas with prompts**    |
| Drift Index / Sycophancy Index        | not separately measured     | **explicit secondary metrics**                        |
| Methodology                           | partially private           | **fully published**                                   |
| License                               | proprietary                 | **CC BY-SA 4.0**                                      |

Full side-by-side: [`docs/GLOO_COMPARISON.md`](docs/GLOO_COMPARISON.md). Adversarial-probe taxonomy: [`docs/ADVERSARIAL_PROBES.md`](docs/ADVERSARIAL_PROBES.md).

## The benchmark in one screen

<table>
<thead>
<tr><th>Component</th><th>What it is</th></tr>
</thead>
<tbody>
<tr><td><strong>8 dimensions</strong></td><td>Character & Virtue · Close Social Relationships · Happiness & Life Satisfaction · Meaning & Purpose · Mental & Physical Health · Financial & Material Stewardship · Faith & Spirituality · <strong>Vocation & Witness</strong></td></tr>
<tr><td><strong>7 faithfulness axes</strong></td><td>Doctrinal Fidelity · Scriptural Grounding · Tradition Fairness · Pastoral Sensitivity · Secular-Drift Resistance · Refusal Calibration · Sycophancy Resistance</td></tr>
<tr><td><strong>5 question types</strong></td><td><code>objective</code> · <code>subjective</code> · <code>adversarial</code> · <code>multi_turn</code> · <code>comparative</code></td></tr>
<tr><td><strong>9 judge personas</strong></td><td>Reformed · Catholic · Orthodox · Wesleyan · Pentecostal · Anglican · Baptist · pastoral counselor · academic theologian</td></tr>
<tr><td><strong>40 alignment indicators</strong></td><td>12 general · 18 distinctively Christian · 10 anti-failure-mode</td></tr>
<tr><td><strong>10 traditions</strong></td><td>Cross-Tradition + Catholic, Orthodox, Reformed, Lutheran, Baptist, Methodist, Anglican, Pentecostal, Evangelical</td></tr>
</tbody>
</table>

### Scoring

```
Flourishing Score   = ⁸√(8 dimension means)
Faithfulness Index  = ⁷√(7 axis means)
CAB-FF Score        = √(Flourishing × Faithfulness)

Drift Index         = 100 − mean(drift signals)        (lower is better)
Sycophancy Index    = 100 − mean(sycophancy signals)   (lower is better)
```

Geometric means prevent compensation: a model can't hide a weak Faith score behind a strong Health score, AND can't hide weak Secular-Drift Resistance behind strong Pastoral Sensitivity. Both must be high.

## Dataset breakdown

```
1,056 questions assembled from a 80-question hand-authored seed
+ per-dimension and cross-cutting question banks. Rebuild any time
with `python scripts/build_dataset.py`. Builder enforces no
duplicates across seed and banks.

  by_dimension:
    Faith & Spirituality:             485    Vocation & Witness:                105
    Character & Virtue:                94    Financial & Material Stewardship:   79
    Meaning & Purpose:                 79    Close Social Relationships:         76
    Happiness & Life Satisfaction:     71    Mental & Physical Health:           67

  by_type:        objective 680  subjective 166  adversarial 120  comparative 48  multi_turn 42
  by_difficulty:  L1 192   L2 464   L3 400
  by_tradition:   Cross-Tradition 799 · Catholic 54 · Reformed 32 · Orthodox 30 ·
                  Lutheran 29 · Anglican 26 · Pentecostal 25 · Methodist 24 ·
                  Baptist 21 · Evangelical 16
```

## Python API

```python
from cab_ff import CABFFEvaluator
from cab_ff.providers import anthropic_model, anthropic_judge   # requires .[anthropic]

evaluator = CABFFEvaluator(
    model_fn=anthropic_model("claude-sonnet-4-6"),
    judge_fn=anthropic_judge("claude-opus-4-7"),
)
report = evaluator.evaluate("data/CAB_FF_v3_dataset.json", max_questions=50)

print(f"CAB-FF: {report['summary']['cab_ff_score']:.1f}")
print(f"Drift Index: {report['summary']['drift_index']:.1f}  (lower is better)")
```

Other adapters: `openai_model` / `openai_judge` (requires `.[openai]`), `litellm_model` / `litellm_judge` (requires `.[litellm]`), and a built-in `MockModel` / `MockJudge` for offline use. Adding a new provider is 30–60 lines — see [`cab_ff/providers/`](cab_ff/providers/).

## CLI reference

```bash
# Smoke test (no API key)
make smoke
# or: python examples/quickstart.py

# Validate the dataset
python -m cab_ff.cli validate data/CAB_FF_v3_dataset.json

# Inspect the configuration
python -m cab_ff.cli dimensions      # 8 dimensions + 7 axes
python -m cab_ff.cli question-types  # 5 types with descriptions
python -m cab_ff.cli judges          # 9 personas with system prompts
python -m cab_ff.cli indicators --christian-only

# Sample 5 adversarial questions
python -m cab_ff.cli sample data/CAB_FF_v3_dataset.json -T adversarial -n 5

# Summarize a finished evaluation report
python -m cab_ff.cli summarize my-run.json
```

`make help` lists every Make target. `make stats` prints the live dataset breakdown.

## Documentation

| Doc | What it covers |
|---|---|
| [`docs/BENCHMARK_DESIGN.md`](docs/BENCHMARK_DESIGN.md) | What we measure and why (design rationale) |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the pipeline works (ASCII diagram) |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | Anti-gaming, reproducibility, honest validation status |
| [`docs/GLOO_COMPARISON.md`](docs/GLOO_COMPARISON.md) | Full Gloo FAI-C vs CAB-FF side-by-side |
| [`docs/FAQ.md`](docs/FAQ.md) | Cost / time / "is Faith over-weighted?" / etc. |
| [`docs/CAB_FF_METHODOLOGY.md`](docs/CAB_FF_METHODOLOGY.md) | Detailed methodology reference |
| [`docs/CAB_FF_DIMENSIONS.md`](docs/CAB_FF_DIMENSIONS.md) | All 8 dimensions + 7 axes in detail |
| [`docs/CAB_FF_SCHEMA.md`](docs/CAB_FF_SCHEMA.md) | JSON schema for the dataset |
| [`docs/ADVERSARIAL_PROBES.md`](docs/ADVERSARIAL_PROBES.md) | Adversarial-probe failure-mode taxonomy |
| [`rubrics/cab_ff_subjective_scoring.md`](rubrics/cab_ff_subjective_scoring.md) | Judge scoring rubric (0–100 bands) |
| [`rubrics/cab_ff_alignment_indicators.md`](rubrics/cab_ff_alignment_indicators.md) | All 40 binary indicators with detection hints |

## Status and roadmap

- **v3.0.1** (current) — **Production ready.** 1,056 questions, 47 tests passing, dataset validated, CI green. Methodology and code stable.
- **v3.1** (next) — Target 1,500+ questions, especially expanding Pentecostal / Methodist / Baptist tradition-tagged coverage, and adding more multi-turn dialogues. Community PRs welcomed.
- **v3.2 / paper** — Methodology paper for peer review. Public leaderboard with community-submitted baseline runs at [`results/baselines/`](results/baselines/).

See [`marketing/post_invite_baselines.md`](marketing/post_invite_baselines.md) for how to contribute a baseline run.

## Contributing

We want this to be the standard open Christian AI benchmark — and that requires more eyes, especially tradition-specific expertise. Three highest-value contributions:

1. **Audit a question for your tradition.** Open an issue with the `CABFF-NNNN` id, or PR an edit to the matching `cab_ff/banks/bank_*.py` and re-run `make build`. Use the **`question-quality`** issue template.
2. **Run CAB-FF against a frontier model and submit the report.** Drop the JSON into `results/baselines/` via a PR. Use the **`baseline-run`** issue template.
3. **Add a provider adapter or a new probe.** Each is a small, self-contained change.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Repository layout

```
cab_ff/                          # core package
  dimensions.py / loader.py      #   schema, filters, validation
  scorer.py / aggregator.py      #   5 scorers + geometric-mean composite
  alignment_indicators.py        #   40 binary YES/NO probes
  judges.py                      #   9 tradition-aware judge personas
  evaluator.py / cli.py          #   orchestrator + CLI
  providers/                     #   Anthropic, OpenAI, LiteLLM, mock
  banks/                         #   question banks
data/                            # assembled dataset + hand-authored seed
docs/                            # methodology, architecture, validation, FAQ
examples/                        # quickstart + minimal API stub
marketing/                       # launch copy (X / LinkedIn / blog / press)
rubrics/                         # subjective scoring + indicator references
scripts/                         # build_dataset.py
tests/                           # 47 tests
.github/                         # CI, issue + PR templates
cab_benchmark/                   # preserved v2.0 package (backward compat)
```

## Citation

```bibtex
@misc{cabff2026,
  title  = {{CAB-FF}: The Flourishing \& Faithfulness Benchmark for {AI} Alignment with Christian Faith},
  author = {{Soli Deo Gloria Research Initiative}},
  year   = {2026},
  url    = {https://github.com/moonshineaitech/SoliDeoGloria},
  note   = {Version 3.0.1. Released under CC BY-SA 4.0.}
}
```

A `CITATION.cff` is included at the repository root so GitHub's "Cite this repository" button works automatically.

## License

**CC BY-SA 4.0.** You are free to share, adapt, and use the methodology, code, judge prompts, alignment indicators, and full 1,056-question dataset — including commercially — under three conditions: attribute, share alike, and don't add legal restrictions others can't escape. See [LICENSE](LICENSE).

## Contact

- **Website:** [SoliDeoGloria.ai](https://SoliDeoGloria.ai)
- **Publisher:** Eldest AI LLC dba GoldRock AI
- **Issues:** [GitHub Issues](https://github.com/moonshineaitech/SoliDeoGloria/issues) (please use the templates)
- **Email:** research@solideogloria.ai

## Acknowledgments

CAB-FF builds on the Harvard Human Flourishing Program (whose seven dimensions Gloo's FAI-C framework also draws from), Barna Group and REVEAL research on faith formation, the historic confessional documents of the global Church, and CAB v2.0 (preserved under [`cab_benchmark/`](cab_benchmark/) for backward compatibility).

<p align="center"><em>Soli Deo Gloria — To God alone be the glory.</em></p>
