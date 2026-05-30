"""Quantize a merged checkpoint to AWQ INT4 for vLLM serving.

Usage:
    python -m trainer.deploy.quantize_awq --checkpoint outputs/sdg-27b-dpo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True,
                        help="Path to merged BF16 safetensors dir.")
    parser.add_argument("--out", default=None,
                        help="Output dir. Default: <checkpoint>/awq.")
    parser.add_argument("--calib-samples", type=int, default=128)
    parser.add_argument("--group-size", type=int, default=128)
    args = parser.parse_args()

    try:
        from awq import AutoAWQForCausalLM
        from transformers import AutoTokenizer
    except ImportError as exc:
        print(f"[awq] autoawq not installed ({exc}). "
              f"Install: pip install -e '.[deploy]'")
        return 1

    checkpoint = Path(args.checkpoint) / "merged" if (Path(args.checkpoint) / "merged").exists() else Path(args.checkpoint)
    out_dir = Path(args.out) if args.out else (Path(args.checkpoint) / "awq")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[awq] loading {checkpoint}")
    model = AutoAWQForCausalLM.from_pretrained(str(checkpoint),
                                                safetensors=True, device_map="auto")
    tok = AutoTokenizer.from_pretrained(str(checkpoint), trust_remote_code=True)

    quant_config = {
        "zero_point": True,
        "q_group_size": args.group_size,
        "w_bit": 4,
        "version": "GEMM",
    }
    print(f"[awq] quantizing with {args.calib_samples} calibration samples...")
    model.quantize(tok, quant_config=quant_config, calib_data="pileval",
                   max_calib_samples=args.calib_samples)
    model.save_quantized(str(out_dir))
    tok.save_pretrained(str(out_dir))
    print(f"[awq] done -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
