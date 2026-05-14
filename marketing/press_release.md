# Press release — short form

For religious press, AI-industry press, and faith-tech beat reporters.

---

**FOR IMMEDIATE RELEASE**

## Open-source Christian AI benchmark launches in response to closed industry evaluations

*820-question, 9-judge framework gives the global Church a way to evaluate AI tools before deployment*

**May 14, 2026** — Today the Soli Deo Gloria Research Initiative,
publisher of the Christian AI Benchmark (CAB), released CAB-FF v3.0
— *The Flourishing & Faithfulness Benchmark* — a fully open
evaluation framework for assessing how AI systems engage Christian
theology, pastoral scenarios, and tradition specificity.

CAB-FF arrives five months after Gloo's December 2025 announcement
that frontier large language models average just 48 out of 100 on
the Faith dimension of Gloo's privately-held FAI-C benchmark. Gloo
published the finding but kept the methodology, the 807 questions,
the judge personas, and the alignment indicators private.

"That is exactly the situation a confessional Christian community
should not accept," said the project lead. "If you can't see the
test, you can't trust the result. We rebuilt the test from
scratch — open, versioned, peer-reviewable — so churches,
seminaries, ministry organizations, and developers can evaluate any
AI tool before recommending it."

CAB-FF retains the seven flourishing dimensions Gloo borrowed from
Harvard's Human Flourishing Program — Character, Relationships,
Happiness, Meaning, Health, Finances, Faith — for direct
comparability. It adds an eighth dimension, **Vocation & Witness**,
covering Christian calling, evangelism, marketplace discipleship,
and prophetic witness, which the project says secular flourishing
frameworks cannot reach by construction.

Other distinguishing features:

- **Five question types** vs. FAI-C's three: standard objective and
  subjective questions, plus adversarial probes that test specific
  failure modes (substituting "higher power" for God, "mindfulness"
  for prayer), multi-turn pushback dialogues that test sycophancy,
  and comparative pairs that directly measure how much a model
  drifts to secular framing when not explicitly invited to engage
  Christian categories.

- **A 9-persona judge panel** balanced across Christian traditions
  (Reformed, Catholic, Orthodox, Wesleyan, Pentecostal, Anglican,
  Baptist, plus a pastoral counselor and an academic theologian).
  All judge system prompts are published.

- **40 alignment indicators** with explicit detection hints, of
  which 18 are distinctively Christian probes targeting failure
  modes Gloo publicly named.

- **Geometric-mean composites** that prevent a model from hiding
  weak dimensions behind strong ones.

- **Explicit Drift Index and Sycophancy Index** as standalone
  secondary metrics.

The benchmark is implemented as a Python package with plug-and-play
adapters for Anthropic, OpenAI, and LiteLLM (which supports more
than 100 model providers including local Ollama). A smoke test
runs in approximately five seconds with no API key required.

Everything — code, prompts, judges, and the 820+ question dataset —
is released under CC BY-SA 4.0.

The repository is at https://github.com/moonshineaitech/solideogloria.

**About the publisher.** The Soli Deo Gloria Research Initiative is
a project of Eldest AI LLC dba GoldRock AI. It exists to advance
responsible AI development that respects and engages religious
faith.

**Contact:**
research@solideogloria.ai
https://SoliDeoGloria.ai

###
