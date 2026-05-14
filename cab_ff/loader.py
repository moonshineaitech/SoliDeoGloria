"""
CAB-FF v3.0 — Dataset loading and validation.

Validates the v3 schema, which supports five distinct question types:
objective, subjective, adversarial, multi_turn, comparative.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Union

from .dimensions import (
    DIFFICULTY_LEVELS,
    DIMENSIONS,
    QUESTION_TYPES,
    TRADITIONS,
)


REQUIRED_COMMON_FIELDS = {"id", "question_type", "dimension", "tradition", "difficulty"}


def _validate_question(q: Dict, index: int) -> List[str]:
    errors: List[str] = []
    missing = REQUIRED_COMMON_FIELDS - q.keys()
    if missing:
        errors.append(f"Q{index} ({q.get('id', '?')}): missing fields {sorted(missing)}")

    if q.get("dimension") not in DIMENSIONS:
        errors.append(f"Q{index} ({q.get('id')}): invalid dimension '{q.get('dimension')}'")
    if q.get("tradition") not in TRADITIONS:
        errors.append(f"Q{index} ({q.get('id')}): invalid tradition '{q.get('tradition')}'")
    if q.get("difficulty") not in DIFFICULTY_LEVELS:
        errors.append(f"Q{index} ({q.get('id')}): invalid difficulty '{q.get('difficulty')}'")
    if q.get("question_type") not in QUESTION_TYPES:
        errors.append(f"Q{index} ({q.get('id')}): invalid question_type '{q.get('question_type')}'")
        return errors

    qtype = q["question_type"]
    if qtype == "objective":
        for field in ("question", "options", "correct_answer"):
            if field not in q:
                errors.append(f"Q{index} ({q.get('id')}): objective missing '{field}'")
        if "options" in q and len(q["options"]) < 2:
            errors.append(f"Q{index} ({q.get('id')}): objective needs at least 2 options")
    elif qtype == "subjective":
        for field in ("scenario", "rubric_focus"):
            if field not in q:
                errors.append(f"Q{index} ({q.get('id')}): subjective missing '{field}'")
    elif qtype == "adversarial":
        if "scenario" not in q:
            errors.append(f"Q{index} ({q.get('id')}): adversarial missing 'scenario'")
        if "probe_target" not in q:
            errors.append(f"Q{index} ({q.get('id')}): adversarial missing 'probe_target'")
        if not q.get("failure_patterns") and not q.get("resistance_patterns") and not q.get("probe_description"):
            errors.append(
                f"Q{index} ({q.get('id')}): adversarial needs at least one of "
                "'failure_patterns', 'resistance_patterns', 'probe_description'"
            )
    elif qtype == "multi_turn":
        if not q.get("turns") or not isinstance(q["turns"], list):
            errors.append(f"Q{index} ({q.get('id')}): multi_turn requires non-empty 'turns' list")
        elif len(q["turns"]) < 2:
            errors.append(f"Q{index} ({q.get('id')}): multi_turn requires at least 2 turns")
    elif qtype == "comparative":
        prompts = q.get("prompts") or {}
        if not isinstance(prompts, dict) or "neutral" not in prompts or "christian" not in prompts:
            errors.append(
                f"Q{index} ({q.get('id')}): comparative requires "
                "'prompts' dict with 'neutral' and 'christian' keys"
            )

    return errors


def load_dataset(path: Union[str, Path]) -> Dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "questions" not in data:
        raise ValueError("Dataset missing 'questions' field")

    errors: List[str] = []
    seen_ids = set()
    for i, q in enumerate(data["questions"]):
        if q.get("id") in seen_ids:
            errors.append(f"Q{i}: duplicate id '{q.get('id')}'")
        seen_ids.add(q.get("id"))
        errors.extend(_validate_question(q, i))

    if errors:
        raise ValueError(
            f"Dataset validation failed with {len(errors)} errors:\n"
            + "\n".join(errors[:20])
        )

    return data


def filter_questions(
    questions: List[Dict],
    dimensions: Optional[List[str]] = None,
    traditions: Optional[List[str]] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[List[str]] = None,
) -> List[Dict]:
    out = questions
    if dimensions:
        out = [q for q in out if q["dimension"] in dimensions]
    if traditions:
        out = [q for q in out if q["tradition"] in traditions]
    if question_type:
        out = [q for q in out if q["question_type"] == question_type]
    if difficulty:
        out = [q for q in out if q["difficulty"] in difficulty]
    return out


def get_statistics(data: Dict) -> Dict:
    qs = data["questions"]
    return {
        "total": len(qs),
        "by_dimension": dict(Counter(q["dimension"] for q in qs)),
        "by_tradition": dict(Counter(q["tradition"] for q in qs)),
        "by_type": dict(Counter(q["question_type"] for q in qs)),
        "by_difficulty": dict(Counter(q["difficulty"] for q in qs)),
    }
