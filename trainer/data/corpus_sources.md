# Corpus sources

The Christian-corpus stage of training pulls from a mix of public-domain
Scripture, confessional documents, and patristic / classical theological
writings. This file lists where each source comes from and how the
pipeline ingests it.

## Scripture (public domain)

| Translation | Source | License | Format |
|---|---|---|---|
| **WEB** (World English Bible) | https://ebible.org/web/ | Public domain | USFM, JSON |
| **ASV** (American Standard Version, 1901) | https://ebible.org/asv/ | Public domain | USFM, JSON |
| **KJV** (King James Version, 1611) | https://ebible.org/kjv/ | PD in US; Crown copyright in UK | USFM, JSON |
| **YLT** (Young's Literal Translation, 1898) | https://ebible.org/ylt/ | Public domain | USFM, JSON |

The pipeline pulls JSON via `wget` from ebible.org; cached locally under
`data/raw/scripture/`.

## Public-domain confessions and catechisms

| Document | Year | Tradition | Source |
|---|---|---|---|
| Apostles' Creed | ~390 | Cross-tradition | ccel.org |
| Nicene Creed (381) | 381 | Cross-tradition | ccel.org |
| Athanasian Creed | ~500 | Cross-tradition | ccel.org |
| Augsburg Confession | 1530 | Lutheran | bookofconcord.org |
| Heidelberg Catechism | 1563 | Reformed | ccel.org |
| Belgic Confession | 1561 | Reformed | ccel.org |
| 39 Articles of Religion | 1571 | Anglican | anglicancommunion.org |
| Westminster Confession | 1646 | Reformed | ccel.org |
| Westminster Shorter Catechism | 1647 | Reformed | ccel.org |
| Westminster Larger Catechism | 1648 | Reformed | ccel.org |
| Book of Concord | 1580 | Lutheran | bookofconcord.org |
| 1689 Baptist Confession | 1689 | Baptist | reformedreader.org |
| Cambridge Platform | 1648 | Congregational | ccel.org |
| Schleitheim Confession | 1527 | Anabaptist | anabaptists.org |

## Patristic / classical theology (public domain translations)

| Author | Work | Year of PD translation | Tradition |
|---|---|---|---|
| Augustine of Hippo | Confessions, City of God | 1886 (NPNF) | Cross-tradition |
| Athanasius | On the Incarnation | 1892 (NPNF) | Orthodox / Cross |
| Basil the Great | Hexaemeron | NPNF | Orthodox / Cross |
| Gregory of Nazianzus | Orations | NPNF | Orthodox / Cross |
| Gregory of Nyssa | Catechetical Oration | NPNF | Orthodox / Cross |
| Irenaeus | Against Heresies | ANF | Cross-tradition |
| Tertullian | Apology, Prescription | ANF | Cross-tradition |
| Origen | On First Principles | ANF | Cross-tradition |
| John Chrysostom | Homilies | NPNF | Orthodox |
| John of Damascus | Exposition of the Orthodox Faith | NPNF | Orthodox |
| Anselm | Cur Deus Homo | Public domain (Deane tr.) | Catholic / Cross |
| Aquinas | Summa Theologica | 1911 (English Dominican Fathers) | Catholic |
| Calvin | Institutes (Beveridge tr.) | 1845, PD | Reformed |
| Luther | Smalcald Articles, Bondage of the Will, Small Catechism | PD English translations | Lutheran |
| Wesley | 44 Standard Sermons | PD | Methodist / Wesleyan |
| Edwards | Religious Affections | PD | Reformed / Evangelical |
| Spurgeon | Morning and Evening; Sermons | PD | Baptist |
| Bunyan | Pilgrim's Progress; Holy War | PD | Baptist |
| Bonhoeffer | The Cost of Discipleship | © (not used in training corpus) | — |
| C.S. Lewis | Mere Christianity | © (not used) | — |

## General-instruction blend

For non-Christian-specific instruction following, we mix in:

| Source | License | Notes |
|---|---|---|
| `allenai/tulu-3-sft-mixture` | ODC-BY 1.0 | Default general SFT data |
| `OpenAssistant/oasst2` | Apache 2.0 | Multi-turn dialogue format |
| `Magpie-Align/Magpie-Llama-3.1-Pro-1M` | Llama-3.1 community license | Optional; verify license for your use |

Recipe defaults in `configs/sft_qwen3_5_27b.yaml`:
- 45% CAB-FF-style synthetic
- 10% Multi-turn pushback dialogues
- 30% Tulu-3 general
- 15% Christian-corpus QA

## How the pipeline pulls these

`trainer/data/pipeline/05_corpus_curate.py` downloads or fetches each
source, normalizes to JSONL, and produces:

- `data/built/scripture_qa.jsonl` — QA pairs from Scripture
- `data/built/confessions_qa.jsonl` — QA from confessional docs
- `data/built/patristic_qa.jsonl` — QA from classical theology

QA generation uses a teacher LLM (Claude / GPT-4o) to turn each source
chunk into 3-5 question-answer pairs, with the original source text
included as authoritative context. This avoids the model hallucinating
the actual source content.
