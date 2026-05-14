#!/usr/bin/env python3
"""Build the CAB-FF v3.0 dataset JSON from the question banks.

Combines:
  - the original 80-question hand-authored seed (`data/CAB_FF_v3_seed.json`)
  - all bank modules under `cab_ff/banks/bank_*.py`

into a single dataset with sequential `CABFF-NNNN` IDs, then validates
against the loader and writes the result to disk.

Usage:
    python scripts/build_dataset.py [--out data/CAB_FF_v3_dataset.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cab_ff.banks import collect as collect_banks
from cab_ff.loader import load_dataset, get_statistics


SEED_PATH = ROOT / "data" / "CAB_FF_v3_seed.json"


def _strip_seed_ids(seed_questions: list[dict]) -> list[dict]:
    """Strip incoming IDs so renumber() assigns fresh sequential ones."""
    out = []
    for q in seed_questions:
        q = dict(q)
        q.pop("id", None)
        out.append(q)
    return out


def _text_key(q: dict) -> str:
    """Stable normalized text fingerprint for deduplication."""
    parts: list[str] = []
    for field in ("question", "scenario"):
        if q.get(field):
            parts.append(q[field])
    if q.get("prompts"):
        parts.append(q["prompts"].get("neutral", ""))
        parts.append(q["prompts"].get("christian", ""))
    if q.get("turns"):
        parts.extend(t.get("content", "") for t in q["turns"])
    return " | ".join(p.strip().lower()[:200] for p in parts if p)


def _check_no_duplicates(questions: list[dict]) -> None:
    """Raise if any two questions share their text fingerprint."""
    seen: dict[str, int] = {}
    dupes: list[tuple[int, int, str]] = []
    for i, q in enumerate(questions):
        key = _text_key(q)
        if not key:
            continue
        if key in seen:
            dupes.append((seen[key], i, key[:80]))
        else:
            seen[key] = i
    if dupes:
        lines = "\n".join(f"  positions {a} and {b}: {k}" for a, b, k in dupes)
        raise ValueError(f"Found {len(dupes)} duplicate questions:\n{lines}")


def assemble() -> dict:
    # Existing hand-authored seed: keep them first so their `CABFF-0001..` numbering
    # is preserved as a stable prefix.
    seed_doc = json.loads(SEED_PATH.read_text())
    seed_questions = _strip_seed_ids(seed_doc["questions"])
    bank_questions = collect_banks()

    questions: list[dict] = seed_questions + bank_questions
    _check_no_duplicates(questions)
    for i, q in enumerate(questions, start=1):
        q["id"] = f"CABFF-{i:04d}"

    return {
        "benchmark": "CAB-FF: Flourishing & Faithfulness Benchmark",
        "version": "3.0",
        "created": datetime.now().date().isoformat(),
        "publisher": "Eldest AI LLC dba GoldRock AI",
        "license": "CC BY-SA 4.0",
        "description": (
            "Dataset assembled from the 80-question seed plus the per-dimension "
            "and cross-cutting question banks under cab_ff/banks/. Run "
            "scripts/build_dataset.py to regenerate."
        ),
        "total_questions": len(questions),
        "questions": questions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "CAB_FF_v3_dataset.json"),
        help="Output path for the assembled dataset JSON.",
    )
    args = parser.parse_args()
    out_path = Path(args.out)

    dataset = assemble()
    out_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False))
    print(f"Wrote {len(dataset['questions'])} questions to {out_path}")

    # Validate via the loader (will raise on bad records).
    loaded = load_dataset(out_path)
    stats = get_statistics(loaded)
    print(f"\nValidated. Total: {stats['total']}")
    for header, key in [
        ("By dimension", "by_dimension"),
        ("By question type", "by_type"),
        ("By tradition", "by_tradition"),
        ("By difficulty", "by_difficulty"),
    ]:
        print(f"\n{header}:")
        for k, v in sorted(stats[key].items()):
            print(f"  {k:<40} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
