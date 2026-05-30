"""Tradition-specialist adapter merger.

After training the base general LoRA (SFT+DPO from the main pipeline)
plus per-tradition specialist LoRAs, this tool merges the appropriate
tradition adapter on top of the general adapter for inference.

CLI:
    python -m trainer.deploy.tradition_adapter_merge \\
        --base-model google/gemma-4-31b \\
        --general-adapter outputs/sdg-31b-dpo \\
        --tradition-adapter outputs/sdg-31b-catholic \\
        --out outputs/sdg-31b-catholic-served
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--general-adapter", required=True,
                        help="Path to the general SFT+DPO adapter.")
    parser.add_argument("--tradition-adapter", required=True,
                        help="Path to the per-tradition specialist adapter.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--weights", default="0.7,0.3",
                        help="Weights for general,tradition (must sum to 1.0).")
    args = parser.parse_args()

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        print(f"[merge] requires gpu deps: {exc}")
        return 1

    w_general, w_tradition = [float(x) for x in args.weights.split(",")]
    assert abs(w_general + w_tradition - 1.0) < 1e-6, "weights must sum to 1"

    print(f"[merge] loading base: {args.base_model}")
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16,
        trust_remote_code=True, device_map="auto",
    )
    tok = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)

    print(f"[merge] loading general adapter: {args.general_adapter}")
    model = PeftModel.from_pretrained(base, args.general_adapter, adapter_name="general")
    print(f"[merge] loading tradition adapter: {args.tradition_adapter}")
    model.load_adapter(args.tradition_adapter, adapter_name="tradition")

    # PEFT supports add_weighted_adapter for runtime weighted sum
    print(f"[merge] weighted-merging adapters ({w_general}/{w_tradition})")
    model.add_weighted_adapter(
        adapters=["general", "tradition"],
        weights=[w_general, w_tradition],
        adapter_name="merged",
        combination_type="linear",
    )
    model.set_adapter("merged")

    # Bake the merged adapter into base weights for serving
    merged = model.merge_and_unload()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(out), safe_serialization=True)
    tok.save_pretrained(str(out))
    print(f"[merge] saved -> {out}")
    print(f"\nServe with: bash trainer/deploy/vllm_serve.sh {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
