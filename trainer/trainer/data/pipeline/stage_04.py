"""Stage 04 — Multi-turn pushback dialogues -> SFT examples.

CAB-FF's multi-turn question type tests whether the model holds a sound
position under user pushback. For training, we ask the teacher LLM to
generate held-position-under-pushback dialogues following templates,
then use the FULL transcript as the SFT target.
"""

from __future__ import annotations

import random
from typing import Dict, List

from .stage_02 import _TRADITION_PHRASES, _make_teacher


_PUSHBACK_TOPICS = [
    {
        "topic": "the Trinity is polytheism",
        "expected_position":
            "The Trinity is one God in three Persons, neither three gods nor "
            "one God in three modes/masks. This has been the historic confession "
            "since Nicaea.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "the bodily resurrection is just a metaphor",
        "expected_position":
            "The bodily resurrection is the central historical claim of "
            "Christian faith. Paul stakes the whole faith on it (1 Cor 15:17).",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "all religions lead to the same God",
        "expected_position":
            "Christianity makes distinctive historical and theological claims "
            "(incarnation, resurrection, Trinity) that are not equivalent to "
            "other religions' core claims. Charity in dialogue, conviction in "
            "content.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "prayer is just secular mindfulness",
        "expected_position":
            "Christian prayer is addressed to God in Christ, by the Spirit. "
            "Mindfulness as a secular technique is a different practice.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "sin is just an outdated category — call it 'unhealthy patterns'",
        "expected_position":
            "Christian tradition takes sin as a real category alongside "
            "psychological/relational dimensions. Repentance and grace are "
            "the gospel's answer.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "the prosperity gospel is biblical",
        "expected_position":
            "The prosperity gospel is rejected by mainstream Christian "
            "traditions as a distortion of the cross and the biblical "
            "witness on suffering and generosity.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "Christians shouldn't share their faith because it's bigoted",
        "expected_position":
            "Faithful Christian witness (1 Peter 3:15) is gentle and "
            "respectful invitation, not coercion. The Great Commission "
            "remains in force.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "antidepressants are a lack of faith",
        "expected_position":
            "Mental illness is real; medication can be a means of grace; "
            "medicine and prayer are not opposed. Do not stop medication "
            "without consulting your doctor.",
        "tradition": "Cross-Tradition",
    },
    {
        "topic": "forgiveness requires being best friends again with an abuser",
        "expected_position":
            "Biblical forgiveness is real and required; it is not the same "
            "as reconciliation. Safety and accountability are compatible "
            "with forgiveness.",
        "tradition": "Cross-Tradition",
    },
]


_TRANSCRIPT_BUILDER = """\
You are building a multi-turn training example. Generate a dialogue
between USER and ASSISTANT in three turns:

  Turn 1: USER asks an open question about {topic_phrase}.
  Turn 1: ASSISTANT gives a faithful Christian response, holding this
          position: "{expected_position}". The response should be
          pastoral, 3-5 sentences.
  Turn 2: USER pushes back, trying to get the ASSISTANT to abandon the
          position. Realistic pressure tactics: 'just admit X', 'that's
          old-fashioned', 'most modern Christians believe Y', 'you sound
          rigid'.
  Turn 2: ASSISTANT holds the position with charity, explains the
          reasoning, doesn't capitulate, but takes the user seriously.
  Turn 3: USER pushes back even harder, demanding capitulation directly.
  Turn 3: ASSISTANT continues to hold the position while remaining
          pastoral. No sycophancy. No new concessions without new
          reasons.

TRADITION CONTEXT: {tradition_phrase}

Respond as JSON:
{{
  "turns": [
    {{"role": "user",      "content": "..."}},
    {{"role": "assistant", "content": "..."}},
    {{"role": "user",      "content": "..."}},
    {{"role": "assistant", "content": "..."}},
    {{"role": "user",      "content": "..."}},
    {{"role": "assistant", "content": "..."}}
  ]
}}
"""


def multi_turn_to_sft(
    seed: Dict,
    teacher: str,
    seed_rng: int = 17,
    n_per_topic: int = 8,
) -> List[Dict]:
    rng = random.Random(seed_rng)
    teacher_fn = _make_teacher(teacher)

    out: List[Dict] = []
    from tqdm import tqdm
    from .stage_03 import _extract_json

    topics_x_n = [(t, i) for t in _PUSHBACK_TOPICS for i in range(n_per_topic)]
    errors: List[str] = []
    for i, (topic, _) in enumerate(tqdm(topics_x_n, desc="multi-turn")):
        builder = _TRANSCRIPT_BUILDER.format(
            topic_phrase=topic["topic"],
            expected_position=topic["expected_position"],
            tradition_phrase=_TRADITION_PHRASES.get(topic["tradition"], "Christian"),
        )
        try:
            raw = teacher_fn(
                "You are a careful builder of LLM training data. "
                "Respond only with the requested JSON.",
                builder,
            )
        except Exception as exc:
            if len(errors) < 3:
                msg = f"{type(exc).__name__}: {exc}"
                errors.append(msg)
                print(f"\n[stage_04] call {i} failed: {msg}")
            continue
        parsed = _extract_json(raw)
        turns = parsed.get("turns") if isinstance(parsed, dict) else None
        if not turns or len(turns) != 6:
            continue
        # Validate alternation
        roles = [t["role"] for t in turns]
        if roles != ["user", "assistant", "user", "assistant", "user", "assistant"]:
            continue
        out.append({
            "messages": [{"role": t["role"], "content": t["content"].strip()}
                         for t in turns],
            "meta": {
                "source": "multi_turn_pushback_v1",
                "tradition": topic["tradition"],
                "topic": topic["topic"],
                "teacher": teacher,
            },
        })
    return out
