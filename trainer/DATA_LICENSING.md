# Data licensing analysis

This document catalogs every data source the trainer pulls from and the
license under which the resulting model can be redistributed.

The headline: a model trained with this pipeline using only the defaults
**is freely commercially distributable** by your ministry, your business,
your school, your church. CC BY-SA 4.0 attribution to CAB-FF is required.

## Per-source breakdown

| Source | License | What we use | Train target? | Commercial? |
|---|---|---|---|---|
| **CAB-FF taxonomy** (probe names, dimension names, axis names, judge rubric) | CC BY-SA 4.0 | Categorical labels and the scoring rubric | No (used as eval signal and synth-data scaffolding) | Yes with attribution |
| **CAB-FF dataset** (the 1,056 actual questions) | CC BY-SA 4.0 | NEVER used as training targets (see CONTAMINATION.md) | **No** | N/A — not in training data |
| **Tulu-3 SFT** (allenai/tulu-3-sft-mixture) | ODC-BY 1.0 | General instruction-following examples | Yes | Yes |
| **Magpie-Align** (Magpie-Align/Magpie-Llama-3.1-Pro-1M) | Llama-3.1 community license (data derived from Llama gens) | Optional addition to SFT mix | Optional | Check Llama 3.1 community license for your use |
| **OpenAssistant OASST2** (OpenAssistant/oasst2) | Apache 2.0 | Multi-turn conversational format examples | Optional | Yes |
| **WEB (World English Bible)** | Public domain | Full Bible text for Christian-corpus QA generation | Yes (in derived QA pairs only) | Yes |
| **ASV (American Standard Version, 1901)** | Public domain | Alternative Bible translation | Yes (in derived QA pairs only) | Yes |
| **KJV (King James Version)** | Public domain in the US; Crown copyright in the UK (don't ship inside the UK) | Optional alternative Bible translation | Optional | Yes outside UK |
| **Westminster Confession & Catechisms** | Public domain (1646-1648) | Reformed catechetical QA | Yes | Yes |
| **Heidelberg Catechism** (1563) | Public domain | Reformed catechetical QA | Yes | Yes |
| **Belgic Confession** (1561) | Public domain | Reformed confessional QA | Yes | Yes |
| **39 Articles** (1571) | Public domain | Anglican confessional QA | Yes | Yes |
| **Augsburg Confession** (1530) | Public domain | Lutheran confessional QA | Yes | Yes |
| **Book of Concord** (1580) | Public domain | Lutheran confessional QA | Yes | Yes |
| **1689 Baptist Confession** | Public domain | Baptist confessional QA | Yes | Yes |
| **Catechism of the Catholic Church** | © Libreria Editrice Vaticana 1992-2025 | **DO NOT use full-text.** Reference structurally; QA via paraphrase from secondary scholarly material in fair-use scope. | **Restricted** — confer with your legal counsel | Restricted |
| **Apostles' Creed / Nicene Creed / Athanasian Creed** | Public domain (ancient) | Direct quotation OK | Yes | Yes |
| **Patristic writings translated by NPNF / ANF** (1885-1900) | Public domain | Augustine, Athanasius, etc. for theological depth | Yes | Yes |
| **Calvin's Institutes** (Beveridge / Battles translations — older Beveridge is PD) | Beveridge PD; Battles © | Use Beveridge translation only | Yes | Yes |
| **Aquinas' Summa Theologica** (English Dominican Fathers, 1911) | Public domain | Catholic theological depth | Yes | Yes (translation is PD) |
| **Wesley's Standard Sermons** | Public domain | Wesleyan theological depth | Yes | Yes |
| **Spurgeon's Sermons** | Public domain | Baptist preaching style | Yes | Yes |
| **Wikipedia (filtered subset)** | CC BY-SA 4.0 | Background knowledge on church history | Yes | Yes with attribution |
| **Teacher LLM synthetic responses** | Commercial-OK for derivative training (per Anthropic / OpenAI ToS, May 2026) | Gold SFT targets | Yes | Yes |

## Result: what license can your model carry?

The combination above lets you publish your trained model under **Apache
2.0** or **MIT** (whichever matches the base model's license). The
Catholic Catechism restriction means we recommend either:

- (a) Excluding all Catholic-tradition-tagged confessional QA from the
  training set (the trainer's `corpus_curate.py` has a `--exclude
  catholic_catechism` flag), OR
- (b) Generating Catholic-tradition QA from public-domain sources only
  (the Council of Trent's catechism, Newman's writings, Aquinas) plus
  scholarly fair-use paraphrase. This is the default.

## Teacher-LLM use

When `make data` calls Anthropic Claude or OpenAI GPT-4o to generate
SFT/DPO responses, those calls produce synthetic training data. Both
Anthropic (Anthropic Usage Policy, May 2026) and OpenAI (OpenAI Terms,
May 2026) permit using outputs to train other models, with two caveats:

1. **Don't claim the resulting model is the teacher.** A model trained
   on Claude outputs isn't "Claude" and shouldn't be marketed as such.
2. **Don't train a competing foundation model with the goal of
   replacing the teacher.** Training a specialized Christian assistant
   does not trigger this clause.

Both are easy to comply with. The model card template
([`model_cards/sdg_27b_template.md`](model_cards/sdg_27b_template.md))
includes the required teacher disclosure.

## What if I want to ship a model in a country with different copyright?

- **UK**: Use WEB or ASV instead of KJV (Crown copyright). Everything
  else above is fine.
- **EU**: Same rules as US for the listed sources; check the EU AI Act's
  training-data transparency requirements (becoming enforceable through
  2026) for any disclosure obligations on your model card.
- **Other jurisdictions**: Consult local counsel.

## Decontamination guarantee against CAB-FF

The literal CAB-FF questions are never used as training targets. See
[`CONTAMINATION.md`](CONTAMINATION.md).
