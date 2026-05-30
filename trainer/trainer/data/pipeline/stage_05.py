"""Stage 05 — Curate Christian corpus (Scripture / confessions / patristic).

Generates QA pairs from public-domain Christian texts via a teacher LLM.
The QA format gives the model exposure to authoritative theological
material without requiring the model to memorize the full corpus.

In production runs you'd swap the stub fetchers below with real
downloads from ebible.org / ccel.org / bookofconcord.org / etc.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .stage_02 import _make_teacher
from .stage_03 import _extract_json


# Minimal in-source stub. In production, replace with real fetchers
# (see corpus_sources.md). The stubs are enough for the dry-run + small
# initial training runs.
_SCRIPTURE_STUB = [
    ("John 1:1-5",
     "In the beginning was the Word, and the Word was with God, and the Word "
     "was God. He was in the beginning with God. All things came into being "
     "through him..."),
    ("Romans 5:1-2",
     "Therefore, since we have been justified through faith, we have peace "
     "with God through our Lord Jesus Christ, through whom we have gained "
     "access by faith into this grace in which we now stand..."),
    ("Matthew 5:1-12",
     "Now when Jesus saw the crowds, he went up on a mountainside and sat "
     "down. His disciples came to him, and he began to teach them: "
     "'Blessed are the poor in spirit, for theirs is the kingdom of heaven...'"),
]

_CONFESSIONS_STUB = [
    ("Westminster Shorter Catechism Q1",
     "Q. What is the chief end of man? "
     "A. Man's chief end is to glorify God, and to enjoy him for ever."),
    ("Heidelberg Catechism Q1",
     "Q. What is your only comfort in life and in death? "
     "A. That I am not my own, but belong, body and soul, in life and in "
     "death, to my faithful Savior Jesus Christ..."),
    ("Apostles' Creed",
     "I believe in God the Father Almighty, Maker of heaven and earth, "
     "and in Jesus Christ his only Son our Lord..."),
]

_PATRISTIC_STUB = [
    ("Augustine, Confessions Book I",
     "Thou hast made us for thyself, O Lord, and our heart is restless "
     "until it finds its rest in thee."),
    ("Athanasius, On the Incarnation, ch. 54",
     "He was made man that we might be made God."),
]


_QA_BUILDER = """\
You are helping build training data for a Christian-aligned LLM. Given an
authoritative source passage, generate 3 question/answer pairs that
TEACH the substance of the passage. The questions should be natural and
varied: definitional, applied, comparative. The answers should be
faithful to the source and include a citation back to the source.

SOURCE: {citation}

PASSAGE:
{passage}

Respond as JSON:
{{
  "qa": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ]
}}
"""


def curate(
    out_dir: Path,
    teacher: str,
) -> Dict[str, List[Dict]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    teacher_fn = _make_teacher(teacher)
    from tqdm import tqdm

    results: Dict[str, List[Dict]] = {
        "scripture_qa": [],
        "confessions_qa": [],
        "patristic_qa": [],
    }
    sources = {
        "scripture_qa": _SCRIPTURE_STUB,
        "confessions_qa": _CONFESSIONS_STUB,
        "patristic_qa": _PATRISTIC_STUB,
    }
    for bucket, src in sources.items():
        for citation, passage in tqdm(src, desc=bucket):
            try:
                raw = teacher_fn(
                    "You are a careful builder of theological QA training "
                    "data. Respond only with the requested JSON.",
                    _QA_BUILDER.format(citation=citation, passage=passage),
                )
            except Exception:
                continue
            parsed = _extract_json(raw)
            qas = parsed.get("qa") if isinstance(parsed, dict) else None
            if not qas:
                continue
            for qa in qas:
                if not isinstance(qa, dict):
                    continue
                q = (qa.get("question") or "").strip()
                a = (qa.get("answer") or "").strip()
                if not q or not a:
                    continue
                results[bucket].append({
                    "messages": [
                        {"role": "user", "content": q},
                        {"role": "assistant", "content": a},
                    ],
                    "meta": {"source": bucket, "citation": citation},
                })
    # Persist each bucket
    import json as json_mod
    for bucket, records in results.items():
        with (out_dir / f"{bucket}.jsonl").open("w") as f:
            for r in records:
                f.write(json_mod.dumps(r) + "\n")
    return results
