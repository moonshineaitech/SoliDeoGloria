"""Question banks for CAB-FF v3.0. Each bank module exports QUESTIONS: list[dict]."""

import importlib
import pkgutil
from pathlib import Path


def _discover_banks() -> list:
    """Discover every `bank_*` module in this package, in alphabetical order."""
    pkg_dir = Path(__file__).parent
    names = sorted(
        m.name for m in pkgutil.iter_modules([str(pkg_dir)])
        if m.name.startswith("bank_")
    )
    return [importlib.import_module(f"{__name__}.{n}") for n in names]


def collect() -> list[dict]:
    """Collect QUESTIONS from every bank in discovery order."""
    out: list[dict] = []
    for bank in _discover_banks():
        out.extend(getattr(bank, "QUESTIONS", []))
    return out
