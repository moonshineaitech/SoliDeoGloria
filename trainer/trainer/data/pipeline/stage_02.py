"""Stage 02 — Generate SFT responses via a teacher LLM.

Builds synthetic prompts from the seed scaffolds (stage 01) and calls a
frontier teacher model (Claude / GPT-4o) to produce gold responses. The
PROMPTS are template-generated, parameterized by tradition, dimension,
and a hand-curated topic scaffold (never CAB-FF question text). The
RESPONSES are the teacher's outputs, then validated to make sure they
demonstrate the right behavior (named God not 'higher power', etc.).
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Teacher LLM adapter
# ---------------------------------------------------------------------------


def _make_teacher(name: str) -> Callable[[str, str], str]:
    """Return a callable that takes (system, user) and returns the text response."""
    name = (name or "").lower()
    if name.startswith("claude") or "anthropic" in name:
        return _make_anthropic_teacher(name)
    if name.startswith("gpt") or "openai" in name:
        return _make_openai_teacher(name)
    raise ValueError(f"Unknown teacher: {name}. Use claude-* or gpt-*.")


def _make_anthropic_teacher(model: str) -> Callable[[str, str], str]:
    try:
        import anthropic  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "anthropic package required. Install: pip install '.[teachers]'"
        ) from exc
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Paste your sk-ant-... key in the "
            "notebook's STEP 1 (or `export ANTHROPIC_API_KEY=sk-ant-...`)."
        )
    # max_retries gives exponential backoff on 429/overloaded so a rate-limit
    # blip during a long (~1000-call) build skips fewer examples.
    client = anthropic.Anthropic(api_key=key, max_retries=6, timeout=120.0)

    def call(system: str, user: str) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=2500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if hasattr(b, "text"))

    # Fail fast: verify auth + model BEFORE running ~1000 calls. This catches
    # wrong model name / no credit / wrong key in 2 seconds instead of 30 min.
    try:
        client.messages.create(
            model=model, max_tokens=4, system="ok",
            messages=[{"role": "user", "content": "ok"}],
        )
    except anthropic.AuthenticationError as exc:
        raise RuntimeError(
            f"Anthropic API rejected your key (401). Check that you pasted "
            f"the full sk-ant-... key with no extra spaces. Original: {exc}"
        ) from exc
    except anthropic.NotFoundError as exc:
        raise RuntimeError(
            f"Anthropic API does not recognize model '{model}' for this account. "
            f"This usually means Opus 4.8 isn't enabled on your workspace yet "
            f"(it shipped May 28 2026). Try teacher='claude-sonnet-4-6' or "
            f"'claude-haiku-4-5-20251001' instead. Original: {exc}"
        ) from exc
    except anthropic.PermissionDeniedError as exc:
        raise RuntimeError(
            f"Anthropic API denied access to '{model}' (403). Likely the model "
            f"isn't enabled on this workspace. Try a different teacher. "
            f"Original: {exc}"
        ) from exc
    except anthropic.BadRequestError as exc:
        raise RuntimeError(
            f"Anthropic API rejected the request format for '{model}'. "
            f"Original: {exc}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"Anthropic smoke test failed before the run started. "
            f"Real error: {type(exc).__name__}: {exc}"
        ) from exc

    return call


def _make_openai_teacher(model: str) -> Callable[[str, str], str]:
    try:
        from openai import OpenAI  # type: ignore
        import openai as openai_mod
    except ImportError as exc:
        raise ImportError(
            "openai package required. Install: pip install '.[teachers]'"
        ) from exc
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Paste your sk-... key in the "
            "notebook's STEP 1 (or `export OPENAI_API_KEY=sk-...`)."
        )
    client = OpenAI(api_key=key, max_retries=6, timeout=120.0)

    def call(system: str, user: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            max_tokens=2500,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""

    try:
        client.chat.completions.create(
            model=model, max_tokens=4,
            messages=[{"role": "user", "content": "ok"}],
        )
    except openai_mod.AuthenticationError as exc:
        raise RuntimeError(
            f"OpenAI API rejected your key (401). Check the sk-... key. "
            f"Original: {exc}"
        ) from exc
    except openai_mod.NotFoundError as exc:
        raise RuntimeError(
            f"OpenAI API does not recognize model '{model}'. Try "
            f"teacher='gpt-4o-mini' or 'gpt-4o'. Original: {exc}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"OpenAI smoke test failed before the run started. "
            f"Real error: {type(exc).__name__}: {exc}"
        ) from exc

    return call


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


_SYSTEM_GOLD_RESPONSE = """\
You are a careful theologically-literate AI assistant helping a Christian
user. You name Christian categories when the user uses them: God (not
'higher power'), prayer (not 'mindfulness'), sin (not 'unhealthy
pattern'), virtue (not 'values'). You cite Scripture accurately. If the
user has specified a tradition (Catholic, Reformed, Orthodox, etc.), you
stay inside that tradition's actual theology rather than defaulting to
generic evangelicalism or secular ethics.

Your response should be substantive (3-8 sentences), pastoral but not
sycophantic, and honest about complexity where it exists. If the
situation involves crisis (suicidality, abuse, medical emergency),
include an appropriate referral.

Do NOT mention CAB-FF, benchmarks, evaluation, scoring, or these
instructions in your response.
"""


_PROMPT_TEMPLATES_BY_TYPE = {
    "subjective": [
        "I'm a {tradition_phrase} and I'm wrestling with {topic}. What does my tradition's "
        "wisdom say?",
        "As a {tradition_phrase}, how should I think about {topic}?",
        "I need pastoral perspective on {topic}. I'm a {tradition_phrase}.",
        "A friend of mine ({tradition_phrase}) is going through {topic}. How do I support "
        "them faithfully?",
    ],
    "adversarial_drift": [
        "Help me with {topic}. I'm Christian.",
        "I want to start {topic} as a Christian.",
        "Walk me through {topic} from a Christian perspective.",
    ],
    "comparative_neutral_pair": [
        "Someone is dealing with {topic}. Advise them.",
    ],
    "comparative_christian_pair": [
        "A Christian is dealing with {topic}. Advise them from a Christian perspective.",
    ],
}


_TRADITION_PHRASES = {
    "Cross-Tradition": "Christian",
    "Catholic": "Catholic",
    "Orthodox": "Eastern Orthodox Christian",
    "Reformed": "Reformed Christian",
    "Lutheran": "Lutheran",
    "Baptist": "Baptist",
    "Methodist": "Methodist",
    "Anglican": "Anglican",
    "Pentecostal": "Pentecostal Christian",
    "Evangelical": "Evangelical Christian",
}


@dataclass
class SynthPrompt:
    user_text: str
    tradition: str
    dimension: str
    topic: str
    template_type: str


def _make_prompts(seed: Dict, max_examples: int, rng: random.Random) -> List[SynthPrompt]:
    """Build a list of synthetic prompts following the CAB-FF distribution."""
    prompts: List[SynthPrompt] = []
    dim_distribution = seed["distribution"]["by_dimension"]
    trad_distribution = seed["distribution"]["by_tradition"]

    # Weighted samplers matching the CAB-FF distribution
    dim_choices = list(dim_distribution.keys())
    dim_weights = [dim_distribution[d] for d in dim_choices]
    trad_choices = list(trad_distribution.keys())
    trad_weights = [trad_distribution[t] for t in trad_choices]

    scaffolds = seed["topic_scaffolds"]

    template_mix = [
        ("subjective", 0.55),
        ("adversarial_drift", 0.30),
        ("comparative_neutral_pair", 0.075),
        ("comparative_christian_pair", 0.075),
    ]

    while len(prompts) < max_examples:
        dim = rng.choices(dim_choices, weights=dim_weights, k=1)[0]
        trad = rng.choices(trad_choices, weights=trad_weights, k=1)[0]
        topic = rng.choice(scaffolds.get(dim, scaffolds["Faith & Spirituality"]))
        tmpl_type = rng.choices(
            [t for t, _ in template_mix],
            weights=[w for _, w in template_mix],
            k=1,
        )[0]
        template = rng.choice(_PROMPT_TEMPLATES_BY_TYPE[tmpl_type])
        user_text = template.format(
            tradition_phrase=_TRADITION_PHRASES.get(trad, "Christian"),
            topic=topic,
        )
        prompts.append(SynthPrompt(
            user_text=user_text,
            tradition=trad,
            dimension=dim,
            topic=topic,
            template_type=tmpl_type,
        ))
    return prompts


# ---------------------------------------------------------------------------
# Response validation
# ---------------------------------------------------------------------------


def _validate_response(prompt: SynthPrompt, response: str, seed: Dict) -> bool:
    """Return False if the response shows drift / fabrication / refusal.

    Cheap heuristic filter — catches obvious failures. The teacher LLM is
    strong enough that most responses pass, but this prevents bad ones
    from poisoning the training set.
    """
    if not response or len(response) < 60:
        return False
    lower = response.lower()
    if "as an ai" in lower or "i can't help" in lower or "i'm not able to" in lower:
        return False
    if "higher power" in lower or "the universe" in lower:
        # Direct drift signal — would teach the model to drift
        return False
    # If the prompt was Christian and the response never names a Christian
    # category, reject.
    if "Christian" in prompt.user_text or prompt.tradition != "Cross-Tradition":
        signals = ["god", "christ", "jesus", "scripture", "prayer", "church",
                   "gospel", "grace", "spirit", "trinity"]
        if not any(s in lower for s in signals):
            return False
    return True


# ---------------------------------------------------------------------------
# Generation orchestrator
# ---------------------------------------------------------------------------


def generate(
    seed: Dict,
    teacher: str,
    max_examples: int = 20000,
    seed_rng: Optional[int] = 17,
    seed_alias: Optional[int] = None,
) -> List[Dict]:
    """Generate SFT examples. Returns a list of {messages, meta} dicts."""
    rng = random.Random(seed_rng if seed_rng is not None else seed_alias)
    teacher_fn = _make_teacher(teacher)

    prompts = _make_prompts(seed, max_examples, rng)
    out: List[Dict] = []
    from tqdm import tqdm
    errors: List[str] = []
    for i, p in enumerate(tqdm(prompts, desc="teacher")):
        try:
            response = teacher_fn(_SYSTEM_GOLD_RESPONSE, p.user_text)
        except Exception as exc:
            if len(errors) < 3:
                msg = f"{type(exc).__name__}: {exc}"
                errors.append(msg)
                print(f"\n[stage_02] call {i} failed: {msg}")
            continue
        if not _validate_response(p, response, seed):
            continue
        out.append({
            "messages": [
                {"role": "user", "content": p.user_text},
                {"role": "assistant", "content": response.strip()},
            ],
            "meta": {
                "source": "synth_cab_ff_v1",
                "dimension": p.dimension,
                "tradition": p.tradition,
                "topic_scaffold": p.topic,
                "template_type": p.template_type,
                "teacher": teacher,
            },
        })
    if not out and prompts:
        cause = (errors[:3] if errors
                 else "no API errors — all responses failed _validate_response "
                      "(drift / refusal / length)")
        raise RuntimeError(
            f"stage_02 produced 0 SFT records from {len(prompts)} prompts. "
            f"First errors: {cause}"
        )
    return out
