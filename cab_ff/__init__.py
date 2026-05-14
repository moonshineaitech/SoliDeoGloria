"""
CAB v3.0 — Flourishing & Faithfulness Benchmark (CAB-FF)

A successor to CAB v2.0 designed to evaluate AI systems on the seven
research-backed dimensions of human flourishing (Harvard Human Flourishing
Program) AND a distinctively Christian eighth dimension (Vocation & Witness),
scored against seven transverse faithfulness axes including doctrinal
fidelity, scriptural grounding, secular-drift resistance, and sycophancy
resistance.

Built to be more rigorous, broader, and more reproducible than Gloo's
private FAI-C benchmark.
"""

__version__ = "3.0.0"
__author__ = "GoldRock AI / Soli Deo Gloria Research Initiative"

from .dimensions import (
    DIMENSIONS,
    DIMENSION_SYMBOLS,
    TRANSVERSE_AXES,
    QUESTION_TYPES,
    TRADITIONS,
)
from .loader import load_dataset, get_statistics
from .scorer import (
    ObjectiveScorer,
    SubjectiveScorer,
    AdversarialScorer,
    MultiTurnScorer,
    ComparativeScorer,
    AlignmentIndicatorScorer,
)
from .aggregator import (
    aggregate_scores,
    flourishing_score,
    faithfulness_index,
    final_cab_ff_score,
    drift_index,
    sycophancy_index,
)
from .judges import JUDGE_PERSONAS, JudgePanel
from .evaluator import CABFFEvaluator

__all__ = [
    "DIMENSIONS",
    "DIMENSION_SYMBOLS",
    "TRANSVERSE_AXES",
    "QUESTION_TYPES",
    "TRADITIONS",
    "JUDGE_PERSONAS",
    "JudgePanel",
    "load_dataset",
    "get_statistics",
    "ObjectiveScorer",
    "SubjectiveScorer",
    "AdversarialScorer",
    "MultiTurnScorer",
    "ComparativeScorer",
    "AlignmentIndicatorScorer",
    "aggregate_scores",
    "flourishing_score",
    "faithfulness_index",
    "final_cab_ff_score",
    "drift_index",
    "sycophancy_index",
    "CABFFEvaluator",
]
