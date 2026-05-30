"""Publish a checkpoint + model card + eval report to the Hugging Face Hub."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from string import Template


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True,
                        help="Local checkpoint dir (with merged/ subdir).")
    parser.add_argument("--repo", required=True,
                        help="HF Hub repo id (e.g. solideogloria/sdg-27b-v0.1).")
    parser.add_argument("--eval-report", default=None,
                        help="Path to CAB-FF report JSON.")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN"),
                        help="HF token (also via env HF_TOKEN).")
    parser.add_argument("--private", action="store_true",
                        help="Create the repo as private.")
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[publish] huggingface_hub not installed.")
        return 1

    if not args.token:
        print("[publish] No HF token. Set HF_TOKEN or --token.")
        return 1

    api = HfApi(token=args.token)
    print(f"[publish] creating {args.repo} (private={args.private})")
    create_repo(args.repo, token=args.token, private=args.private, exist_ok=True)

    ckpt = Path(args.checkpoint)
    merged = ckpt / "merged" if (ckpt / "merged").exists() else ckpt

    # Render the model card
    template = (Path(__file__).resolve().parents[2] /
                "model_cards" / "sdg_27b_template.md").read_text()
    eval_report = None
    if args.eval_report and Path(args.eval_report).exists():
        eval_report = json.loads(Path(args.eval_report).read_text())
    card = _render_card(template, args.repo, ckpt, eval_report)
    card_path = merged / "README.md"
    card_path.write_text(card)
    print(f"[publish] rendered model card -> {card_path}")

    print(f"[publish] uploading {merged} ...")
    api.upload_folder(repo_id=args.repo, folder_path=str(merged), token=args.token)

    if args.eval_report and Path(args.eval_report).exists():
        api.upload_file(
            repo_id=args.repo,
            path_or_fileobj=args.eval_report,
            path_in_repo="cab_ff_report.json",
            token=args.token,
        )

    print(f"[publish] done -> https://huggingface.co/{args.repo}")
    return 0


def _render_card(template: str, repo: str, ckpt: Path, eval_report: dict | None) -> str:
    meta_path = ckpt / "training_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    eval_section = ""
    if eval_report:
        s = eval_report.get("summary", {})
        eval_section = (
            f"| Metric | Score |\n|---|---:|\n"
            f"| CAB-FF Score | {s.get('cab_ff_score', 0):.2f} |\n"
            f"| Flourishing Score | {s.get('flourishing_score', 0):.2f} |\n"
            f"| Faithfulness Index | {s.get('faithfulness_index', 0):.2f} |\n"
            f"| Drift Index (lower is better) | {s.get('drift_index', 0):.2f} |\n"
            f"| Sycophancy Index (lower is better) | {s.get('sycophancy_index', 0):.2f} |\n"
        )
    return Template(template).safe_substitute(
        REPO=repo,
        BASE_MODEL=meta.get("base_model", "unknown"),
        EVAL_TABLE=eval_section or "_No CAB-FF report attached to this release._",
    )


if __name__ == "__main__":
    sys.exit(main())
