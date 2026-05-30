"""Per-dimension drilldown — identifies the weakest dimension/axis from
a CAB-FF eval report, with optional comparison to a baseline.

Used by the iterate.py loop to pick the next round's training target.

CLI:
    python -m trainer.eval.per_dimension_drilldown \\
        --report outputs/sdg-31b-dpo/cab_ff_report.json \\
        --baseline baselines/gemma_4_31b_base_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--baseline", default=None,
                        help="Optional baseline report for delta analysis.")
    parser.add_argument("--top-n", type=int, default=3,
                        help="Show top-N weakest dimensions / axes.")
    parser.add_argument("--out-json", default=None,
                        help="Write machine-readable summary here.")
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text())["summary"]
    baseline = None
    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text())["summary"]

    by_dim = report.get("by_dimension", {})
    by_axis = report.get("by_axis", {})

    dim_rows = _rank(by_dim, baseline and baseline.get("by_dimension", {}))
    axis_rows = _rank(by_axis, baseline and baseline.get("by_axis", {}))

    print("\n" + "=" * 70)
    print("CAB-FF Per-Dimension Drilldown")
    print("=" * 70)
    print(f"\n  CAB-FF score:        {report.get('cab_ff_score', 0):6.2f}")
    if baseline:
        bs = baseline.get("cab_ff_score", 0)
        print(f"  Baseline score:      {bs:6.2f}")
        print(f"  Delta:               {report.get('cab_ff_score', 0) - bs:+6.2f}")
    print(f"  Drift Index:         {report.get('drift_index', 0):6.2f}  (lower better)")
    print(f"  Sycophancy Index:    {report.get('sycophancy_index', 0):6.2f}  (lower better)")

    print(f"\n  Weakest dimensions (worst {args.top_n}):")
    for name, score, delta in dim_rows[:args.top_n]:
        delta_str = f" (Δ {delta:+.2f} vs base)" if delta is not None else ""
        print(f"    • {name:<40} {score:6.2f}{delta_str}")

    print(f"\n  Weakest axes (worst {args.top_n}):")
    for name, score, delta in axis_rows[:args.top_n]:
        delta_str = f" (Δ {delta:+.2f} vs base)" if delta is not None else ""
        print(f"    • {name:<40} {score:6.2f}{delta_str}")

    # Suggested action
    if dim_rows:
        weakest_dim = dim_rows[0][0]
        weakest_axis = axis_rows[0][0] if axis_rows else "Doctrinal Fidelity"
        print(f"\n  → Next-round target:")
        print(f"      dimension: {weakest_dim}")
        print(f"      axis:      {weakest_axis}")
        print(f"      Generate +2000 examples with these filters.\n")

    if args.out_json:
        Path(args.out_json).write_text(json.dumps({
            "weakest_dimension": dim_rows[0][0] if dim_rows else None,
            "weakest_axis": axis_rows[0][0] if axis_rows else None,
            "dimension_ranking": [
                {"name": n, "score": s, "delta_vs_base": d}
                for n, s, d in dim_rows
            ],
            "axis_ranking": [
                {"name": n, "score": s, "delta_vs_base": d}
                for n, s, d in axis_rows
            ],
        }, indent=2))
    return 0


def _rank(d: Dict, baseline: Dict | None) -> List[Tuple[str, float, float | None]]:
    """Return (name, score, delta_vs_baseline) sorted ascending by score."""
    rows = []
    for name, info in (d or {}).items():
        s = info.get("score", 0.0) if isinstance(info, dict) else float(info)
        delta = None
        if baseline and name in baseline:
            bi = baseline[name]
            bs = bi.get("score", 0.0) if isinstance(bi, dict) else float(bi)
            delta = s - bs
        rows.append((name, s, delta))
    rows.sort(key=lambda x: x[1])
    return rows


if __name__ == "__main__":
    sys.exit(main())
