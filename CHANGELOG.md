# Changelog

All notable changes to the Christian AI Benchmark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **820-question assembled dataset** (`data/CAB_FF_v3_dataset.json`,
  rebuildable via `scripts/build_dataset.py`). Larger than Gloo's
  privately-held 807-question FAI-C set. Built from a 80-question
  hand-authored seed plus per-dimension and cross-cutting question
  banks under `cab_ff/banks/`. All 820 records validate against the
  v3 schema. Distribution:
    - Faith 385, Vocation & Witness 88, Character 82, Relationships 70,
      Health 61, Stewardship 45, Happiness 44, Meaning 41.
    - Objective 525, Subjective 124, Adversarial 104, Multi-turn 28,
      Comparative 39.
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
