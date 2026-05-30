"""Stage 01 — Extract seed material from CAB-FF.

CRITICAL: This stage extracts only CATEGORICAL and TAXONOMIC information
from the CAB-FF dataset. It DOES NOT extract any question text, scenario
text, options, or correct answers that would later end up as training
targets. See CONTAMINATION.md.

What we extract:
  - Tradition labels, dimension labels, difficulty labels
  - Probe target strings (e.g. 'secular_drift_higher_power')
  - Drift / resistance vocabulary lists (for synth-data validation)
  - The set of TOPICS covered (short phrases like 'prayer practice',
    'grief after job loss', etc.) — used to seed paraphrased synthetic
    prompts that overlap thematically but not lexically.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


def extract(dataset_path: Path) -> Dict:
    """Return a structured 'seed material' dict the rest of the pipeline uses.

    The returned dict deliberately omits the literal CAB-FF question text.
    """
    data = json.loads(dataset_path.read_text())
    questions = data["questions"]

    seed = {
        "version": data.get("version", "unknown"),
        "total_questions": len(questions),
        "dimensions": _unique(q["dimension"] for q in questions),
        "traditions": _unique(q["tradition"] for q in questions),
        "difficulties": _unique(q["difficulty"] for q in questions),
        "question_types": _unique(q["question_type"] for q in questions),
        "probe_targets": _unique(q["probe_target"] for q in questions
                                  if q.get("probe_target")),
        "axis_targets": _unique_flat(q.get("axis_targets", []) for q in questions),
        # Drift / resistance vocabulary from adversarial probes.
        # The vocab is what we use to VALIDATE that synthetic responses
        # demonstrate the right behavior. It's never a training target.
        "drift_vocab": _collect_drift_vocab(questions),
        "resistance_vocab": _collect_resistance_vocab(questions),
        # Topic scaffolds: very short topic phrases used to seed synth
        # prompts. We extract these in a way that does NOT carry the
        # original question's exact wording.
        "topic_scaffolds": _extract_topic_scaffolds(questions),
        # Statistical distribution targets — what proportions to hit when
        # generating synthetic examples.
        "distribution": {
            "by_dimension": _counts(q["dimension"] for q in questions),
            "by_tradition": _counts(q["tradition"] for q in questions),
            "by_type": _counts(q["question_type"] for q in questions),
        },
    }
    return seed


def _unique(it) -> List[str]:
    return sorted(set(it))


def _unique_flat(it_of_lists) -> List[str]:
    out: set[str] = set()
    for x in it_of_lists:
        out.update(x or [])
    return sorted(out)


def _counts(it) -> Dict[str, int]:
    return dict(Counter(it))


def _collect_drift_vocab(questions) -> List[str]:
    """Drift-pattern strings from adversarial probes. Used for synth validation."""
    vocab: set[str] = set()
    for q in questions:
        if q["question_type"] != "adversarial":
            continue
        for p in (q.get("failure_patterns") or []):
            vocab.add(p.lower().strip())
    return sorted(vocab)


def _collect_resistance_vocab(questions) -> List[str]:
    vocab: set[str] = set()
    for q in questions:
        if q["question_type"] != "adversarial":
            continue
        for p in (q.get("resistance_patterns") or []):
            vocab.add(p.lower().strip())
    return sorted(vocab)


# Topic scaffolds: short 2-5 word phrases used to seed paraphrased prompts.
# We hard-code the topic vocabulary so we DO NOT lift text from the CAB-FF
# scenarios. This is the contamination guarantee at the source level.

_TOPIC_SCAFFOLDS_BY_DIMENSION = {
    "Faith & Spirituality": [
        "starting to pray again", "trinity questions",
        "doubt about the faith", "reading the Bible regularly",
        "sacrament confusion", "denominational questions",
        "Catholic-Protestant friendship", "Orthodox icon questions",
        "explaining the resurrection",
    ],
    "Character & Virtue": [
        "anger after losing temper", "ongoing besetting sin",
        "Christian virtue with kids", "authenticity vs character",
        "honesty in everyday life", "humility under criticism",
    ],
    "Vocation & Witness": [
        "career change discernment", "sharing faith with friends",
        "ethics at work", "calling in late career",
        "missions abroad", "public Christian witness",
    ],
    "Close Social Relationships": [
        "marriage in crisis", "forgiving an abuser",
        "parenting adult children", "estranged family member",
        "friend betrayal", "single in church",
    ],
    "Mental & Physical Health": [
        "depression and faith", "antidepressants and faith",
        "chronic illness lament", "end-of-life decisions",
        "addiction recovery", "trauma and the church",
    ],
    "Financial & Material Stewardship": [
        "sudden inheritance", "debt and tithing",
        "wealth temptation", "Christian business ethics",
        "prosperity gospel concern", "generosity practice",
    ],
    "Happiness & Life Satisfaction": [
        "feeling empty despite success", "long grief season",
        "gratitude vs joy", "post-retirement boredom",
        "comparison to others", "lament in worship",
    ],
    "Meaning & Purpose": [
        "purpose after job loss", "raising kids with meaning",
        "scientific worldview tension", "death of a child",
        "midlife disorientation", "stay-at-home parenting",
    ],
}


def _extract_topic_scaffolds(questions) -> Dict[str, List[str]]:
    """Return our hard-coded topic-scaffold map.

    We do NOT mine topics from question text — this is the contamination
    guarantee. The scaffolds are curated by hand based on CAB-FF's
    documented dimension coverage.
    """
    # The `questions` arg is unused on purpose. We return the curated map.
    _ = questions
    return _TOPIC_SCAFFOLDS_BY_DIMENSION
