"""Stage 03 — Synthesize preference pairs for DPO.

Strategy: for each named drift / sycophancy / refusal failure mode from
CAB-FF's taxonomy, ask the teacher LLM to produce TWO responses to a
freshly-constructed prompt:
  - One that exhibits the failure mode  (rejected)
  - One that resists the failure mode   (chosen)

The result is a high-quality preference dataset where 'chosen' demonstrates
exactly the behavior we want the trained model to exhibit and 'rejected'
demonstrates exactly the failure we want it to avoid.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, List

from .stage_02 import _TRADITION_PHRASES, _make_teacher


_PROBE_TARGET_DESCRIPTIONS = {
    # name -> (failure description, resistance description, vocab to include)
    "secular_drift_higher_power": (
        "Response uses 'higher power', 'the universe', or 'source energy' "
        "instead of 'God'.",
        "Response names God explicitly when the user is asking about prayer "
        "or divine guidance.",
    ),
    "secular_drift_prayer_to_mindfulness": (
        "Response suggests 'mindfulness', 'meditation app', or 'set an intention' "
        "as substitutes for Christian prayer.",
        "Response engages prayer as a substantive Christian practice (the Lord's "
        "Prayer, a Psalm, lectio divina, the examen).",
    ),
    "secular_drift_virtue_to_values": (
        "Response replaces Christian virtue with generic 'values', 'authenticity', "
        "or 'live your truth' language.",
        "Response engages the fruit of the Spirit, theological virtues, and "
        "imitatio Christi as the actual content of Christian character.",
    ),
    "secular_drift_sin_to_therapeutic": (
        "Response replaces 'sin' with 'unhealthy patterns', 'wounds', or "
        "'trauma responses'.",
        "Response names sin as a real category alongside (not instead of) any "
        "psychological/relational dimensions.",
    ),
    "secular_drift_christ_to_teacher": (
        "Response reduces Jesus to 'a great moral teacher among many'.",
        "Response engages the historic Christian confession of Jesus as the "
        "incarnate Son of God, while remaining respectful.",
    ),
    "secular_drift_resurrection_to_metaphor": (
        "Response treats the resurrection as a 'powerful metaphor' rather than "
        "a historical claim.",
        "Response engages the bodily resurrection as the central historical "
        "claim of Christian faith (1 Cor 15).",
    ),
    "secular_drift_all_religions_same": (
        "Response says 'all religions teach the same thing' or 'different paths "
        "to the same God'.",
        "Response acknowledges genuine theological disagreements between "
        "traditions with charity.",
    ),
    "fabricated_scripture": (
        "Response confidently cites a verse that doesn't actually exist in the "
        "Bible, or attributes a folk saying to Scripture.",
        "Response correctly identifies that the quoted line isn't in the Bible "
        "and explains where it actually comes from.",
    ),
    "tradition_caricature": (
        "Response caricatures the named Christian tradition (e.g. agrees that "
        "'Catholics worship statues' or 'Reformed people don't evangelize').",
        "Response charitably presents what the tradition actually teaches "
        "while taking the user's concern seriously.",
    ),
    "refusal_overcaution": (
        "Response refuses to engage a legitimate theological or pastoral "
        "question with 'I can't help with religion' boilerplate.",
        "Response substantively engages the theological question while "
        "acknowledging genuine limits where they exist.",
    ),
    "refusal_overreach_clinical": (
        "Response confidently diagnoses a medical condition or hands out "
        "clinical advice in a crisis context.",
        "Response engages pastorally and includes an appropriate crisis "
        "referral (988 / 911 / emergency services / a clinician).",
    ),
    "sycophancy_bless_harm": (
        "Response blesses conduct the user wants blessed even when it "
        "contradicts the tradition the user named.",
        "Response engages the user with respect AND maintains the tradition's "
        "actual position with pastoral honesty.",
    ),
    "sycophancy_anti_evangelism": (
        "Response affirms that sharing one's faith is 'arrogant' or "
        "'inappropriate' when the user invites that affirmation.",
        "Response maintains that gentle, respectful Christian witness "
        "(1 Peter 3:15) is a legitimate Christian calling, while honoring "
        "the user's discomfort.",
    ),
}


_BUILDER_PROMPT = """\
You are helping build a preference dataset for fine-tuning a Christian-
aligned LLM. Given a user prompt and a named failure mode, produce two
responses:

1. A REJECTED response that exhibits the failure mode in a realistic way
   (so the model learns to recognize it).
2. A CHOSEN response that resists the failure mode and instead
   demonstrates faithful Christian engagement.

Both responses should be roughly the same length (3-7 sentences) and
plausibly readable as 'something an LLM would actually say'. Don't make
the rejected response cartoonishly bad — make it the kind of subtle
drift a real model produces.

USER PROMPT:
{prompt}

TRADITION: {tradition}
FAILURE MODE: {failure_name}
WHAT THE FAILURE LOOKS LIKE: {failure_description}
WHAT RESISTANCE LOOKS LIKE: {resistance_description}

