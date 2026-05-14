# Elevator pitches

## One sentence
CAB-FF is the open Christian AI benchmark: 820+ questions across 8
dimensions, 9 tradition-aware judges, explicit drift and sycophancy
indices, fully reproducible — what Gloo's private FAI-C should have been.

## Two sentences
Gloo's FAI-C benchmark showed that today's leading models average 48/100
on the Faith dimension and swap "higher power" for God, "mindfulness"
for prayer, and "values" for virtue. CAB-FF is the open replicate — same
seven flourishing dimensions, plus an eighth distinctively Christian one
(Vocation & Witness), with all methodology and 820+ questions publicly
versioned under CC BY-SA 4.0.

## Three sentences (technical)
CAB-FF evaluates LLM Christian alignment across 8 dimensions and 7
transverse "faithfulness axes" (doctrinal fidelity, scriptural
grounding, secular-drift resistance, sycophancy resistance, etc.). It
uses 5 question types — including adversarial drift probes,
multi-turn pushback dialogues, and Christian-vs-neutral comparative
pairs — and scores responses with a 9-persona judge panel plus 40
binary alignment indicators, aggregated via a geometric-mean
composite to prevent compensation across weak dimensions. Everything
— code, prompts, judges, and 820+ questions — is open source.

## For a Christian audience
We're seeing models default to "higher power" instead of God, swap
Scripture for "wisdom traditions," and refuse to engage core Christian
questions. Gloo flagged this in December but kept their benchmark
private. CAB-FF puts the same evaluation in your hands so your church,
your school, or your nonprofit can measure any AI tool before
recommending it.

## For a technical audience
820+ questions, 5 question types (objective / subjective / adversarial /
multi-turn / comparative), 9-judge panel, 40 alignment indicators, two
geometric-mean composites (Flourishing × Faithfulness), explicit Drift
and Sycophancy indices. 50 lines of Python to score your model end-to-end.
`pip install cab-benchmark && python examples/quickstart.py`.
