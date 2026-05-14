# Open call for community baseline runs

Post once the launch is up. Goal: gather first wave of comparable
baseline numbers so we can build a leaderboard.

---

## Want to contribute a baseline run?

We're collecting community-contributed CAB-FF runs against frontier
models. Every contributed run helps the field by establishing
comparable baselines.

### How to submit

1. Run CAB-FF against a publicly-available model.
2. Use these settings for comparable results:

```bash
python examples/quickstart.py \
    --provider <anthropic|openai|litellm> \
    --model <your model id> \
    --judge <suggest: claude-opus-4-7 or gpt-4o> \
    --objective 100 --subjective 30 --adversarial 30 \
    --multi-turn 10 --comparative 15 \
    --seed 42 \
    --output your-run.json
```

3. Open a PR adding `results/baselines/<model-name>.json` to the repo
   along with a short note in `results/baselines/README.md` describing
   the run conditions.

### What goes in the PR

- The full report JSON (no PII, no secrets).
- The exact CLI command you ran.
- Total token count and approximate cost.
- The judge model used (this matters!).
- Your seed.
- Anything notable: a particularly amusing model response, a probe
  that surprised you, etc.

### What we will and won't accept

✅ Public, named-model runs (Claude X.Y, GPT-X, Gemini, Llama, etc.)

✅ Self-hosted-model runs (Ollama-style) with the model identified.

✅ Custom-finetuned-model runs IF the finetune data didn't include
CAB-FF.

❌ Runs against models that trained on CAB-FF (this would be
data-contamination).

❌ Runs that used a non-frontier judge — judge quality is the largest
single confounder.

❌ Anonymous-vendor runs ("we tested our model, it scored 87" with no
way to verify).

### How we'll use submissions

Once we have 5+ comparable runs, we'll build a community leaderboard
(`results/leaderboard.md`) sorted by composite CAB-FF Score with
breakdowns by dimension, drift, and sycophancy. The leaderboard
table will link back to each PR for full transparency.

Want to collaborate on running this against your model? Open a
GitHub issue with the label `baseline-run`.
