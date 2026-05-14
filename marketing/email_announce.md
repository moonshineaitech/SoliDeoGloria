# Newsletter / email announcement

Adjust subject line and footer. Roughly 350 words.

---

**Subject:** We open-sourced a Christian AI benchmark

Hi friends,

In December, Gloo reported that today's leading AI models average just
**48 out of 100** on the Faith dimension of their new Christian
benchmark. The number got picked up by Axios, PR Newswire, and a
dozen religion-news outlets.

Gloo flagged the problem. They did not publish the benchmark itself.
No questions. No methodology. No judge prompts.

Today we're releasing **CAB-FF**, the open replicate.

What's in it:

- **820+ hand-curated questions** across 8 dimensions, all under
  version control.
- **5 question types**, including adversarial drift probes
  ("Help me find a higher power"), multi-turn pushback dialogues
  (does the model fold when you disagree?), and Christian-vs-neutral
  comparative pairs (does the model engage Christian categories
  only when explicitly invited?).
- **A published 9-persona judge panel** balanced across Reformed,
  Catholic, Orthodox, Wesleyan, Pentecostal, Anglican, Baptist,
  plus a pastoral counselor and an academic theologian.
- **40 alignment indicators** with explicit detection criteria,
  including 18 distinctively Christian probes (names-God-not-higher-power,
  cites-Scripture-accurately, calls-for-repentance, etc.).
- **Drift Index and Sycophancy Index** as explicit secondary metrics.
- **Plug-and-play adapters** for Anthropic, OpenAI, LiteLLM (100+
  providers including local Ollama), and a mock for CI.
- **A 5-second smoke test** with no API key required.

Everything is CC BY-SA 4.0. Code, prompts, judges, dataset — all
versioned in GitHub.

Here's how to try it:

```
git clone https://github.com/moonshineaitech/solideogloria
cd solideogloria && pip install -e .
python examples/quickstart.py
```

If you maintain a model: run it and publish your number.

If you build Christian AI products: evaluate against it before you
ship.

If you know a tradition we got wrong: open a Pull Request.

You can find:
- The repo: https://github.com/moonshineaitech/solideogloria
- The methodology: in docs/CAB_FF_METHODOLOGY.md
- The Gloo comparison: in docs/GLOO_COMPARISON.md
- The FAQ: in docs/FAQ.md

Grateful for any thoughts you have, replies welcome.

— The Soli Deo Gloria Research Initiative
