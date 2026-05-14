"""
CAB-FF v3.0 — Main evaluator orchestrating all five question types.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .aggregator import aggregate_scores
from .alignment_indicators import select_indicators
from .judges import JudgePanel
from .loader import filter_questions, load_dataset
from .scorer import (
    AdversarialScorer,
    AlignmentIndicatorScorer,
    ComparativeScorer,
    MultiTurnScorer,
    ObjectiveScorer,
    SubjectiveScorer,
)


ModelFn = Callable[[str], str]
JudgeFn = Callable[[str, str], str]


@dataclass
class EvaluationConfig:
    apply_alignment_indicators: bool = True
    indicator_categories: Optional[List[str]] = None
    randomize_objective_options: bool = True
    panel: Optional[JudgePanel] = None
    verbose: bool = True


class CABFFEvaluator:
    """Run the full CAB-FF evaluation on a model.

    The caller supplies:
        model_fn  — single-string -> string, the model under test
        judge_fn  — (system, user) -> string, an LLM judge call

    Implementations are kept opaque so this works with any backend.
    """

    def __init__(
        self,
        model_fn: ModelFn,
        judge_fn: Optional[JudgeFn] = None,
        config: Optional[EvaluationConfig] = None,
    ):
        self.model_fn = model_fn
        self.judge_fn = judge_fn
        self.config = config or EvaluationConfig()
        panel = self.config.panel or JudgePanel()

        self.objective = ObjectiveScorer(
            randomize_options=self.config.randomize_objective_options,
        )
        self.subjective = SubjectiveScorer(judge_fn, panel) if judge_fn else None
        self.adversarial = AdversarialScorer(judge_fn=judge_fn)
        self.multi_turn = MultiTurnScorer(model_fn, judge_fn, panel) if judge_fn else None
        self.comparative = ComparativeScorer(model_fn, judge_fn) if judge_fn else None

        indicators = select_indicators(categories=self.config.indicator_categories)
        self.indicators = (
            AlignmentIndicatorScorer(judge_fn, indicators) if judge_fn else None
        )

    def evaluate(
        self,
        dataset_path: str,
        dimensions: Optional[List[str]] = None,
        traditions: Optional[List[str]] = None,
        question_type: Optional[str] = None,
        max_questions: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> Dict:
        data = load_dataset(dataset_path)
        questions = filter_questions(
            data["questions"],
            dimensions=dimensions,
            traditions=traditions,
            question_type=question_type,
        )
        if max_questions:
            questions = questions[:max_questions]

        if self.config.verbose:
            print(f"Evaluating {len(questions)} questions against CAB-FF v3.0…")

        results: List[Dict] = []
        for q in questions:
            results.append(self._evaluate_one(q))

        summary = aggregate_scores(results)
        report = {
            "metadata": {
                "benchmark": "CAB-FF v3.0",
                "dataset_version": data.get("version"),
                "timestamp": datetime.now().isoformat(),
                "questions_evaluated": len(questions),
                "filters": {
                    "dimensions": dimensions,
                    "traditions": traditions,
                    "question_type": question_type,
                },
            },
            "summary": summary,
            "detailed_results": results,
        }
        if output_path:
            Path(output_path).write_text(json.dumps(report, indent=2))
            if self.config.verbose:
                print(f"Wrote {output_path}")
        return report

    def _evaluate_one(self, q: Dict) -> Dict:
        record = {
            "id": q["id"],
            "dimension": q["dimension"],
            "tradition": q["tradition"],
            "difficulty": q["difficulty"],
            "question_type": q["question_type"],
        }
        qtype = q["question_type"]

        if qtype == "objective":
            prompt, meta = self.objective.prepare_question(q)
            response = self.model_fn(prompt)
            score, details = self.objective.score(q, response, metadata=meta)
            record["score"] = score
            record["details"] = details

        elif qtype == "subjective":
            if not self.subjective:
                raise RuntimeError("judge_fn required for subjective questions")
            prompt = self.subjective.prepare_question(q)
            response = self.model_fn(prompt)
            score, details = self.subjective.score(q, response)
            record["score"] = score
            record["details"] = details
            self._maybe_attach_indicators(q, response, details, record)

        elif qtype == "adversarial":
            response = self.model_fn(q["scenario"])
            score, details = self.adversarial.score(q, response)
            record["score"] = score
            record["details"] = details
            self._maybe_attach_indicators(q, response, details, record)

        elif qtype == "multi_turn":
            if not self.multi_turn:
                raise RuntimeError("judge_fn required for multi_turn questions")
            score, details = self.multi_turn.score(q)
            record["score"] = score
            record["details"] = details
            final_resp = details["transcript"][-1]["assistant"]
            self._maybe_attach_indicators(q, final_resp, details, record)

        elif qtype == "comparative":
            if not self.comparative:
                raise RuntimeError("judge_fn required for comparative questions")
            score, details = self.comparative.score(q)
            record["score"] = score
            record["details"] = details

        if "axis_scores" in q:
            record["axis_scores"] = q["axis_scores"]
        elif (q.get("axis_targets")):
            record["axis_scores"] = {a: record.get("score", 0.0) for a in q["axis_targets"]}

        return record

    def _maybe_attach_indicators(self, q: Dict, response: str, details: Dict, record: Dict) -> None:
        if not (self.config.apply_alignment_indicators and self.indicators):
            return
        ai_score, ai_meta = self.indicators.score(q, response)
        details["alignment_indicators"] = ai_meta
        # Blend: subjective_score 0.7 + indicator_score 0.3
        if record.get("score") is not None:
            record["score"] = 0.7 * record["score"] + 0.3 * ai_score
            record["details"]["composite_blend"] = {
                "base_score": ai_meta.get("base_score"),
                "indicator_score": ai_score,
                "weight_base": 0.7,
                "weight_indicators": 0.3,
            }
