"""Tests for the ship-today tooling: preflight, cost estimator, run_all."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TRAINER = Path(__file__).resolve().parents[1]


def test_cost_estimator_all_presets_runs():
    r = subprocess.run(
        [sys.executable, "-m", "trainer.scripts.cost_estimate", "--all-presets"],
        cwd=str(TRAINER), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "TOTAL" in r.stdout
    assert "e4b-cheap" in r.stdout
    assert "gemma-31b" in r.stdout


def test_cost_estimator_single_preset_has_total():
    r = subprocess.run(
        [sys.executable, "-m", "trainer.scripts.cost_estimate", "--preset", "gemma-31b"],
        cwd=str(TRAINER), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "TOTAL ESTIMATE" in r.stdout


def test_cost_estimator_overrides():
    """Custom GPU rate + hours should be respected."""
    r = subprocess.run(
        [sys.executable, "-m", "trainer.scripts.cost_estimate",
         "--gpu-hourly", "2.00", "--train-hours", "5", "--iterate-rounds", "0",
         "--n-evals", "1", "--n-examples", "10000", "--teacher", "gpt-4o-mini",
         "--judge", "gpt-4o"],
        cwd=str(TRAINER), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    # 5 GPU-hr * $2.00 = $10 compute
    assert "$10" in r.stdout


def test_preflight_runs_and_reports():
    """Preflight should run to completion (non-zero exit on CPU box is fine)."""
    r = subprocess.run(
        [sys.executable, "-m", "trainer.scripts.preflight",
         "--min-disk-gb", "1", "--min-vram-gb", "1"],
        cwd=str(TRAINER), capture_output=True, text=True,
    )
    # On a CPU box without the GPU stack this exits non-zero — that's correct.
    assert "PREFLIGHT" in r.stdout
    # The dataset check must find the repo dataset (path resolution is correct).
    assert "CAB-FF dataset found" in r.stdout


def test_run_all_script_is_valid_bash():
    script = TRAINER / "scripts" / "run_all.sh"
    assert script.exists()
    r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    assert r.returncode == 0, f"bash syntax error: {r.stderr}"


def test_run_today_guide_exists_and_has_three_paths():
    guide = TRAINER / "RUN_TODAY.md"
    assert guide.exists()
    text = guide.read_text()
    assert "PATH A" in text and "PATH B" in text and "PATH C" in text
    # Every path should have a concrete cost
    assert "$10" in text or "$10-20" in text
