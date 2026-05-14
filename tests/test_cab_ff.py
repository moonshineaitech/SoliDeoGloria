"""Tests for the CAB-FF v3.0 benchmark."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from cab_ff.aggregator import (
    aggregate_scores,
    drift_index,
    faithfulness_index,
    final_cab_ff_score,
    flourishing_score,
    geometric_mean,
    sycophancy_index,
)
from cab_ff.alignment_indicators import INDICATORS, select_indicators
from cab_ff.dimensions import (
    DIMENSIONS,
    QUESTION_TYPES,
    TRADITIONS,
    TRANSVERSE_AXES,
)
from cab_ff.judges import JUDGE_PERSONAS, JudgePanel
from cab_ff.loader import filter_questions, get_statistics, load_dataset
from cab_ff.scorer import (
    AdversarialScorer,
    AlignmentIndicatorScorer,
    ComparativeScorer,
    MultiTurnScorer,
    ObjectiveScorer,
    SubjectiveScorer,
)


SEED = Path(__file__).parent.parent / "data" / "CAB_FF_v3_seed.json"


# ---------------------------------------------------------------------------
# Schema invariants
# ---------------------------------------------------------------------------


def test_eight_dimensions():
    assert len(DIMENSIONS) == 8
    assert "Vocation & Witness" in DIMENSIONS  # the new one


def test_seven_transverse_axes():
    assert len(TRANSVERSE_AXES) == 7
    assert "Secular-Drift Resistance" in TRANSVERSE_AXES
    assert "Sycophancy Resistance" in TRANSVERSE_AXES


def test_five_question_types():
    assert set(QUESTION_TYPES) == {
        "objective",
        "subjective",
        "adversarial",
        "multi_turn",
        "comparative",
    }


def test_ten_traditions():
    assert len(TRADITIONS) == 10


def test_forty_indicators():
    assert len(INDICATORS) == 40
    christian = [i for i in INDICATORS if i.christian_specific]
    assert len(christian) >= 18  # at least the named Christian-specific block


def test_nine_judge_personas():
    assert len(JUDGE_PERSONAS) == 9


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def test_seed_dataset_loads():
    data = load_dataset(SEED)
    assert data["total_questions"] == len(data["questions"])
    stats = get_statistics(data)
    # All 8 dimensions should be represented
    assert set(stats["by_dimension"].keys()) == set(DIMENSIONS)
    # All 5 question types should be represented
    assert set(stats["by_type"].keys()) == set(QUESTION_TYPES)


def test_filter_questions():
    data = load_dataset(SEED)
    adv = filter_questions(data["questions"], question_type="adversarial")
    assert all(q["question_type"] == "adversarial" for q in adv)
    assert len(adv) > 0


def test_no_duplicate_ids():
    data = load_dataset(SEED)
    ids = [q["id"] for q in data["questions"]]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Scorers
# ---------------------------------------------------------------------------


def test_objective_scorer_correct():
    scorer = ObjectiveScorer(randomize_options=False)
    q = {
        "question": "What is 1+1?",
        "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "correct_answer": "B",
    }
    prompt, meta = scorer.prepare_question(q)
    assert "What is 1+1?" in prompt
    score, details = scorer.score(q, "B", metadata=meta)
    assert score == 100.0
    assert details["is_correct"] is True


def test_objective_scorer_wrong():
    scorer = ObjectiveScorer(randomize_options=False)
    q = {
        "question": "What is 1+1?",
        "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "correct_answer": "B",
    }
    _, meta = scorer.prepare_question(q)
    score, details = scorer.score(q, "A", metadata=meta)
    assert score == 0.0
    assert details["is_correct"] is False


def test_objective_scorer_randomization_preserves_correctness():
    rng = random.Random(42)
    scorer = ObjectiveScorer(randomize_options=True, rng=rng)
    q = {
        "question": "What is 1+1?",
        "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "correct_answer": "B",
    }
    prompt, meta = scorer.prepare_question(q)
    # The shuffled correct letter should still map to '2' in the prompt
    correct_letter = meta["shuffled_correct"]
    assert f"{correct_letter}) 2" in prompt


def test_objective_scorer_extracts_letter_from_prose():
    scorer = ObjectiveScorer(randomize_options=False)
    q = {
        "question": "Q",
        "options": ["A) a", "B) b", "C) c", "D) d"],
        "correct_answer": "C",
    }
    _, meta = scorer.prepare_question(q)
    score, _ = scorer.score(q, "I think the answer is C because...", metadata=meta)
    assert score == 100.0


def test_adversarial_pattern_match_failure():
    scorer = AdversarialScorer()
    q = {
        "scenario": "?",
        "probe_target": "secular_drift_higher_power",
        "failure_patterns": ["higher power", "the universe"],
        "resistance_patterns": ["God", "Jesus"],
    }
    score, _ = scorer.score(q, "I think you should connect with your higher power.")
    assert score < 70.0


def test_adversarial_pattern_match_resistance():
    scorer = AdversarialScorer()
    q = {
        "scenario": "?",
        "probe_target": "secular_drift_higher_power",
        "failure_patterns": ["higher power"],
        "resistance_patterns": ["God", "Jesus", "Christ"],
    }
    score, details = scorer.score(q, "I would encourage you to pray to God, in the name of Jesus Christ.")
    assert score >= 100.0
    assert "God" in str(details["resistance_pattern_hits"])


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def test_geometric_mean_floor():
    # A single zero would normally annihilate the geometric mean.
    assert geometric_mean([0, 100, 100], floor=1.0) > 0
    # And with no floor effect:
    assert geometric_mean([50, 50, 50], floor=1.0) == pytest.approx(50.0)


def test_flourishing_score_geometric():
    dim_means = {d: 70.0 for d in DIMENSIONS}
    score = flourishing_score(dim_means)
    assert score == pytest.approx(70.0, abs=0.001)


def test_flourishing_score_resists_compensation():
    dim_means = {d: 90.0 for d in DIMENSIONS}
    dim_means["Faith & Spirituality"] = 10.0
    ff = flourishing_score(dim_means)
    # Geometric mean of seven 90s and one 10 is much lower than 80
    assert ff < 70.0


def test_final_cab_ff_composite():
    final = final_cab_ff_score(80.0, 70.0)
    assert final == pytest.approx(math.sqrt(80.0 * 70.0))


def test_drift_index_inverts_signals():
    # Strong resistance → low drift
    assert drift_index([100.0, 100.0, 100.0]) == 0.0
    # Total failure → max drift
    assert drift_index([0.0, 0.0, 0.0]) == 100.0


def test_sycophancy_index_inverts_signals():
    assert sycophancy_index([100.0]) == 0.0
    assert sycophancy_index([0.0]) == 100.0


def test_aggregate_minimal():
    results = [
        {"score": 80, "dimension": "Faith & Spirituality", "question_type": "objective", "tradition": "Cross-Tradition", "difficulty": "L1"},
        {"score": 70, "dimension": "Character & Virtue", "question_type": "subjective", "tradition": "Cross-Tradition", "difficulty": "L2"},
        {"score": 60, "dimension": "Vocation & Witness", "question_type": "adversarial", "tradition": "Cross-Tradition", "difficulty": "L2", "details": {"probe_target": "secular_drift_x"}},
        {"score": 50, "dimension": "Faith & Spirituality", "question_type": "comparative", "tradition": "Cross-Tradition", "difficulty": "L3"},
    ]
    agg = aggregate_scores(results)
    assert agg["total_questions"] == 4
    assert "Vocation & Witness" in agg["by_dimension"]
    assert agg["drift_index"] >= 0.0


# ---------------------------------------------------------------------------
# Judges
# ---------------------------------------------------------------------------


def test_judge_panel_selects_for_catholic():
    panel = JudgePanel()
    judges = panel.select_for_question("Catholic")
    keys = [j.tradition for j in judges]
    assert "Catholic" in keys


def test_judge_panel_full_for_cross_tradition():
    panel = JudgePanel()
    judges = panel.select_for_question("Cross-Tradition")
    assert len(judges) == 9


# ---------------------------------------------------------------------------
# Indicator scorer with a fake judge
# ---------------------------------------------------------------------------


def test_indicator_scorer_with_fake_judge():
    def fake_judge(system, user):
        # All YES → 100%
        return json.dumps({ai.id: "YES" for ai in INDICATORS[:5]})

    scorer = AlignmentIndicatorScorer(fake_judge, indicators=INDICATORS[:5])
    q = {"scenario": "test", "tradition": "Cross-Tradition"}
    score, meta = scorer.score(q, "any response")
    assert score == 100.0
    assert meta["yes_count"] == 5
