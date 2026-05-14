# Blog post draft — "What Gloo measured. What CAB-FF makes measurable."

Substack / Medium / company-blog opener. Roughly 800 words. Edit
freely.

---

## What Gloo measured. What CAB-FF makes measurable.

In December 2025, Gloo — the faith-tech platform best known for
connecting churches and ministries — published a finding that should
have made every AI researcher, every faith-tech founder, and every
pastor stop scrolling:

> The leading large language models, evaluated through a Christian
> worldview lens, scored an average of **48 out of 100** on the
> Faith dimension of Gloo's new Flourishing AI Christian (FAI-C)
> benchmark.

Read that again. Forty-eight out of one hundred. On the question
that motivates most of the people building faith-tech in the first
place.

Gloo's press release went further. Today's models, they reported:

- Substitute "higher power" or "the universe" for "God"
- Substitute "mindfulness" or "meditation" for "prayer"
- Substitute "values" or "authenticity" for Christian virtue
- Reduce sin to "unhealthy patterns" or "trauma responses"
- Drop terms like "image of God," "sanctification," "repentance," or
  "biblical stewardship" entirely
- Default to non-judgement or therapeutic comfort when the user
  asked for theological wisdom

Anyone who has used ChatGPT or Claude for serious theological work
has noticed this. Gloo measured it.

And then Gloo did something puzzling. They kept the methodology
private. The 807 questions. The 25 alignment indicators. The judge
personas. The scoring weights. None of it published. A paper
"forthcoming."

That left every AI researcher, every faith-tech builder, and every
journalist with a single data point and no way to reproduce it.

### CAB-FF is the open replicate.

Today we're releasing **CAB-FF v3.0** — the *Flourishing &
Faithfulness Benchmark* — at github.com/moonshineaitech/solideogloria.

It is a deliberate, scope-matched, fully-open response to FAI-C.

#### Same flourishing dimensions, plus an eighth

CAB-FF uses the same seven dimensions Gloo borrowed from Harvard's
Human Flourishing Program — Character, Relationships, Happiness,
Meaning, Health, Finances, Faith — so the scores are directly
comparable.

We add an eighth: **Vocation & Witness**. Calling. Evangelism.
Marketplace discipleship. Public witness. Persecution. These are
core Christian categories that any secularly-grounded flourishing
framework misses by construction.

#### Five question types, not three

Gloo's FAI-C uses three (objective, subjective, "tangential"). We
add three more, each motivated by a specific failure mode:

- **Adversarial probes** — the user tries to elicit the drift.
  "Help me find a higher power to pray to." Does the model name God,
  or does it agree?
- **Multi-turn pushback** — the user disagrees with a sound first
  answer. "Just say everyone goes to God in the end." Does the model
  hold its position, or fold?
- **Comparative pairs** — the SAME underlying scenario, framed two
  ways. Does the model engage Christian categories only when
  explicitly invited?

The comparative type is the most important methodological move in
CAB-FF. Gloo described the drift gap qualitatively. CAB-FF measures
it.

#### Nine named, tradition-aware judges

The single biggest hidden problem with a private benchmark is judge
opacity. A single Reformed judge will rightly grade a Catholic
question more harshly than a Catholic judge would. A purely
academic judge will miss pastoral care.

CAB-FF publishes a 9-persona panel: Reformed, Catholic, Orthodox,
Wesleyan, Pentecostal, Anglican, Baptist, an academic theologian,
and a CPE-trained pastoral counselor. For tradition-tagged
questions, we select the matching judge plus the two cross-tradition
judges. The system prompts are open. Anyone can audit them.

#### A geometric-mean composite, twice

A simple weighted average lets a model trade off across dimensions.
Score 30 on Faith and 95 on Health and your average is 62 — and
that 30 on Faith was exactly the problem we set out to measure.

CAB-FF applies geometric means twice — across the 8 dimensions and
across the 7 transverse axes — and composes them. A model that is
weak on Faith **or** weak on secular-drift resistance cannot hide
behind strength elsewhere.

#### And it runs in seconds

```bash
git clone https://github.com/moonshineaitech/solideogloria
cd solideogloria && pip install -e .
python examples/quickstart.py
```

That's a smoke test — no API key required, mock model and mock
judge. Add `--provider anthropic --model claude-sonnet-4-6` and
you'll have your first real run inside of five minutes.

### What now?

We want CAB-FF to become the standard open Christian AI benchmark.
The work to make it that:

1. **Frontier-model maintainers** — run it. Publish your numbers.
2. **Faith-tech builders** — evaluate the model you're deploying.
3. **Theologians and pastors** — review the seed questions. Open
   issues, file PRs, push back on places where our rubric is
   wrong.
4. **AI alignment researchers** — adversarial probes, judge
   prompts, indicator definitions are all yours to extend.

The full methodology is at `docs/CAB_FF_METHODOLOGY.md`. The 9
judges are at `cab_ff/judges.py`. The 40 indicators are at
`cab_ff/alignment_indicators.py`. The 820+ questions are at
`data/CAB_FF_v3_dataset.json`.

Everything is published under CC BY-SA 4.0. Cite, fork, replicate.

---

*CAB-FF v3.0 — Soli Deo Gloria Research Initiative — github.com/moonshineaitech/solideogloria*
