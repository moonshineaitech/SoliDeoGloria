# CAB-FF Eval Report

**Model:** `$REPO`
**Base:** `$BASE_MODEL`
**Eval dataset:** CAB-FF v3.0 (1,056 questions)
**Judge:** $JUDGE
**Date:** $DATE

## Summary

| Metric | Score |
|---|---:|
| **CAB-FF Score** (composite) | **$CAB_FF** / 100 |
| Flourishing Score | $FLOURISHING |
| Faithfulness Index | $FAITHFULNESS |
| Drift Index *(lower is better)* | $DRIFT |
| Sycophancy Index *(lower is better)* | $SYCOPHANCY |

## vs base model

$DELTA_TABLE

## Per-dimension breakdown

$BY_DIMENSION

## Per-axis breakdown (faithfulness lenses)

$BY_AXIS

## Methodology

See [CAB-FF methodology](https://github.com/moonshineaitech/SoliDeoGloria/blob/main/docs/CAB_FF_METHODOLOGY.md).

## How to verify

```bash
git clone https://github.com/moonshineaitech/SoliDeoGloria
cd SoliDeoGloria
pip install -e .
python -m trainer.eval.run_cab_ff \
    --backend vllm \
    --checkpoint $REPO \
    --dataset data/CAB_FF_v3_dataset.json \
    --judge $JUDGE \
    --out my_verification_report.json
```
