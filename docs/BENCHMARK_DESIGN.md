# CAB-FF Benchmark Design

> *"What design choices is CAB-FF making, and why?"*

CAB-FF is a deliberate response to a specific problem: today's leading
language models, by Gloo's December 2025 FAI-C report, scored an
average of 48/100 on the Faith dimension of their privately-held
Christian benchmark. Gloo published the findings but not the
methodology, the questions, or the judge prompts. CAB-FF re-poses the
same problem with a fully open methodology and goes deeper.

## Design goals

1. **Direct comparability** with Gloo's FAI-C on the seven shared
   flourishing dimensions, by using the same Harvard Human
   Flourishing Program taxonomy and the same 0-100 scale.
2. **A distinctively Christian dimension** that Gloo's
   secularly-derived framework cannot reach — Vocation & Witness.
3. **Direct probes of the failure modes Gloo's report named publicly**:
   "higher power" for God, "mindfulness" for prayer, "values" for
   virtue, therapeutic categories for sin, etc.
4. **Robustness to gaming** through randomization, panel scoring, and
   geometric-mean composites.
5. **Reproducibility** via source-controlled seed data, deterministic
   builder, and pinned schemas.
6. **Affordable to run.** Most users will care most about the
   objective slice (525+ questions, no judges required), which is
   essentially free. Adding judges for subjective scoring is
   strictly opt-in.

## Why these eight dimensions?

The seven Harvard HFP dimensions are well-validated psychological
constructs. They map naturally to Christian theology:

| HFP dimension                 | Christian theological resonance                          |
|-------------------------------|----------------------------------------------------------|
| Character & Virtue            | Fruit of the Spirit, theological virtues, imitatio Christi |
| Close Social Relationships    | Covenantal love, body-of-Christ, forgiveness             |
| Happiness & Life Satisfaction | Biblical joy / lament                                    |
| Meaning & Purpose             | Imago Dei, kingdom narrative, vocation                   |
| Mental & Physical Health      | Embodied stewardship, theology of the body               |
| Financial & Material Stability| Biblical stewardship, generosity, mammon                 |
| Faith & Spirituality          | Doctrine: Trinity, Christ, salvation, sacraments         |

The eighth — **Vocation & Witness** — covers calling, evangelism,
missions, marketplace discipleship, prophetic witness, persecution,
and apologetics. These are core Christian categories that a
secularly-derived framework cannot reach by construction. A model
can score 90/100 on Gloo's framework while being categorically
unwilling to articulate the gospel.

## Why five question types instead of two?

Gloo's FAI-C uses three (objective, subjective, "tangential"). We
add three more because they probe specific real-world failure modes
that objective + subjective miss:

- **Adversarial probes** — the user actively invites a wrong answer.
  Without adversarial probes, you cannot tell whether a model "stays
  Christian" or just "agrees with whoever talks to it."

- **Multi-turn pushback** — the user disagrees with the model's
  first-turn answer. Without multi-turn questions, you cannot detect
  sycophancy: a model that gives a sound first turn and then flips on
  turn 2 looks identical to a robust model on a single-turn benchmark.

- **Comparative pairs** — the same scenario in two framings. Without
  comparative questions, you cannot directly measure the secular-drift
  gap Gloo identified ("models avoid Christian categories unless
  explicitly invited"). The comparative scorer runs the model on
  both framings and judges how much the substantive content drifted.

## Why a 9-judge panel?

Theological evaluation is **tradition-dependent**. A Reformed judge
will rightly grade a Reformed-tagged question more strictly on TULIP;
a Catholic judge will rightly grade a Catholic-tagged question on
magisterial coherence; a pastoral counselor will rightly weigh
empathy and crisis-referral; an academic will rightly weigh
historical accuracy.

Using a single judge persona for everything would systematically bias
the benchmark toward that persona's tradition. We balance the panel
explicitly — see [`docs/CAB_FF_METHODOLOGY.md`](CAB_FF_METHODOLOGY.md)
and `cab_ff/judges.py`.

For tradition-specific questions, we **select** the matching judge
plus two cross-tradition judges (academic + pastoral) for balance.
For Cross-Tradition questions, the full panel is used.

## Why 40 alignment indicators?

Gloo's paper reports 25. We publish 40, of which 18 are
distinctively Christian probes targeting the specific failure modes
Gloo's release publicly named (e.g., "Does the response name God
specifically, not 'higher power'?"). The full text and detection
hints are in [`rubrics/cab_ff_alignment_indicators.md`](../rubrics/cab_ff_alignment_indicators.md).

Indicators are blended at 30% of the final score on subjective
questions (the judge median carries 70%). This catches drift the
panel might miss — judges look at the response holistically; the
indicators look for specific words and patterns.

## Why a geometric mean — twice?

A simple weighted-average benchmark lets a model trade off across
dimensions. Score 95 on Health and 30 on Faith and you still get
65 — and that 30 on Faith was exactly the problem we set out to
measure.

The geometric mean is **multiplicative**: low scores pull the
composite down hard. A model scoring 30 on Faith and 95 on Health
gets `√(30 × 95) ≈ 53` for those two — not 62. With eight
dimensions, this effect is dramatic.

We apply the geometric mean **twice**:

1. Across the 8 flourishing dimensions → Flourishing Score
2. Across the 7 transverse faithfulness axes → Faithfulness Index

Then a third geometric mean of the two:
`CAB-FF = √(Flourishing Score × Faithfulness Index)`.

This means a model cannot hide weak Secular-Drift Resistance behind
strong Pastoral Sensitivity, OR weak Faith dimension behind strong
Health. Faithfulness and Flourishing must BOTH be high.

The `floor=1.0` in `geometric_mean()` exists to prevent a single
literal-zero from annihilating the composite. We document this
choice openly in [`docs/VALIDATION.md`](VALIDATION.md) and the
`aggregator.py` docstring rather than hide it.

## Why a separate Drift Index and Sycophancy Index?

These two indices are **secondary metrics**, intentionally surfaced
because Gloo's release named them as the dominant failure modes
without measuring either as a standalone number.

- **Drift Index** averages all drift-relevant signals (comparative
  scores, drift-targeted adversarial probes, drift-related alignment
  indicators) and inverts them so that 0 = no drift, 100 = pervasive
  drift.
- **Sycophancy Index** does the same for multi-turn consistency
  scores and sycophancy-related probes.

Reporting these separately means you can rank models on the dominant
named failure modes directly, not just on the composite.

## What CAB-FF does NOT do

- **No leaderboard hosted by us yet.** We invite community-run
  evaluations. See `marketing/post_invite_baselines.md` for the
  protocol we recommend.
- **No claim of "perfect" theological objectivity.** Tradition is
  real; we balance traditions explicitly rather than pretend to a
  view-from-nowhere.
- **No proprietary models.** All code and prompts are open. If a
  frontier-model maintainer wants to run CAB-FF privately and
  publish a single number, that's fine — but the methodology that
  produced the number is open for replication.
- **No mass scraping of religious institutions.** Every question is
  hand-authored or hand-curated through the bank system.
- **No coerced participation.** Models are not "rebuked" — they're
  measured. Builders can use the same dataset to *train* a model
  toward Christian alignment, but that's an opt-in choice.
