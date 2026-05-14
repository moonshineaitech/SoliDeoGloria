# Changelog

All notable changes to the Christian AI Benchmark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2026-05-14 — Audit, fixes, expansion

### Fixed
- **`cab_ff/evaluator.py`** — `composite_blend` metadata previously
  recorded `None` for `base_score`. Now records the actual pre-blend
  judge score. (Regression test added.)
- **`cab_ff/scorer.py`** — Adversarial pattern matching now uses
  word boundaries for short alphabetic patterns, so e.g. the
  resistance pattern `"God"` no longer fires on `"godly"` nor `"sin"`
  on `"sincere"`. Multi-word and regex patterns are preserved as-is.
- **`cab_ff/scorer.py`** — JSON extraction from judge responses now
  uses balanced-brace scanning (string-aware) instead of a greedy
  `\\{.*\\}` regex. Stray `{` or `}` characters inside judge
  justifications no longer cause parse failures.
- **`scripts/build_dataset.py`** — Builder enforces no duplicate
  scenarios across the seed and banks, with a clear error listing the
  positions of any duplicates.
- Removed 5 duplicate scenarios that were present in both the seed
  and the bank modules.

### Added
- **236 new questions** taking the assembled dataset from 820 to
  **1,056**. Specific coverage improvements:
    - Tradition shortage closed: Baptist 4 → 21, Evangelical 3 → 16,
      Methodist 7 → 24, Anglican 8 → 26, Pentecostal 9 → 25,
      Lutheran 13 → 29, Orthodox 16 → 30.
    - Dimension shortage closed: Meaning 41 → 79, Happiness 44 → 71,
      Stewardship 45 → 79.
    - L1 (foundational) questions: 144 → 192.
    - Multi-turn dialogues: 28 → 42.
    - Comparative pairs: 39 → 48.
- **New bank modules** under `cab_ff/banks/`:
  `bank_tradition_deep_one.py`, `bank_tradition_deep_two.py`,
  `bank_meaning_more.py`, `bank_happiness_more.py`,
  `bank_stewardship_more.py`, `bank_foundations.py`.
- **19 new tests** under `tests/test_cab_ff_audit_fixes.py` covering
  the JSON extractor, the word-boundary pattern matcher, the
  SubjectiveScorer panel/median logic, MultiTurnScorer dialogue
  blending, ComparativeScorer, aggregator edge cases, and the
  `composite_blend.base_score` regression.

## [3.0.0] - 2026-05-14

### Added — CAB v3.0 "Flourishing & Faithfulness" (CAB-FF)
- New `cab_ff` package alongside the v2.0 `cab_benchmark` package.
- **8 dimensions**: the 7 Harvard Human Flourishing Program dimensions
  (Character, Relationships, Happiness, Meaning, Health, Finances, Faith)
  plus a distinctively Christian eighth dimension **Vocation & Witness**.
- **7 transverse faithfulness axes** scored cross-dimensionally:
  Doctrinal Fidelity, Scriptural Grounding, Tradition Fairness, Pastoral
  Sensitivity, Secular-Drift Resistance, Refusal Calibration,
  Sycophancy Resistance.
- **5 question types** (vs. v2.0's 2): objective, subjective,
  **adversarial**, **multi_turn**, **comparative**.
- **9-judge tradition-aware panel** with published persona prompts.
- **40 alignment indicators** (vs. Gloo FAI's 25), 18 of them
  distinctively Christian, with detection hints.
- **Composite scoring**: CAB-FF = sqrt(Flourishing Score x Faithfulness
  Index); plus secondary Drift Index and Sycophancy Index.
- **Assembled dataset** at `data/CAB_FF_v3_dataset.json`, rebuildable
  via `scripts/build_dataset.py`. Larger than Gloo's privately-held
  807-question FAI-C set. Built from an 80-question hand-authored seed
  plus per-dimension and cross-cutting question banks under
  `cab_ff/banks/`. All records validate against the v3 schema and the
  builder enforces no-duplicates. See `README.md` for the current
  distribution by dimension, type, tradition, and difficulty.
- Full methodology, schema, dimensions, Gloo-comparison, and
  adversarial-probe documentation under `docs/`.
- New CLI: `python -m cab_ff.cli` with subcommands `validate`,
  `dimensions`, `question-types`, `judges`, `indicators`, `sample`,
  `summarize`.

### Compatibility
- v2.0 (`cab_benchmark`) is preserved and continues to work unchanged.

## [2.0.0] - 2026-01-31

### Added
- Complete dataset of 991 unique questions
- 10 theological dimensions with comprehensive coverage
- 10 denominational traditions represented fairly
- Dual scoring modes (objective and subjective)
- LLM judge panel evaluation methodology
- Geometric mean aggregation for robust scoring
- Comprehensive evaluation scripts
- Detailed rubrics for subjective evaluation
- Full documentation and examples

### Changed
- Complete rebuild from v1.0 methodology
- Improved question uniqueness (100% unique)
- Enhanced tradition-specific questions
- Better balance across dimensions

### Fixed
- Eliminated all duplicate questions from v1.0
- Corrected theological inaccuracies
- Improved rubric specificity

## [1.0.0] - 2026-01-30

### Added
- Initial benchmark release
- Basic question set

### Known Issues
- Question duplication (fixed in v2.0)
