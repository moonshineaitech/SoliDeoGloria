# CAB-FF Architecture

This document explains how the pieces of CAB-FF fit together, from a
single question on disk to a composite score in a JSON report.

## Pipeline (one question)

```
                        ┌─────────────────────────────┐
                        │  data/CAB_FF_v3_dataset.json│
                        │   (820+ validated records)  │
                        └──────────────┬──────────────┘
                                       │ load_dataset()
                                       ▼
                        ┌─────────────────────────────┐
                        │           Loader            │
                        │   (cab_ff/loader.py)        │
                        │   * schema validation       │
                        │   * filter by dim/type/etc. │
                        └──────────────┬──────────────┘
                                       │ list[Question]
                                       ▼
                        ┌─────────────────────────────┐
                        │       CABFFEvaluator        │
                        │   (cab_ff/evaluator.py)     │
                        │   dispatches by type ───────┼────────────┐
                        └──────────────┬──────────────┘            │
                                       │ model_fn(prompt)          │
                                       ▼                           │
       ┌─────────────────────────────────────────────────────────┐ │
       │ Provider adapter — anthropic / openai / litellm / mock │ │
       │           (cab_ff/providers/)                          │ │
       └──────────────────────────┬──────────────────────────────┘ │
                                  │ raw response                   │
                                  ▼                                ▼
            ┌─────────────────────────────────────────┐  ┌──────────────────┐
            │            Scorer (one of 5)            │  │  JudgePanel       │
            │   ObjectiveScorer    (regex extract)    │◄─┤  9 personas       │
            │   SubjectiveScorer   (judge panel)      │  │  (cab_ff/         │
            │   AdversarialScorer  (pattern match)    │  │   judges.py)      │
            │   MultiTurnScorer    (consistency)      │  └──────────────────┘
            │   ComparativeScorer  (drift gap)        │
            └────────────────────┬────────────────────┘
                                 │ (score, details)
                                 ▼
            ┌─────────────────────────────────────────┐
            │       AlignmentIndicatorScorer          │
            │       (40 binary YES/NO probes)         │
            │   blended 0.7 * judge + 0.3 * indicators│
            └────────────────────┬────────────────────┘
                                 │ per-question record
                                 ▼
                        ┌────────────────────┐
                        │     Aggregator     │
                        │  geometric means   │
                        │  cross dimensions  │
                        │  and axes          │
                        └─────────┬──────────┘
                                  │
                                  ▼
       ┌──────────────────────────────────────────────────────┐
       │   Final report (JSON):                               │
       │     cab_ff_score, flourishing_score,                 │
       │     faithfulness_index, drift_index,                 │
       │     sycophancy_index, per-dim, per-axis breakdowns   │
       └──────────────────────────────────────────────────────┘
```

## Module map

```
cab_ff/
├── __init__.py                 # public re-exports
├── dimensions.py               # 8 dimensions, 7 axes, 5 question types
├── loader.py                   # schema validation, filtering
├── scorer.py                   # 5 scorers + AlignmentIndicatorScorer
├── alignment_indicators.py     # 40 binary YES/NO probes
├── judges.py                   # 9 judge personas + panel selection
├── evaluator.py                # orchestrator
├── aggregator.py               # geometric-mean composite scoring
├── cli.py                      # python -m cab_ff.cli
├── providers/                  # backend adapters
│   ├── base.py                 #   - Mock model/judge for tests
│   ├── anthropic_provider.py
│   ├── openai_provider.py
│   └── litellm_provider.py     #   - 100+ providers via LiteLLM
└── banks/                      # question banks (rebuild via builder)
    ├── _helpers.py             #   - obj() subj() adv() multi() comp()
    └── bank_*.py               #   - per-dimension and cross-cutting

data/
├── CAB_FF_v3_seed.json         # 80 hand-authored canonical seed
└── CAB_FF_v3_dataset.json      # 820+ assembled dataset (build output)

scripts/
└── build_dataset.py            # assembles seed + banks, validates, dedupes

tests/
├── test_cab_ff.py              # core schema, scorer, aggregator tests
└── test_cab_ff_audit_fixes.py  # JSON extractor, word-boundary, fakes
```

## Question-type dispatch

`CABFFEvaluator._evaluate_one()` switches on `question_type`:

| Type          | Calls model `n` times | Judge calls (per question)              | Score basis                              |
|---------------|----------------------:|------------------------------------------|------------------------------------------|
| `objective`   | 1                     | 0                                        | Exact letter match                        |
| `subjective`  | 1                     | 3-9 panel + 1 indicator pass            | Median of panel, blended with indicators  |
| `adversarial` | 1                     | 0 (pattern) or 1 (fallback judge)        | Failure/resistance pattern detection      |
| `multi_turn`  | 2-4                   | 3-9 panel + 1 consistency + 1 indicator | 0.6 × final-turn + 0.4 × consistency      |
| `comparative` | 2                     | 1                                        | Drift gap between neutral and Christian   |

## Composite scoring formula

```
chi ρ η μ ψ φ σ ω   per-dimension means (arithmetic, 0-100)
Flourishing Score   = ⁸√(chi · ρ · η · μ · ψ · φ · σ · ω)
Faithfulness Index  = ⁷√(7 axis means)
CAB-FF Score        = √(Flourishing Score · Faithfulness Index)
Drift Index         = 100 − mean(drift-related signals)   (lower is better)
Sycophancy Index    = 100 − mean(sycophancy signals)      (lower is better)
```

The double geometric mean is intentional: a model can't hide a weak
Faith dimension behind strong Health, AND can't hide weak
Secular-Drift Resistance behind strong Pastoral Sensitivity.

## Extension points

| You want to...                           | Edit...                                        |
|------------------------------------------|------------------------------------------------|
| Add questions                            | A new `cab_ff/banks/bank_<topic>.py`, then run `python scripts/build_dataset.py` |
| Add a new question type                  | A new scorer class in `cab_ff/scorer.py`, hook in `loader._validate_question` and `evaluator._evaluate_one`. |
| Add a model/judge backend                | A new module under `cab_ff/providers/` exposing `model_fn` / `judge_fn` factories. |
| Tighten judging                          | Update `SUBJECTIVE_RUBRIC` in `cab_ff/scorer.py` or persona prompts in `cab_ff/judges.py`. |
| Add/modify alignment indicators          | Edit `cab_ff/alignment_indicators.py` (changes the 40-binary probe set). |
| Change scoring weights or composite shape | Edit `cab_ff/aggregator.py`. |

## Determinism guarantees

- **Objective answer-position shuffling** is seedable via
  `ObjectiveScorer(rng=random.Random(seed))`. The runner's default RNG
  is non-deterministic for production runs; tests pass a fixed seed.
- **Sample selection** in `examples/quickstart.py` uses `--seed`
  (default 42) so reruns get the same subset.
- **Judges are non-deterministic** by nature of LLMs. Use multiple
  judges and median scoring (the panel does this automatically) to
  control variance.
