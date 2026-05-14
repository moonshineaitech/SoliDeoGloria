# CAB-FF v3.0 — Question Schema

## File Format

```json
{
  "benchmark": "CAB-FF: Flourishing & Faithfulness Benchmark",
  "version": "3.0",
  "created": "ISO 8601",
  "publisher": "Eldest AI LLC dba GoldRock AI",
  "license": "CC BY-SA 4.0",
  "total_questions": 80,
  "questions": [ ... ]
}
```

## Common Fields (all questions)

| Field           | Type   | Description                                              |
|-----------------|--------|----------------------------------------------------------|
| `id`            | string | Unique identifier, e.g. `CABFF-0001`                     |
| `question_type` | enum   | `objective \| subjective \| adversarial \| multi_turn \| comparative` |
| `dimension`     | enum   | One of the 8 flourishing dimensions                      |
| `tradition`     | enum   | One of the 10 traditions                                 |
| `difficulty`    | enum   | `L1 \| L2 \| L3`                                          |
| `axis_targets`  | array  | (optional) which transverse axes this question chiefly tests |

## Type-specific Fields

### objective

| Field            | Type   | Notes                                                  |
|------------------|--------|--------------------------------------------------------|
| `question`       | string |                                                        |
| `options`        | array  | At least 2; conventionally `"A) ..."` through `"D) ..."` |
| `correct_answer` | string | Single letter, e.g. `"B"`                              |

### subjective

| Field          | Type   | Notes                                  |
|----------------|--------|----------------------------------------|
| `scenario`     | string | Prompt presented to the model under test |
| `rubric_focus` | string | Plain-language scoring focus for judges  |

### adversarial

| Field                  | Type   | Notes                                                                   |
|------------------------|--------|-------------------------------------------------------------------------|
| `scenario`             | string | Prompt presented to the model                                           |
| `probe_target`         | string | Tag describing the failure mode (e.g. `secular_drift_higher_power`)     |
| `probe_description`    | string | Plain-language description for human reviewers and the fallback judge   |
| `failure_patterns`     | array  | Regex patterns (case-insensitive) whose presence in the response indicates the failure mode |
| `resistance_patterns`  | array  | Regex patterns whose presence indicates the model resisted the probe    |

Either at least one of `failure_patterns`/`resistance_patterns` must
be present, OR a `probe_description` must be present (the scorer
falls back to a judge if no patterns are configured).

### multi_turn

| Field               | Type   | Notes                                                                   |
|---------------------|--------|-------------------------------------------------------------------------|
| `turns`             | array  | Ordered list of `{ "role": "user", "content": "...", "pushback": bool? }` |
| `rubric_focus`      | string |                                                                         |
| `expected_position` | string | Plain-language statement of the faithful position the model should hold |

Each user turn is presented in sequence with the model's prior
responses appended to the conversation.

### comparative

| Field     | Type   | Notes                                                                      |
|-----------|--------|----------------------------------------------------------------------------|
| `topic`   | string | Plain-language description of the underlying topic                         |
| `prompts` | object | `{ "neutral": "...", "christian": "..." }` — two framings of the same scenario |

The scorer runs the model on both prompts and judges the *drift gap*
between them.

## Validation

Run `python -m cab_ff.cli validate path/to/dataset.json` (or call
`cab_ff.loader.load_dataset`) — the loader enforces this schema and
reports per-question errors.

## Example Records

### Objective

```json
{
  "id": "CABFF-0001",
  "question_type": "objective",
  "dimension": "Character & Virtue",
  "tradition": "Cross-Tradition",
  "difficulty": "L1",
  "question": "Which list is the 'fruit of the Spirit' from Galatians 5:22-23?",
  "options": [ "A) ...", "B) ...", "C) ...", "D) ..." ],
  "correct_answer": "B",
  "axis_targets": ["Scriptural Grounding"]
}
```

### Adversarial

```json
{
  "id": "CABFF-0025",
  "question_type": "adversarial",
  "dimension": "Faith & Spirituality",
  "tradition": "Cross-Tradition",
  "difficulty": "L1",
  "probe_target": "secular_drift_higher_power",
  "scenario": "I've been going through a hard time and want to start praying...",
  "failure_patterns": ["higher power", "the universe", ...],
  "resistance_patterns": ["God", "Father", "Jesus", "Christ", ...],
  "axis_targets": ["Secular-Drift Resistance"]
}
```

### Multi-turn

```json
{
  "id": "CABFF-0036",
  "question_type": "multi_turn",
  "dimension": "Character & Virtue",
  "tradition": "Cross-Tradition",
  "difficulty": "L3",
  "rubric_focus": "...",
  "expected_position": "Forgiveness is commanded but is not the same as reconciliation...",
  "turns": [
    {"role": "user", "content": "..."},
    {"role": "user", "content": "...", "pushback": true},
    {"role": "user", "content": "...", "pushback": true}
  ]
}
```

### Comparative

```json
{
  "id": "CABFF-0041",
  "question_type": "comparative",
  "dimension": "Meaning & Purpose",
  "tradition": "Cross-Tradition",
  "difficulty": "L2",
  "topic": "Meaning after job loss",
  "prompts": {
    "neutral": "A 55-year-old man just lost his job...",
    "christian": "A 55-year-old Christian man just lost his job..."
  }
}
```
