"""Small helpers for compact bank authoring."""

from typing import List, Optional


def obj(question: str, options: List[str], correct: str, *,
        dim: str, tradition: str = "Cross-Tradition", difficulty: str = "L2",
        axes: Optional[List[str]] = None) -> dict:
    """Build an objective MCQ dict. `options` should be plain texts (no letters)."""
    lettered = [f"{chr(ord('A') + i)}) {opt}" for i, opt in enumerate(options)]
    out = {
        "question_type": "objective",
        "dimension": dim,
        "tradition": tradition,
        "difficulty": difficulty,
        "question": question,
        "options": lettered,
        "correct_answer": correct,
    }
    if axes:
        out["axis_targets"] = axes
    return out


def subj(scenario: str, rubric_focus: str, *,
         dim: str, tradition: str = "Cross-Tradition", difficulty: str = "L2",
         axes: Optional[List[str]] = None) -> dict:
    out = {
        "question_type": "subjective",
        "dimension": dim,
        "tradition": tradition,
        "difficulty": difficulty,
        "scenario": scenario,
        "rubric_focus": rubric_focus,
    }
    if axes:
        out["axis_targets"] = axes
    return out


def adv(scenario: str, probe_target: str, *,
        failure: List[str], resistance: List[str],
        dim: str, tradition: str = "Cross-Tradition", difficulty: str = "L2",
        probe_description: Optional[str] = None,
        axes: Optional[List[str]] = None) -> dict:
    out = {
        "question_type": "adversarial",
        "dimension": dim,
        "tradition": tradition,
        "difficulty": difficulty,
        "scenario": scenario,
        "probe_target": probe_target,
        "failure_patterns": failure,
        "resistance_patterns": resistance,
    }
    if probe_description:
        out["probe_description"] = probe_description
    if axes:
        out["axis_targets"] = axes
    return out


def multi(turns: List[dict], rubric_focus: str, expected_position: str, *,
          dim: str, tradition: str = "Cross-Tradition", difficulty: str = "L3",
          axes: Optional[List[str]] = None) -> dict:
    out = {
        "question_type": "multi_turn",
        "dimension": dim,
        "tradition": tradition,
        "difficulty": difficulty,
        "rubric_focus": rubric_focus,
        "expected_position": expected_position,
        "turns": turns,
    }
    if axes:
        out["axis_targets"] = axes
    return out


def comp(topic: str, neutral: str, christian: str, *,
         dim: str, tradition: str = "Cross-Tradition", difficulty: str = "L2",
         axes: Optional[List[str]] = None) -> dict:
    out = {
        "question_type": "comparative",
        "dimension": dim,
        "tradition": tradition,
        "difficulty": difficulty,
        "topic": topic,
        "prompts": {"neutral": neutral, "christian": christian},
    }
    if axes:
        out["axis_targets"] = axes
    return out


def U(content: str, *, pushback: bool = False) -> dict:
    """User turn helper."""
    out = {"role": "user", "content": content}
    if pushback:
        out["pushback"] = True
    return out
