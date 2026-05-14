# Christian AI Benchmark (CAB) — v3.0 "Flourishing & Faithfulness"

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Version](https://img.shields.io/badge/Version-3.0.0-blueviolet.svg)]()
[![Questions](https://img.shields.io/badge/Questions-820-red.svg)]()
[![Dimensions](https://img.shields.io/badge/Dimensions-8-green.svg)]()
[![Axes](https://img.shields.io/badge/Faithfulness%20Axes-7-orange.svg)]()
[![Types](https://img.shields.io/badge/Question%20Types-5-blue.svg)]()

CAB-FF is a rigorous, fully-open benchmark for evaluating AI systems on
Christian flourishing and faithfulness. It is a deliberate successor to
CAB v2.0 and a public response to Gloo's privately-held **FAI-C
Benchmark** (December 2025).

## At a Glance

| | Gloo FAI-C | **CAB-FF v3.0** |
|---|---|---|
| Question count | 807 (private) | **820 (published)** |
| Dimensions | 7 | **8** (+ Vocation & Witness) |
| Cross-cutting faithfulness axes | implicit | **7 explicit, scored** |
| Question types | obj + subj + tangential | **5: + adversarial, multi-turn, comparative** |
| Alignment indicators | 25 (private) | **40 (published, with hints)** |
| Judge panel | undisclosed | **9 named tradition-aware personas** |
| Drift Index | implicit | **explicit secondary metric** |
| Sycophancy Index | not measured | **explicit secondary metric** |
| Methodology | partially private | **fully open** |
| License | proprietary | CC BY-SA 4.0 |

See [`docs/GLOO_COMPARISON.md`](docs/GLOO_COMPARISON.md) for the full
comparison and where CAB-FF directly probes the failure modes Gloo
publicly identified.

## The Eight Dimensions

The seven Harvard Human Flourishing Program dimensions Gloo uses, plus
one that secular flourishing frameworks cannot reach by construction:

1. Character & Virtue (chi)
2. Close Social Relationships (rho)
3. Happiness & Life Satisfaction (eta)
4. Meaning & Purpose (mu)
5. Mental & Physical Health (psi)
6. Financial & Material Stewardship (phi)
7. Faith & Spirituality (sigma)
8. **Vocation & Witness (omega) — NEW**

See [`docs/CAB_FF_DIMENSIONS.md`](docs/CAB_FF_DIMENSIONS.md).

## The Seven Transverse Axes

Every response is graded against:

- Doctrinal Fidelity, Scriptural Grounding, Tradition Fairness,
  Pastoral Sensitivity, **Secular-Drift Resistance**, **Refusal
  Calibration**, **Sycophancy Resistance**.

## The Five Question Types

| Type | Purpose |
|---|---|
| `objective` | Verifiable multiple-choice factual |
| `subjective` | Open scenario, judge-panel scored |
| `adversarial` | Probes for documented failure modes (secular drift, fabricated Scripture, sycophancy, refusal miscalibration) |
| `multi_turn` | 2-4 turn dialogue with pushback; tests consistency |
| `comparative` | Paired Christian-vs-neutral framing of the same scenario; directly measures drift |

See [`docs/ADVERSARIAL_PROBES.md`](docs/ADVERSARIAL_PROBES.md) for the
adversarial-probe taxonomy.

## Scoring Formula

```
Flourishing Score (FF)     = ⁸√(chi · rho · eta · mu · psi · phi · sigma · omega)
Faithfulness Index (FI)    = ⁷√(7 transverse axis scores)
Final CAB-FF Score         = √(FF · FI)

Drift Index                = 100 − mean(drift signals)        (lower is better)
Sycophancy Index           = 100 − mean(sycophancy signals)   (lower is better)
```

The geometric mean is intentional: a model cannot hide a 30/100 Faith
score behind a 90/100 Health score, and a model cannot hide a 30/100
Anti-Drift score behind a 90/100 Pastoral score.

## Quick Start

```bash
pip install -r requirements.txt

# Validate the seed dataset
python -m cab_ff.cli validate data/CAB_FF_v3_seed.json

# List the 8 dimensions and 7 transverse axes
python -m cab_ff.cli dimensions

# List the 5 question types
python -m cab_ff.cli question-types

# List the 9 judge personas
python -m cab_ff.cli judges

# List the 40 alignment indicators
python -m cab_ff.cli indicators --christian-only

# Sample 5 adversarial questions
python -m cab_ff.cli sample data/CAB_FF_v3_seed.json -T adversarial -n 5
```

## Python API

```python
from cab_ff import CABFFEvaluator
from cab_ff.evaluator import EvaluationConfig

def my_model(prompt: str) -> str: ...
def my_judge(system: str, user: str) -> str: ...

evaluator = CABFFEvaluator(
    model_fn=my_model,
    judge_fn=my_judge,
    config=EvaluationConfig(apply_alignment_indicators=True),
)
report = evaluator.evaluate("data/CAB_FF_v3_seed.json")
print(report["summary"]["cab_ff_score"])
```

A minimal stub example lives at
[`examples/cab_ff_example.py`](examples/cab_ff_example.py).

## Repository Layout

```
cab_ff/                          # v3.0 package
  __init__.py
  dimensions.py                  # 8 dims, 7 axes, 5 types
  judges.py                      # 9 judge personas + panel
  alignment_indicators.py        # 40 binary indicators
  scorer.py                      # ObjectiveScorer, SubjectiveScorer,
                                 #   AdversarialScorer, MultiTurnScorer,
                                 #   ComparativeScorer, AlignmentIndicatorScorer
  aggregator.py                  # FF, FI, CAB-FF, Drift, Sycophancy
  evaluator.py                   # CABFFEvaluator orchestrator
  loader.py                      # schema validation
  cli.py                         # python -m cab_ff.cli
  banks/                         # question banks (per dimension + cross-cutting)
    bank_faith.py                #   - Faith & Spirituality
    bank_character.py            #   - Character & Virtue
    bank_witness.py              #   - Vocation & Witness (NEW)
    bank_relationships.py        #   - Close Social Relationships
    bank_health.py               #   - Mental & Physical Health
    bank_happiness.py            #   - Happiness & Life Satisfaction
    bank_meaning.py              #   - Meaning & Purpose
    bank_stewardship.py          #   - Financial & Material Stewardship
    bank_cross_cutting.py        #   - drift / sycophancy / refusal probes
    bank_extras.py / extras_two  #   - additional objective coverage
    _helpers.py                  #   - obj() subj() adv() multi() comp() U()

cab_benchmark/                   # v2.0 package (preserved)

data/
  CAB_FF_v3_dataset.json         # 820-question assembled dataset (v3.0)
  CAB_FF_v3_seed.json            # 80-question hand-authored seed
  CAB_v2_Dataset_965.json        # v2.0 dataset (preserved)

scripts/
  build_dataset.py               # assembles banks + seed -> dataset JSON

docs/
  CAB_FF_METHODOLOGY.md
  CAB_FF_DIMENSIONS.md
  CAB_FF_SCHEMA.md
  GLOO_COMPARISON.md
  ADVERSARIAL_PROBES.md
  METHODOLOGY.md / DIMENSIONS.md / SCHEMA.md / TRADITIONS.md  (v2.0)

rubrics/
  cab_ff_subjective_scoring.md
  cab_ff_alignment_indicators.md
  subjective_scoring.md / objective_scoring.md                 (v2.0)

tests/
  test_cab_ff.py
  test_loader.py                 (v2.0)
```

## Dataset Statistics (assembled, v3.0)

The assembled dataset at `data/CAB_FF_v3_dataset.json` contains
**820 questions** (more than Gloo's 807) covering all 8 dimensions
and all 5 question types:

```
820 questions
  by_dimension:
    Character & Virtue:                84
    Close Social Relationships:        72
    Faith & Spirituality:             385
    Financial & Material Stewardship:  45
    Happiness & Life Satisfaction:     44
    Meaning & Purpose:                 41
    Mental & Physical Health:          61
    Vocation & Witness:                88
  by_type:
    objective:    525
    subjective:   124
    adversarial:  104
    multi_turn:    28
    comparative:   39
  by_tradition:
    Cross-Tradition:  675
    Catholic:          53
    Reformed:          32
    Orthodox:          16
    Lutheran:          13
    Pentecostal:        9
    Anglican:           8
    Methodist:          7
    Baptist:            4
    Evangelical:        3
  by_difficulty:
    L1: 144   L2: 378   L3: 298
```

### How the dataset is built

The 820-question dataset is **assembled** from the 80-question
hand-authored seed (`data/CAB_FF_v3_seed.json`) plus a set of
per-dimension and cross-cutting question banks under `cab_ff/banks/`.
Rebuild any time with:

```bash
python scripts/build_dataset.py
```

This regenerates `data/CAB_FF_v3_dataset.json` with sequential
`CABFF-NNNN` IDs and validates every record against the schema.

### Roadmap

The v3.1 target is 1500+ questions. To contribute, add a Python file
under `cab_ff/banks/bank_<topic>.py` exporting a `QUESTIONS` list using
the helper constructors in `cab_ff/banks/_helpers.py`, then rerun the
builder. See [`docs/CAB_FF_SCHEMA.md`](docs/CAB_FF_SCHEMA.md) and
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citation

```bibtex
@misc{cabff2026,
  title  = {CAB-FF: The Flourishing & Faithfulness Benchmark for AI Alignment with Christian Faith},
  author = {GoldRock AI / Soli Deo Gloria Research Initiative},
  year   = {2026},
  url    = {https://github.com/GoldRockAI/cab-benchmark}
}
```

## License

CC BY-SA 4.0. Share, adapt, attribute, share-alike. Methodology, code,
and seed dataset are all open.

## Contact

- **Website:** [SoliDeoGloria.ai](https://SoliDeoGloria.ai)
- **Publisher:** Eldest AI LLC dba GoldRock AI
- **Issues:** GitHub Issues

## Acknowledgments

Developed as part of the Soli Deo Gloria Research Initiative. CAB-FF
builds on the work of the Harvard Human Flourishing Program (which Gloo's
framework also draws from), the Barna Group and REVEAL on faith
formation, and the historic doctrinal traditions of the global
Church.
