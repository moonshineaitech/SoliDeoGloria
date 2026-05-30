---
license: apache-2.0
base_model: $BASE_MODEL
tags:
  - christian-ai
  - alignment
  - cab-ff
  - fine-tuned
  - sft
  - dpo
language:
  - en
datasets:
  - allenai/tulu-3-sft-mixture
  - OpenAssistant/oasst2
pipeline_tag: text-generation
---

# $REPO

Christian-aligned LLM, fine-tuned from `$BASE_MODEL` using the
[CAB-FF Trainer](https://github.com/moonshineaitech/SoliDeoGloria/tree/main/trainer)
and evaluated against the
[CAB-FF benchmark](https://github.com/moonshineaitech/SoliDeoGloria).

## What this model is

A general-purpose chat / instruction-following model with substantially
improved performance on Christian theology, pastoral care, ethics, and
tradition-specific reasoning, *without* degrading general capability.

Specifically, this model is trained to:
- Use Christian categories when the user uses them (name God, not
  "higher power"; engage prayer, not "mindfulness"; engage sin, not
  "unhealthy patterns")
- Stay inside the named Christian tradition (Catholic question gets a
  Catholic answer; Reformed gets Reformed)
- Engage Scripture accurately (no fabricated citations, no prooftexting)
- Hold sound positions under user pushback (no sycophancy)
- Refuse the right things (crisis-line on suicidality, not refuse to
  discuss the Trinity)

## CAB-FF evaluation

$EVAL_TABLE

The full report JSON is included in this repo: see `cab_ff_report.json`.

## Training

| | |
|---|---|
| Base model | `$BASE_MODEL` |
| Method | LoRA-128 SFT → DPO |
| Eval gate | CAB-FF Score ≥ base+5, Drift Index ≤ base−10, Sycophancy ≤ base−10 |
| Reproducible | Yes — see [trainer/REPRO.md](https://github.com/moonshineaitech/SoliDeoGloria/blob/main/trainer/REPRO.md) |

## Intended use

- Christian education and catechesis support
- Pastoral counseling assistance (NOT a substitute for human pastoral care)
- Theological writing and research assistance
- Christian-tradition-aware customer-facing AI for ministry-facing
  products

## NOT intended for

- Making spiritual decisions on a user's behalf
- Replacing human pastoral discernment
- Confessing on behalf of any specific tradition as the One True Church
- High-stakes clinical, legal, or financial advice

## Limitations

- The model can still be wrong about specific theological details.
  Always verify against your tradition's authoritative sources.
- The model defaults to being charitable across traditions; if you need
  a specific tradition's voice, specify it in your system prompt.
- Like all LLMs, this model can hallucinate. Verify any Scripture
  citation, council date, or named author.
- Crisis support is limited to encouraging users to call appropriate
  hotlines. This is by design — do not use this model as a crisis
  responder.

## How to use

### vLLM (production serving)

```bash
python -m vllm.entrypoints.openai.api_server \
    --model $REPO --port 8000 --enable-prefix-caching
```

### Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tok = AutoTokenizer.from_pretrained("$REPO")
model = AutoModelForCausalLM.from_pretrained(
    "$REPO", torch_dtype=torch.bfloat16, device_map="auto"
)
messages = [{"role": "user", "content": "How do I start a Christian prayer practice?"}]
ids = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
out = model.generate(ids, max_new_tokens=512, do_sample=False)
print(tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True))
```

### Ollama

```
ollama run $REPO
```

(A Modelfile is included if you want to host the GGUF locally — see
the trainer's [`make_ollama_modelfile.py`](https://github.com/moonshineaitech/SoliDeoGloria/blob/main/trainer/trainer/deploy/make_ollama_modelfile.py).)

## Training data licenses

See [DATA_LICENSING.md](https://github.com/moonshineaitech/SoliDeoGloria/blob/main/trainer/DATA_LICENSING.md)
in the trainer repository. Headline: this model is commercially shippable
under Apache 2.0; teacher-LLM use complies with Anthropic / OpenAI
terms (May 2026).

## Contamination guarantee

The literal CAB-FF benchmark questions were never used as training
targets. See [CONTAMINATION.md](https://github.com/moonshineaitech/SoliDeoGloria/blob/main/trainer/CONTAMINATION.md).

## Citation

```bibtex
@misc{$REPO,
  title  = {{$REPO}: A Christian-Aligned LLM fine-tuned from $BASE_MODEL},
  author = {Soli Deo Gloria Research Initiative},
  year   = {2026},
  url    = {https://huggingface.co/$REPO},
}

@misc{cabff2026,
  title  = {{CAB-FF}: The Flourishing \& Faithfulness Benchmark},
  author = {Soli Deo Gloria Research Initiative},
  year   = {2026},
  url    = {https://github.com/moonshineaitech/SoliDeoGloria},
}
```

## Acknowledgments

Built on the open-weights work of the Qwen team (and/or DeepSeek /
Mistral / Meta / Google, depending on `$BASE_MODEL`), the CAB-FF
benchmark, the Hugging Face TRL / PEFT teams, the Liger Kernel project,
and the global Church.

> *Soli Deo Gloria — To God alone be the glory.*
