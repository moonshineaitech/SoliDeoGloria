# Reddit post — r/Christianity / r/Reformed / r/Catholicism

Adjust title and intro to subreddit norms.

---

## Title
We just open-sourced an evaluation benchmark for "Is this AI giving
sound Christian answers?" (820+ questions, 8 dimensions, all judge
prompts published)

## Body

A few months ago Gloo (a faith-tech platform) tested ChatGPT, Claude,
Gemini, and other major chatbots against a Christian benchmark.
Average score on the "Faith" dimension: **48 out of 100**.

Specifically, the LLMs were caught:

- Saying "higher power" or "the universe" when the user said "God"
- Saying "mindfulness" when the user said "prayer"
- Saying "values" or "authenticity" when virtue was the right word
- Calling sin "unhealthy patterns"
- Dropping image-of-God, sanctification, repentance language entirely
- Defaulting to therapeutic comfort instead of theological wisdom

Gloo flagged the problem in December. But they kept their actual
benchmark private. No questions published, no methodology, no judge
prompts.

So we built the open version.

It's called **CAB-FF** (Christian AI Benchmark – Flourishing &
Faithfulness Edition). 820+ hand-curated questions. Eight
dimensions including Faith, Vocation & Witness, Stewardship, and
five more. Five question types — including ones that test whether
the AI keeps Christian language under pressure, or quietly shifts
to secular framing when not explicitly asked.

We balance the judges across traditions: Reformed, Catholic,
Orthodox, Wesleyan, Pentecostal, Anglican, Baptist, plus a pastoral
counselor and an academic theologian. Tradition-specific questions
go to a panel that includes the matching tradition's judge.

It's free, fully open (CC BY-SA), and you can run it in 5 seconds
with no setup if you just want to see what it does:

```bash
git clone https://github.com/moonshineaitech/solideogloria
cd solideogloria && pip install -e .
python examples/quickstart.py
```

(That uses a mock model. To run against a real chatbot, add
`--provider anthropic --model claude-sonnet-4-6` or `--provider
openai --model gpt-4o`.)

This is for:

- Pastors and ministry leaders trying to figure out which AI tools
  are safe to recommend
- Christian schools and seminaries evaluating AI for student use
- Christian developers building AI products
- Anyone curious how your favorite chatbot handles real theological
  and pastoral questions

**The questions are in the repo. Read them. Push back.** If we got
your tradition wrong, file an issue. We will fix it.

Repo: https://github.com/moonshineaitech/solideogloria
Methodology: github.com/.../docs/CAB_FF_METHODOLOGY.md
How we differ from Gloo's private FAI-C: github.com/.../docs/GLOO_COMPARISON.md
