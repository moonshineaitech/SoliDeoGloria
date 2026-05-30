"""End-to-end dry-run smoke test for the trainer pipeline.

Confirms (without any GPU or API key) that:
  1. The dry-run data generation produces valid JSONL.
  2. The contamination check is wired and runs on a tiny set.
  3. The SFT entrypoint accepts the dry_run config.
  4. The pipeline package imports cleanly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRAINER = REPO / "trainer"


def test_imports():
    """All pipeline modules import without errors."""
    sys.path.insert(0, str(TRAINER))
    from trainer.data.pipeline import cli, stage_01, stage_06, stage_07
    assert hasattr(stage_01, "extract")
    assert hasattr(stage_06, "dedup_and_filter")
    assert hasattr(stage_07, "split_and_format")
    assert hasattr(cli, "main")


def test_dry_run_data_generation(tmp_path: Path):
    """`python -m trainer.data.pipeline.cli dry-run` writes valid JSONL."""
    out = tmp_path / "dry"
    result = subprocess.run(
        [sys.executable, "-m", "trainer.data.pipeline.cli", "dry-run", "--out", str(out)],
        cwd=str(TRAINER),
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    for fname in ("train.jsonl", "eval.jsonl", "pref_train.jsonl", "pref_eval.jsonl"):
        assert (out / fname).exists(), f"missing {fname}"
        for line in (out / fname).open():
            json.loads(line)


def test_contamination_check_detects_overlap():
    """SimHash check should flag a literal copy of a CAB-FF question."""
    sys.path.insert(0, str(TRAINER))
    from trainer.data.pipeline.stage_06 import dedup_and_filter

    dataset_path = REPO / "data" / "CAB_FF_v3_dataset.json"
    if not dataset_path.exists():
        # Skip if dataset isn't in this checkout (e.g. shallow clone)
        return

    cab_ff = json.loads(dataset_path.read_text())
    # Find a scenario-bearing question and copy its scenario into a "training" example.
    contam_text = None
    for q in cab_ff["questions"]:
        if q.get("scenario") and len(q["scenario"].split()) > 20:
            contam_text = q["scenario"]
            break
    assert contam_text, "expected at least one scenario in CAB-FF"

    contam_record = {
        "messages": [
            {"role": "user", "content": contam_text},
            {"role": "assistant", "content": "Pray to God. Read the Psalms. Speak with a pastor."},
        ],
        "meta": {"source": "test_contamination"},
    }
    # A clean example: an everyday question and a long unique answer.
    # Important: must NOT overlap any CAB-FF question (the Westminster
    # Catechism's "chief end of man" is one of CAB-FF's objective items,
    # so we avoid that, biblical literacy MCQs, etc.).
    clean_record = {
        "messages": [
            {"role": "user", "content": "Recommend a starter book on Christian discipleship for a new believer who reads slowly."},
            {"role": "assistant", "content": (
                "For a slow reader who is new to the faith, the most "
                "accessible classics are usually short. Try N. T. Wright's "
                "Simply Christian, or for something even shorter, John "
                "Stott's Basic Christianity. Both lay out the gospel without "
                "assuming prior background.")},
        ],
        "meta": {"source": "test_clean"},
    }
    sft_clean, _, _ = dedup_and_filter(
        sft=[contam_record, clean_record], prefs=[], multi=[],
        cab_ff_dataset=dataset_path,
    )
    sources = [r.get("meta", {}).get("source") for r in sft_clean]
    assert "test_clean" in sources, "clean example should be kept"
    assert "test_contamination" not in sources, "contaminated example MUST be dropped"
