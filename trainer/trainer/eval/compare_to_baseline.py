"""Render a diff of two CAB-FF reports (one base, one trained).

Output is a Markdown table suitable for pasting into a PR description or
a model-card eval section.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-report", required=True)
    parser.add_argument("--baseline-report", required=True)
    parser.add_argument("--checkpoint-name", default="trained")
    parser.add_argument("--baseline-name", default="base")
    args = parser.parse_args()

    ckpt = json.loads(Path(args.checkpoint_report).read_text())["summary"]
    base = json.loads(Path(args.baseline_report).read_text())["summary"]

    print(f"# CAB-FF: {args.checkpoint_name} vs {args.baseline_name}\n")
    print(f"| Metric | {args.baseline_name} | {args.checkpoint_name} | Δ |")
    print("|---|---:|---:|---:|")
    for metric in ("cab_ff_score", "flourishing_score", "faithfulness_index",
                   "drift_index", "sycophancy_index"):
        b = base.get(metric, 0.0)
        c = ckpt.get(metric, 0.0)
        d = c - b
        sign = "+" if d > 0 else ""
        print(f"| {metric} | {b:.2f} | {c:.2f} | {sign}{d:.2f} |")

    print("\n## Per-dimension\n")
    print(f"| Dimension | {args.baseline_name} | {args.checkpoint_name} | Δ |")
    print("|---|---:|---:|---:|")
    base_dims = base.get("by_dimension", {})
    ckpt_dims = ckpt.get("by_dimension", {})
    for dim in sorted(base_dims):
        b = (base_dims[dim] or {}).get("score", 0.0)
        c = (ckpt_dims.get(dim, {}) or {}).get("score", 0.0)
        d = c - b
        sign = "+" if d > 0 else ""
        print(f"| {dim} | {b:.2f} | {c:.2f} | {sign}{d:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
