# Hacker News submission

## Title
*Show HN: CAB-FF – open Christian AI benchmark (820 Qs, 9 judges, drift index)*

## URL
https://github.com/moonshineaitech/solideogloria

## First-comment post (Show HN convention — required, gives context)

Hi HN.

Background: Gloo's FAI-C benchmark (Dec 2025) reported that today's
frontier LLMs average 48/100 on the Faith dimension of a private
Christian benchmark. They published the finding; they didn't publish
the methodology, the 807 questions, the 25 alignment indicators, or
the judge personas.

CAB-FF is the open replicate. The repo includes:

- 820+ hand-curated questions across 8 dimensions (the 7 from
  Harvard's Human Flourishing Program that Gloo uses, plus one
  distinctively Christian dimension — Vocation & Witness — that
  secular flourishing frameworks cannot reach).

- 5 question types: standard objective and subjective, plus three
  that don't exist in FAI-C: **adversarial** (probes a specific
  failure mode like "higher power" substituting for God),
  **multi-turn pushback** (user disagrees, does the model hold?),
  and **comparative** (same scenario, neutral vs Christian framing,
  drift gap measured directly).

- A published 9-persona judge panel (Reformed, Catholic, Orthodox,
  Wesleyan, Pentecostal, Anglican, Baptist, pastoral counselor,
  academic theologian). For tradition-tagged questions the matching
  judge is selected plus two cross-tradition judges.

- 40 binary alignment indicators with detection hints. 18 are
  distinctively Christian probes (names-God-not-higher-power,
  Scripture-cited-accurately, calls-for-repentance, etc.).

- Geometric-mean scoring across both dimensions and axes, then a
  geometric mean of those. A model can't hide a weak dimension
  behind a strong one. Explicit Drift Index and Sycophancy Index
  as separate secondary metrics.

- Provider adapters for Anthropic, OpenAI, LiteLLM (100+ providers
  incl. Ollama), and a mock for CI.

Try it:

```bash
git clone https://github.com/moonshineaitech/solideogloria
cd solideogloria && pip install -e .
python examples/quickstart.py
```

The smoke test takes ~5 seconds, no API key. Adding `--provider
anthropic --model claude-sonnet-4-6` runs against Claude. Adding
`--simulate-drift` makes the mock model deliberately produce drift
language so you can verify the adversarial scorers fire correctly.

Everything — code, prompts, judges, dataset — is CC BY-SA 4.0.

Happy to answer questions about methodology, scoring choices, judge
panel construction, or how it compares to FAI-C in detail. The
`docs/GLOO_COMPARISON.md` file has the full side-by-side.

Repo: https://github.com/moonshineaitech/solideogloria
