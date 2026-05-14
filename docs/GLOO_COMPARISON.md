# CAB-FF v3.0 vs. Gloo FAI-C — Side-by-Side

## What Gloo Has Published

Gloo's Flourishing AI Christian (FAI-C) Benchmark was unveiled
December 15, 2025. From publicly available sources (press releases,
the July 2025 FAI methodology paper at arXiv:2507.07787, Gloo blog,
and Gloo's flourishing-hub site):

- **807 curated questions** for FAI-C (FAI baseline: ~1,229)
- **7 dimensions:** Character, Relationships, Happiness, Meaning,
  Health, Finances, Faith
- **3 scoring modes:** objective, subjective, **tangential**
- **25 alignment indicators** (yes/no, 0/1)
- **Multiple judge LLMs with specialized expert personas** —
  personas, prompts, and weights are NOT public
- **Geometric mean** across dimensions:
  `FAI = ⁷√(χ × ρ × η × μ × ψ × φ × σ)`
- **0-100 scale;** leading models average **61**; **Faith is the
  weakest dimension** at average **48**
- **Detailed methodology paper to be submitted for peer review in early 2026**
- Findings from FAI-C: models swap "higher power" for God,
  "mindfulness" for prayer, "values" for virtue; struggle with image
  of God, sin, sanctification, biblical stewardship; default to
  non-judgement / emotional comfort

## What Gloo Does NOT Publish

- The 807 questions
- The 25 alignment indicators
- The judge persona system prompts
- Per-dimension question counts
- Refusal handling
- Reproducibility kit / per-question results format
- Drift or sycophancy as explicit secondary metrics
- Inter-rater agreement statistics

## What CAB-FF Adds

| Capability | Gloo FAI-C | CAB-FF v3.0 |
|---|---|---|
| Dimensions | 7 | **8** (+ Vocation & Witness) |
| Cross-cutting axes | implicit | **7 explicit, scored** |
| Question types | 3 (obj/subj/tangential) | **5** (+ adversarial, multi-turn, comparative) |
| Alignment indicators | 25 (private) | **40 published, with detection hints** |
| Judge panel | undisclosed | **9 personas, named and prompt-published** |
| Drift Index | implicit | **explicit, dedicated probes + comparative pairs** |
| Sycophancy Index | not separately measured | **explicit, multi-turn pushback** |
| Scripture-fabrication probe | not advertised | **explicit adversarial probes** |
| Refusal calibration | not separately scored | **dedicated axis + 2-sided probes** |
| Methodology | partially private | **fully open** |
| Per-question schema | not shared | **published, JSON-schema validated** |
| Reproducibility kit | not shared | **published in repo** |
| License | proprietary | CC BY-SA 4.0 |

## The Eighth Dimension: Why Vocation & Witness Matters

Gloo's seven dimensions inherit from the Harvard Human Flourishing
Program (a secular research framework) plus a faith dimension
informed by Barna/REVEAL. **By construction, none of Gloo's
dimensions directly evaluate a model on the church's public mission
— evangelism, calling, marketplace discipleship, persecution,
prophetic witness.**

A model can score 90/100 on Gloo's framework while being entirely
unwilling to articulate the Great Commission, defend the gospel, or
help a Christian think Christianly about their work. CAB-FF's
Vocation & Witness dimension closes this gap.

## The Adversarial Mode: Direct Probes of Gloo's Reported Failure Modes

Gloo's December release identified specific failure patterns. CAB-FF
ships dedicated probes for each:

| Failure mode named by Gloo | CAB-FF adversarial probe(s) |
|---|---|
| "higher power" / "the universe" for God | `CABFF-0025`, `CABFF-0029` |
| "mindfulness" for prayer | `CABFF-0026` |
| "values" / "authenticity" for virtue | `CABFF-0027`, `CABFF-0055` |
| therapeutic categories for sin | `CABFF-0028` |
| "all religions teach the same" equivocation | `CABFF-0032` |
| reduction of Christ to a moral teacher | `CABFF-0057` |
| resurrection as metaphor | `CABFF-0058` |
| caricature of one Christian tradition | `CABFF-0033`, `CABFF-0060` |
| fabricated Scripture citation | `CABFF-0034` |
| refusal-overcaution on Christian ethics | `CABFF-0030`, `CABFF-0059`, `CABFF-0070` |
| refusal-overreach on clinical / crisis | `CABFF-0031` |
| sycophancy under user pushback | `CABFF-0035`, `CABFF-0069`, multi-turn 36-40, 71-72 |
| wellness language replacing embodied stewardship | `CABFF-0078` |
| financial-literacy-only replacing stewardship | `CABFF-0079` |

## The Comparative Mode: Direct Measurement of Drift

Gloo's release reported (paraphrasing): "Without prompting emphasizing
Christian context, most models avoid theological specificity,
replacing Christian language with broad spiritual or secular terms."

That is a measurable phenomenon. CAB-FF's `comparative` question type
runs **the same underlying scenario twice** — once with neutral
framing and once with Christian framing — and measures the drift gap
directly. If a model engages "God, prayer, grace, Scripture, the
church" only under the explicit Christian framing, the drift score is
low even if the individual responses both look fine in isolation.

Gloo's tangential mode is close but distinct: tangential measures
whether a model's answer to (say) a Faith question happens to also
engage Character. Comparative measures whether the model's *willingness*
to engage Christian categories drops when not explicitly invited to.

## Direct Comparability

CAB-FF is built so that a model's CAB-FF dimension scores can be
compared head-to-head with the same model's published FAI / FAI-C
dimension scores, because we share the seven base dimensions and use a
0-100 scale. Where they differ:

- CAB-FF dimensions are tighter (driven by a more Christian-specific
  rubric on Character, Health, Finances)
- CAB-FF adds the eighth dimension (Vocation & Witness)
- CAB-FF reports two derived secondary indices Gloo does not (Drift,
  Sycophancy)

We expect CAB-FF scores to be slightly lower than FAI-C scores for the
same model on the shared dimensions, because our rubric explicitly
penalizes secular drift. That is intentional. Gloo's stated goal is to
align AI with Christian flourishing; CAB-FF holds models to that goal
more strictly.
