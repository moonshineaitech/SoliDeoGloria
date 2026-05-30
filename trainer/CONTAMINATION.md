# Test-set contamination prevention

CAB-FF is published. If we trained on the literal CAB-FF questions, the
benchmark would Goodhart immediately and the resulting model's scores would
be meaningless. This document explains how the trainer avoids that.

## The bright line

**The literal `data/CAB_FF_v3_dataset.json` records are NEVER used as
training targets.** Not as SFT supervision, not as DPO chosen responses,
not as GRPO prompts. The trainer enforces this with a content-hash check
at pipeline time and a fail-loud assertion.

What we DO use the dataset for:

1. **The failure-mode taxonomy.** Adversarial probes name specific drift
   patterns (`secular_drift_higher_power`, `fabricated_scripture`, etc.).
   These taxonomies guide synthetic-data generation, but the synthetic
   prompts are LEXICALLY DIFFERENT from the CAB-FF prompts.
2. **The judge rubric.** The CAB-FF subjective-scoring rubric (0-100
   bands, with named drift penalties) is reused as the reward signal for
   GRPO. The rubric itself isn't data — it's the loss function.
3. **The pattern lists.** The adversarial scorers' `failure_patterns` /
   `resistance_patterns` give us a vocabulary of drift-words and
   resistance-words. We use these to validate that synthetic responses
   actually demonstrate the right behavior. We don't include them as
   training targets.

## How the pipeline enforces this

Stage `01_seed_from_cab_ff.py` reads the dataset and extracts only:
- Question types and dimensions (for stratification)
- Probe targets (`probe_target` strings — taxonomy labels)
- Drift/resistance vocabulary lists (for synth validation)
- Rubric focus strings (paraphrased into synth prompts but not reused
  verbatim — see step 4 below)

It explicitly does NOT extract `question`, `scenario`, `options`,
`prompts.neutral`, `prompts.christian`, `turns[].content`, or
`correct_answer`.

Stage `02_generate_responses.py` constructs synthetic prompts from
templates (`PROMPT_TEMPLATES` in the file) parameterized by:
- Tradition
- Dimension
- Failure mode being targeted (so we can teach resistance)
- A randomly-sampled "scenario seed" — a SHORT topic phrase like
  "prayer practice" or "grief after stillbirth" — that overlaps in
  topic but not in exact wording with CAB-FF.

The synthetic prompts are then fed to a teacher LLM (Claude / GPT-4o)
to generate gold responses.

Stage `06_dedup_and_filter.py` runs a SimHash-based near-duplicate check:
- Every generated training example is hashed.
- The check fails loud if any training example's SimHash falls within
  Hamming distance ≤ 5 of any CAB-FF question's SimHash.
- This catches both verbatim leakage and trivial paraphrases.

## How CAB-FF eval stays meaningful after we train

After training, when we run `make eval`, the model is evaluated on the
LITERAL CAB-FF dataset. Since the trainer never showed those exact
questions to the model, the eval is honest — but the model has been
trained to handle the underlying failure modes, so we expect (and aim
for) substantially higher scores than the base model.

The decision rule in `eval/gating.py`:

```
Promote checkpoint X over base B iff:
   X.cab_ff_score      ≥ B.cab_ff_score      + 5    # absolute improvement
   X.drift_index       ≤ B.drift_index       - 10   # less drift
   X.sycophancy_index  ≤ B.sycophancy_index  - 10   # less sycophancy
   X.faithfulness_index ≥ B.faithfulness_index + 5
   AND for each dimension d: X.by_dimension[d] ≥ B.by_dimension[d] - 3
       (no significant regression on any single dimension)
```

These thresholds prevent us from shipping a model that only optimized
for the composite while regressing on, say, Mental & Physical Health
(which is heavy on crisis-referral safety probes).

## Reviewing this guarantee

The contamination check is implemented in
[`trainer/data/pipeline/06_dedup_and_filter.py`](trainer/data/pipeline/06_dedup_and_filter.py)
and verified by the test
`tests/test_contamination.py::test_no_cab_ff_text_in_training_data`.

If you find a contamination case the test missed, please open an issue
with the `validation` label. Contamination concerns get triaged within
48 hours.

## Common questions

**Q: Doesn't the model still "see" Christian theology in pretraining?**
Yes — and that's fine. The base model's general theological knowledge
isn't the eval target. CAB-FF measures specific BEHAVIORS (does the
model substitute "higher power" for God? does it fabricate Scripture?
does it hold a position under pushback?). Behaviors can be trained
independent of background knowledge.

**Q: What about the Bible and the historic creeds? You train on those.**
Yes — those are public domain and not part of the CAB-FF dataset.
Pretraining on Scripture doesn't leak the CAB-FF eval questions.

**Q: What if my training data accidentally paraphrases a CAB-FF
question?** The SimHash check catches Hamming ≤ 5 near-duplicates.
Beyond that, paraphrases of theological scenarios are inevitable —
"How do I forgive my friend?" and "I need to forgive someone, what do I
do?" cover similar ground. The eval is robust to this because (a) the
judge rubric grades the response content, not surface similarity to the
training data, and (b) the held-out 80-question hand-authored seed in
`data/CAB_FF_v3_seed.json` is sacrosanct — even the bank-generated 976
are kept separate.

**Q: Can I see the training data?** Yes — after running `make data`, the
output JSONL files in `data/built/` are inspectable. We recommend
spot-checking 20-50 examples before launching SFT.
