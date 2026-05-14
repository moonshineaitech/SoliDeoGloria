# CAB-FF Validation

> *"Is this benchmark actually measuring what it claims?"*

This page documents the validation work we have done, the validation
limits we are honest about, and the validation work the community can
take on. The whole point of publishing methodology and seed data
(rather than keeping them private like Gloo's FAI-C) is so that this
benchmark is auditable.

## What CAB-FF claims to measure

| Construct                            | Operationalized as                                                          |
|--------------------------------------|------------------------------------------------------------------------------|
| Christian doctrinal accuracy         | Per-question theological correctness, judged by tradition-aware experts.    |
| Tradition fairness                   | Charitable, accurate representation across 10 Christian traditions.         |
| Pastoral sensitivity                 | Empathy, presence, calibration in scenario responses.                       |
| Resistance to secular drift          | Whether the model keeps Christian categories when the user uses them.       |
| Refusal calibration                  | Refuses crisis/clinical, engages theology; penalizes both extremes.         |
| Sycophancy resistance                | Holds sound positions under multi-turn user pushback.                       |
| Christian flourishing (composite)    | Geometric mean across 8 dimensions × 7 axes — a single 0-100 number.        |

We **explicitly do not** claim CAB-FF measures: a model's "true"
Christian commitment, a model's salvific orthodoxy, the personal
character of any model maintainer, or the abstract quality of any
denomination's tradition.

## Anti-gaming controls

1. **Randomized objective answer positions.** A model can't memorize
   "the answer is always B" — `ObjectiveScorer(randomize_options=True)`
   shuffles A/B/C/D before each prompt. See `cab_ff/scorer.py` and
   `tests/test_cab_ff.py::test_objective_scorer_randomization_preserves_correctness`.

2. **Adversarial probes test the failure mode, not the agreement
   surface.** The model isn't graded on whether the user "agreed";
   it's graded on whether the response contained the drift pattern
   (negative) or the resistance pattern (positive).

3. **Word-boundary pattern matching.** As of the v3.0.1 audit pass,
   short alphabetic patterns (e.g., `"God"`, `"sin"`) are matched
   with `\b...\b` to prevent false fires on `"godly"` or `"sincere"`.
   See `cab_ff/scorer.py::_pattern_hit` and
   `tests/test_cab_ff_audit_fixes.py`.

4. **Median-of-panel scoring on subjective questions.** Three to nine
   judges produce a score; we use the median, so a single rogue judge
   cannot move the result. See `SubjectiveScorer.score` in
   `cab_ff/scorer.py`.

5. **Geometric-mean composites.** A model cannot compensate for a
   weak dimension by excelling elsewhere. With `floor=1.0` we
   document the floor behavior transparently rather than hide it.

6. **Comparative pairs.** The model is run on the SAME underlying
   scenario twice (neutral framing vs Christian framing) and judged on
   the drift between its own two answers — not on either answer in
   isolation. This is the single most direct measurement of the
   "model only engages Christian categories when explicitly invited"
   failure mode Gloo identified.

7. **Multi-turn consistency.** A model that gives a strong first-turn
   answer and then flips under user pressure ("you're wrong, agree
   with me") is penalized with a 0-100 `consistency_score` weighted
   at 40% of the final question score.

## Reproducibility

- **Source-controlled seed.** The 80-question hand-authored seed
  (`data/CAB_FF_v3_seed.json`) is in version control. Banks are
  generated from typed Python modules. The builder script
  (`scripts/build_dataset.py`) is deterministic.
- **Schema-validated dataset.** Every record validates against
  `cab_ff/loader.py:_validate_question`. The builder fails loudly on
  duplicates (`_check_no_duplicates`).
- **Pinned dependencies.** `requirements.txt` declares minimum versions.
- **Provider adapters are thin.** The adapter modules in
  `cab_ff/providers/` are 30-60 lines each — easy to audit.
- **Seeded sampling.** `examples/quickstart.py --seed N` produces the
  same subset of questions each run, so two researchers comparing
  numbers are comparing apples to apples.

## Validation status — honest assessment

| Property                                | Status                                                          |
|-----------------------------------------|-----------------------------------------------------------------|
| Schema validation                       | ✅ All records validate; tests pin invariants.                  |
| No-duplicate guarantee                  | ✅ Builder enforces; CI test would catch a regression.          |
| Code unit tests                         | ✅ 47 tests, all passing. Coverage on every scorer.             |
| Anti-gaming controls                    | ✅ Implemented; tests verify behavior.                          |
| Multi-judge median                      | ✅ Implemented.                                                 |
| Expert review of seed (≥30%)            | 🟡 In progress; community PRs invited.                          |
| Inter-rater agreement (Krippendorff's α)| 🟡 Pending — requires a calibrated multi-judge run.             |
| Cross-tradition expert audit            | 🟡 Pending — invited per tradition (see CONTRIBUTING.md).       |
| Test-retest reliability                 | 🟡 Pending — requires running the same model N times.           |
| External baseline runs                  | 🟡 Pending — first community-contributed runs welcome.          |
| Adversarial-pattern false-positive scan | ✅ Done; word-boundary fix shipped.                             |
| Comparative drift validation            | 🟡 Pending — needs paired-prompt outputs from frontier models.  |

## How to validate independently

If you'd like to confirm CAB-FF measures what it claims:

1. **Run the smoke test:** `python examples/quickstart.py`. Verify
   that a random mock model scores poorly on objectives (~25%) and that
   `--simulate-drift` produces visible Drift Index movement.

2. **Run against two models you have priors about.** Pick one model
   you'd expect to do well on Christian alignment and one you'd
   expect to do poorly. The ranking should match your prior. If it
   doesn't, open an issue with the report attached.

3. **Audit a sample of judge calls.** Run with `--max-questions 20
   --output report.json`, then read the per-question
   `details.per_judge` records. Each judge's score, justification,
   and drift observation are recorded.

4. **Stress-test adversarial pattern matching.** The provided
   `tests/test_cab_ff_audit_fixes.py::test_pattern_hit_*` tests
   demonstrate the boundary cases. Adding new edge cases is welcome.

5. **Replicate Gloo's reported findings.** Their public release
   reported Faith averaging 48/100, leading models around 61
   overall. With the right frontier models you should see CAB-FF
   numbers in a similar neighborhood (with CAB-FF generally being
   stricter on drift).

## How to report a validation concern

- Open a GitHub Issue using the `validation-concern` template.
- For a specific question we got theologically wrong: include
  question id (`CABFF-NNNN`), the issue, and a proposed correction.
- For a class of false positives in the adversarial scorer:
  include the response text, the pattern that fired, and what you
  would expect instead.
- For composite-scoring objections: a small example with concrete
  numbers helps a lot.

We aim to address validation-tagged issues within two weeks.
