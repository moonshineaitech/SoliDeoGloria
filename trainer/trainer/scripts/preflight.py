"""Preflight check — run this the moment your GPU box boots, BEFORE you
spend money on data generation or training.

The #1 way people waste money on rented GPUs is renting the box, then
discovering 30 minutes in that CUDA is wrong / disk is full / the API
key is missing / the base model is gated. This script catches all of
that in ~20 seconds.

Exit code 0 = good to go. Non-zero = fix the reported problems first.

    python -m trainer.scripts.preflight --config configs/sft_gemma_4_31b.yaml
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


class Check:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def ok(self, msg: str) -> None:
        print(f"  {GREEN}✓{RESET} {msg}")

    def fail(self, msg: str, fix: str) -> None:
        print(f"  {RED}✗{RESET} {msg}")
        print(f"      {YELLOW}fix:{RESET} {fix}")
        self.failures.append(msg)

    def warn(self, msg: str, note: str) -> None:
        print(f"  {YELLOW}!{RESET} {msg}")
        print(f"      {note}")
        self.warnings.append(msg)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None,
                        help="SFT config to validate base-model access against.")
    parser.add_argument("--need-teacher", action="store_true", default=True,
                        help="Require a teacher API key (for data generation).")
    parser.add_argument("--min-disk-gb", type=int, default=200,
                        help="Minimum free disk in GB.")
    parser.add_argument("--min-vram-gb", type=int, default=40,
                        help="Minimum total VRAM in GB.")
    args = parser.parse_args()

    print(f"\n{BOLD}CAB-FF Trainer — Preflight Check{RESET}\n")
    c = Check()

    # 1. Python version
    print(f"{BOLD}Environment{RESET}")
    if sys.version_info >= (3, 10):
        c.ok(f"Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        c.fail(f"Python {sys.version_info.major}.{sys.version_info.minor} too old",
               "Need Python 3.10+. Use a 3.11 image.")

    # 2. Disk space
    free_gb = shutil.disk_usage(".").free / (1024 ** 3)
    if free_gb >= args.min_disk_gb:
        c.ok(f"Disk: {free_gb:.0f} GB free (need {args.min_disk_gb})")
    else:
        c.fail(f"Disk: only {free_gb:.0f} GB free (need {args.min_disk_gb})",
               "Pick a box with a bigger volume, or set --min-disk-gb lower "
               "for a smaller base model. A 31B base + checkpoints needs ~200GB.")

    # 3. GPU / CUDA
    print(f"\n{BOLD}GPU{RESET}")
    try:
        import torch
        if torch.cuda.is_available():
            n = torch.cuda.device_count()
            total_vram = sum(
                torch.cuda.get_device_properties(i).total_memory
                for i in range(n)
            ) / (1024 ** 3)
            names = {torch.cuda.get_device_name(i) for i in range(n)}
            c.ok(f"{n}× GPU ({', '.join(names)}), {total_vram:.0f} GB total VRAM")
            if total_vram < args.min_vram_gb:
                c.warn(f"VRAM {total_vram:.0f}GB < recommended {args.min_vram_gb}GB",
                       "You may need a smaller base (Gemma 4 E4B) or QLoRA.")
            # bf16 support
            if torch.cuda.is_bf16_supported():
                c.ok("bf16 supported")
            else:
                c.warn("bf16 NOT supported on this GPU",
                       "Set bf16: false / fp16: true in your config (older GPU).")
        else:
            c.fail("CUDA not available to PyTorch",
                   "On a GPU box: check `nvidia-smi` works, and that your torch "
                   "build matches CUDA. Reinstall: pip install torch --index-url "
                   "https://download.pytorch.org/whl/cu124")
    except ImportError:
        c.fail("PyTorch not installed",
               "pip install -e '.[gpu]' on the GPU box.")

    # 4. Core training deps
    print(f"\n{BOLD}Training stack{RESET}")
    for pkg, fix in [
        ("transformers", "pip install -e '.[gpu]'"),
        ("trl", "pip install -e '.[gpu]'"),
        ("peft", "pip install -e '.[gpu]'"),
        ("datasets", "pip install -e '.[gpu]'"),
        ("accelerate", "pip install -e '.[gpu]'"),
    ]:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "?")
            c.ok(f"{pkg} {ver}")
        except ImportError:
            c.fail(f"{pkg} not installed", fix)

    # peft DoRA support
    try:
        import peft
        from peft import LoraConfig
        if "use_dora" in LoraConfig.__dataclass_fields__:
            c.ok("peft supports DoRA (use_dora)")
        else:
            c.warn("peft too old for DoRA",
                   "pip install -U 'peft>=0.10' — configs default to DoRA.")
    except Exception:
        pass

    # flash-attn (optional but big speedup)
    try:
        import flash_attn  # noqa: F401
        c.ok(f"flash-attn {getattr(flash_attn, '__version__', '?')}")
    except ImportError:
        c.warn("flash-attn not installed (training will be ~2x slower)",
               "pip install flash-attn==2.7.0 --no-build-isolation")

    # liger (optional speedup)
    try:
        import liger_kernel  # noqa: F401
        c.ok("liger-kernel installed")
    except ImportError:
        c.warn("liger-kernel not installed (training will be slower)",
               "pip install liger-kernel")

    # 5. Teacher API key (for data generation)
    print(f"\n{BOLD}API keys{RESET}")
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    if has_anthropic:
        c.ok("ANTHROPIC_API_KEY set")
    if has_openai:
        c.ok("OPENAI_API_KEY set")
    if args.need_teacher and not (has_anthropic or has_openai):
        c.fail("No teacher API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)",
               "export ANTHROPIC_API_KEY=sk-ant-...  (needed for `make data`)")

    has_hf = bool(os.environ.get("HF_TOKEN"))
    if has_hf:
        c.ok("HF_TOKEN set")
    else:
        c.warn("HF_TOKEN not set",
               "Needed to download gated bases and to publish. "
               "export HF_TOKEN=hf_...")

    # 6. Base-model access
    if args.config:
        print(f"\n{BOLD}Base model access{RESET}")
        try:
            import yaml
            cfg = yaml.safe_load(Path(args.config).read_text())
            base = cfg["model"]["base_model"]
            try:
                from huggingface_hub import model_info
                model_info(base, token=os.environ.get("HF_TOKEN"))
                c.ok(f"Can access {base} on the Hub")
            except Exception as exc:
                c.fail(f"Cannot access {base}: {exc}",
                       f"Accept the license at https://huggingface.co/{base} "
                       f"and set HF_TOKEN.")
        except Exception as exc:
            c.warn(f"Could not read config {args.config}: {exc}", "")

    # 7. CAB-FF dataset present (repo root is two levels above trainer/)
    print(f"\n{BOLD}Benchmark data{RESET}")
    # preflight.py lives at trainer/trainer/scripts/ ; repo root = parents[3]
    candidates = [
        Path(__file__).resolve().parents[3] / "data" / "CAB_FF_v3_dataset.json",
        Path(__file__).resolve().parents[2] / "data" / "CAB_FF_v3_dataset.json",
        Path("../data/CAB_FF_v3_dataset.json"),
        Path("data/CAB_FF_v3_dataset.json"),
    ]
    found = next((p for p in candidates if p.exists()), None)
    if found:
        c.ok(f"CAB-FF dataset found ({found})")
    else:
        c.fail("CAB-FF dataset not found in any expected location",
               "Run from inside the full repo; the dataset should be at "
               "<repo>/data/CAB_FF_v3_dataset.json.")

    # Verdict
    print(f"\n{BOLD}{'='*50}{RESET}")
    if c.failures:
        print(f"{RED}{BOLD}PREFLIGHT FAILED{RESET} — {len(c.failures)} blocker(s), "
              f"{len(c.warnings)} warning(s).")
        print(f"{RED}Fix the blockers above before spending money on training.{RESET}\n")
        return 1
    if c.warnings:
        print(f"{YELLOW}{BOLD}PREFLIGHT OK (with {len(c.warnings)} warning(s)){RESET} "
              f"— you can proceed, but review the warnings.\n")
        return 0
    print(f"{GREEN}{BOLD}PREFLIGHT PASSED{RESET} — everything checks out. "
          f"You're clear to run `make data` and train.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
