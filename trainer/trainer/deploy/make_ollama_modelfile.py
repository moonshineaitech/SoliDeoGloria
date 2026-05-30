"""Generate an Ollama Modelfile for a quantized GGUF checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path


_TEMPLATE = """\
# Generated Modelfile for SoliDeoGloria — Christian-aligned LLM
# Trained with the CAB-FF Trainer; eval gated against the CAB-FF benchmark.

FROM ./{gguf_filename}

TEMPLATE \"\"\"{template}\"\"\"

PARAMETER temperature 0.5
PARAMETER top_p 0.95
PARAMETER top_k 40
PARAMETER num_ctx 8192
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"

SYSTEM \"\"\"You are SoliDeoGloria, a Christian-aligned AI assistant. You
engage Christian theology, pastoral care, ethics, and denominational
diversity with substance and charity. You name Christian categories when
the user uses them (God, prayer, sin, grace, virtue) and stay inside the
tradition the user has specified. You cite Scripture accurately. You
hold sound positions under pushback without being sycophantic. You
refuse the right things — crisis-line on suicidality — and engage
substantively otherwise.\"\"\"

LICENSE \"\"\"
Apache 2.0 — see https://github.com/moonshineaitech/SoliDeoGloria for
the trainer, the benchmark, and the model card.
\"\"\"
"""

_DEFAULT_TEMPLATES = {
    "qwen": (
        "{{- if .System }}<|im_start|>system\n{{ .System }}<|im_end|>\n{{- end }}"
        "{{- range $i, $_ := .Messages }}"
        "{{- $last := eq (len (slice $.Messages $i)) 1 -}}"
        "{{- if eq .Role \"user\" }}<|im_start|>user\n{{ .Content }}<|im_end|>\n"
        "{{- else if eq .Role \"assistant\" }}<|im_start|>assistant\n{{ .Content }}"
        "{{- if not $last }}<|im_end|>\n{{- end }}"
        "{{- end }}"
        "{{- if and $last (ne .Role \"assistant\") }}<|im_start|>assistant\n{{- end }}"
        "{{- end }}"
    ),
    "llama": (
        "<|begin_of_text|>"
        "{{- if .System }}<|start_header_id|>system<|end_header_id|>\n\n{{ .System }}<|eot_id|>{{- end }}"
        "{{- range .Messages }}<|start_header_id|>{{ .Role }}<|end_header_id|>\n\n{{ .Content }}<|eot_id|>{{- end }}"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gguf-dir", required=True,
                        help="Directory containing the .gguf file.")
    parser.add_argument("--quant", default="Q4_K_M",
                        help="Which quant to use (e.g. Q4_K_M, Q5_K_M).")
    parser.add_argument("--family", default="qwen", choices=["qwen", "llama"])
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    gguf_dir = Path(args.gguf_dir)
    gguf_filename = f"model-{args.quant}.gguf"
    if not (gguf_dir / gguf_filename).exists():
        print(f"[ollama] not found: {gguf_dir / gguf_filename}")
        return 1

    out = Path(args.out) if args.out else (gguf_dir / "Modelfile")
    out.write_text(_TEMPLATE.format(
        gguf_filename=gguf_filename,
        template=_DEFAULT_TEMPLATES[args.family],
    ))
    print(f"[ollama] wrote {out}")
    print("\nNext:")
    print(f"  cd {gguf_dir}")
    print(f"  ollama create solideogloria -f Modelfile")
    print(f"  ollama run solideogloria")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
