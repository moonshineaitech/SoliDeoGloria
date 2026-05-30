"""Quantize a merged checkpoint to GGUF for Ollama / llama.cpp / consumer GPUs.

Requires `llama.cpp` cloned and built in `$LLAMA_CPP_DIR` (or pass --llama-cpp-dir).
We use llama.cpp's `convert_hf_to_gguf.py` for the HF→GGUF conversion, then
`llama-quantize` for the actual quantization.

Usage:
    LLAMA_CPP_DIR=/opt/llama.cpp \\
        python -m trainer.deploy.quantize_gguf \\
            --checkpoint outputs/sdg-27b-dpo \\
            --quants Q4_K_M Q5_K_M
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--out", default=None,
                        help="Output dir (default: <checkpoint>/gguf)")
    parser.add_argument("--quants", nargs="+",
                        default=["Q4_K_M", "Q5_K_M"],
                        help="GGUF quant levels to produce.")
    parser.add_argument("--llama-cpp-dir", default=os.environ.get("LLAMA_CPP_DIR"))
    args = parser.parse_args()

    if not args.llama_cpp_dir or not Path(args.llama_cpp_dir).exists():
        print("[gguf] LLAMA_CPP_DIR not set or not found. Clone+build llama.cpp first:")
        print("    git clone https://github.com/ggerganov/llama.cpp /opt/llama.cpp")
        print("    cd /opt/llama.cpp && cmake -B build && cmake --build build")
        print("    export LLAMA_CPP_DIR=/opt/llama.cpp")
        return 1

    llcpp = Path(args.llama_cpp_dir)
    convert = llcpp / "convert_hf_to_gguf.py"
    quantize_bin = llcpp / "build" / "bin" / "llama-quantize"
    if not convert.exists():
        print(f"[gguf] convert_hf_to_gguf.py not found at {convert}")
        return 1
    if not quantize_bin.exists():
        print(f"[gguf] llama-quantize not built at {quantize_bin}")
        return 1

    ckpt = Path(args.checkpoint)
    merged = ckpt / "merged" if (ckpt / "merged").exists() else ckpt
    out_dir = Path(args.out) if args.out else ckpt / "gguf"
    out_dir.mkdir(parents=True, exist_ok=True)

    base_gguf = out_dir / "model-f16.gguf"
    print(f"[gguf] HF -> GGUF (f16) ...")
    subprocess.run(
        ["python", str(convert), str(merged), "--outfile", str(base_gguf),
         "--outtype", "f16"],
        check=True,
    )

    for q in args.quants:
        out = out_dir / f"model-{q}.gguf"
        print(f"[gguf] quantizing -> {q}")
        subprocess.run([str(quantize_bin), str(base_gguf), str(out), q], check=True)

    print(f"[gguf] done -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