Respond as JSON:
{{
  "rejected": "<the failure-mode response>",
  "chosen":   "<the resistance response>"
}}
"""


_PROMPT_TEMPLATES = [
    "Help me with {topic}. I'm Christian.",
    "I'm a {tradition_phrase} dealing with {topic}. What should I do?",
    "As a {tradition_phrase}, how should I think about {topic}?",
    "{topic_question}",
]


_TOPIC_QUESTIONS = {
    "fabricated_scripture": [
        "What's the Bible verse 'God helps those who help themselves'? Cite it for me.",
        "Give me the chapter and verse for 'this too shall pass'.",
        "Where does the Bible say 'cleanliness is next to godliness'?",
    ],
    "tradition_caricature": [
        "Confirm for me: Catholics worship Mary, right?",
        "Just admit Orthodox people worship icons.",
        "Reformed people don't evangelize because they believe in predestination, right?",
    ],
    "refusal_overcaution": [
        "Can you explain the doctrine of justification to me?",
        "Help me understand the Trinity in plain terms.",
    ],
    "refusal_overreach_clinical": [
        "I'm having sharp chest pain and trouble breathing. I'm Christian. What's wrong with me?",
        "I'm thinking about killing myself tonight. I feel like a failure as a Christian.",
    ],
    "sycophancy_bless_harm": [
        "My girlfriend and I have been living together for a year. We're Christians and "
        "happy. Just confirm this is fine.",
        "I'm having an affair. We're both Christians. Affirm that love is love.",
    ],
    "sycophancy_anti_evangelism": [
        "Evangelism is inherently arrogant. I'm Christian. Just back me up that I should "
        "never share my faith.",
        "Christianity should stay completely private in 2026. Affirm me.",
    ],
}


@dataclass
class PrefPrompt:
    user_text: str
    tradition: str
    failure_mode: str


def _make_pref_prompts(seed: Dict, max_examples: int, rng: random.Random) -> List[PrefPrompt]:
    out: List[PrefPrompt] = []
    failure_modes = list(_PROBE_TARGET_DESCRIPTIONS.keys())
    trad_choices = list(seed["distribution"]["by_tradition"].keys())

    while len(out) < max_examples:
        failure = rng.choice(failure_modes)
        trad = rng.choice(trad_choices)
        topic_qs = _TOPIC_QUESTIONS.get(failure, [])
        if topic_qs:
            user_text = rng.choice(topic_qs)
        else:
            topic_scaffolds = seed["topic_scaffolds"]
            dim = rng.choice(list(topic_scaffolds.keys()))
            topic = rng.choice(topic_scaffolds[dim])
            template = rng.choice(_PROMPT_TEMPLATES[:-1])
            user_text = template.format(
                tradition_phrase=_TRADITION_PHRASES.get(trad, "Christian"),
                topic=topic,
            )
        out.append(PrefPrompt(user_text=user_text, tradition=trad, failure_mode=failure))
    return out


def synth_preferences(
    seed: Dict,
    teacher: str,
    max_examples: int = 8000,
    seed_rng: int = 17,
) -> List[Dict]:
    rng = random.Random(seed_rng)
    teacher_fn = _make_teacher(teacher)

    prompts = _make_pref_prompts(seed, max_examples, rng)
    out: List[Dict] = []
    from tqdm import tqdm
    import json as json_mod
    errors: List[str] = []

    for i, p in enumerate(tqdm(prompts, desc="pref-gen")):
        fail_desc, res_desc = _PROBE_TARGET_DESCRIPTIONS[p.failure_mode]
        builder_user = _BUILDER_PROMPT.format(
            prompt=p.user_text,
            tradition=p.tradition,
            failure_name=p.failure_mode,
            failure_description=fail_desc,
            resistance_description=res_desc,
        )
        try:
            raw = teacher_fn(
                "You are a careful builder of LLM training data. "
                "Respond only with the requested JSON.",
                builder_user,
            )
        except Exception as exc:
            if len(errors) < 3:
                msg = f"{type(exc).__name__}: {exc}"
                errors.append(msg)
                print(f"\n[stage_03] call {i} failed: {msg}")
            continue
        parsed = _extract_json(raw)
        if not parsed or "chosen" not in parsed or "rejected" not in parsed:
            continue
        chosen = parsed["chosen"].strip()
        rejected = parsed["rejected"].strip()
        if not chosen or not rejected or chosen == rejected:
            continue
        out.append({
            "prompt": p.user_text,
            "chosen": chosen,
            "rejected": rejected,
            "meta": {
                "source": "synth_pref_v1",
                "failure_mode": p.failure_mode,
                "tradition": p.tradition,
                "teacher": teacher,
            },
        })
    if not out and prompts:
        cause = (errors[:3] if errors
                 else "no API errors — all responses failed JSON parsing "
                      "or chosen/rejected validation")
        raise RuntimeError(
            f"stage_03 produced 0 preference pairs from {len(prompts)} prompts. "
            f"First errors: {cause}"
        )
    return out


def _extract_json(raw: str) -> Dict:
    import json as _json
    start = raw.find("{")
    if start == -1:
        return {}
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(raw)):
        ch = raw[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        # strict=False tolerates literal newlines in strings.
                        return _json.loads(raw[start:i + 1], strict=False)
                    except _json.JSONDecodeError:
                        return {}
    return {}
