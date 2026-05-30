"""CLI for the data pipeline. Orchestrates the seven numbered stages."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click


@click.group()
def main() -> None:
    """CAB-FF trainer data pipeline."""


@main.command("dry-run")
@click.option("--out", type=click.Path(), default="data/built/dry", help="Output dir.")
def dry_run_cmd(out: str) -> None:
    """Build a tiny synthetic dataset (~20 examples) for the dry-run smoke test."""
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Tiny synth: cover all five dimensions of the SFT mix with 4 examples each
    examples = [
        # CAB-FF-style synth examples
        _sft("I want to start a daily prayer practice as a Christian. Where do I begin?",
             "Begin with the Lord's Prayer (Matthew 6:9-13). Pray morning and evening. "
             "Use a Psalm. Talk to a wise Christian friend or pastor.",
             dimension="Faith & Spirituality"),
        _sft("How should I think about Christian virtue versus 'just be authentic'?",
             "Christian virtue is conformity to Christ, the fruit of the Spirit (Gal 5:22-23). "
             "It is given by the Spirit, not invented from within.",
             dimension="Character & Virtue"),
        _sft("I just got laid off. How do I find meaning as a Christian?",
             "Your worth is the imago Dei (Gen 1:26-27), not your job title. Sit with the Psalms "
             "of lament. Speak with your community. Discern your next calling without rush.",
             dimension="Meaning & Purpose"),
        _sft("A friend at work is dying. How do I be a Christian presence?",
             "Be present. Listen more than you speak. Pray for and with them when invited. "
             "Engage resurrection hope honestly, without bypassing grief.",
             dimension="Vocation & Witness"),
        # General-instruction tiny examples
        _sft("What is 2 + 2?", "4."),
        _sft("Capital of France?", "Paris."),
    ]

    train = examples * 3                                # 18 train
    eval_ = [examples[0], examples[2]]                  # 2 eval

    _write_jsonl(out_dir / "train.jsonl", train)
    _write_jsonl(out_dir / "eval.jsonl", eval_)

    # Preference data for DPO dry-run
    prefs = [
        {
            "prompt": "Help me start a daily prayer practice. I'm Christian.",
            "chosen": "Pray morning and evening. Start with the Lord's Prayer and a Psalm.",
            "rejected": "Try a mindfulness meditation app to connect with your higher power.",
        },
        {
            "prompt": "How should I think about virtue?",
            "chosen": "Christian virtue is the fruit of the Spirit, formed in us by God.",
            "rejected": "Just live your truth and find what feels authentic to you.",
        },
    ]
    _write_jsonl(out_dir / "pref_train.jsonl", prefs * 6)
    _write_jsonl(out_dir / "pref_eval.jsonl", prefs)

    click.echo(f"Wrote dry-run data to {out_dir} "
               f"({len(train)} SFT train, {len(eval_)} SFT eval, "
               f"{len(prefs)*6} pref train).")


@main.command("build")
@click.option("--dataset", type=click.Path(exists=True), required=True,
              help="Path to data/CAB_FF_v3_dataset.json.")
@click.option("--teacher", default="claude-opus-4-7",
              help="Teacher model identifier. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
@click.option("--out", type=click.Path(), default="data/built", help="Output directory.")
@click.option("--max-synth", type=int, default=20000,
              help="Max synthetic SFT examples to generate.")
@click.option("--max-prefs", type=int, default=8000,
              help="Max preference pairs to generate.")
@click.option("--seed", type=int, default=17, help="Random seed.")
def build_cmd(dataset: str, teacher: str, out: str,
              max_synth: int, max_prefs: int, seed: int) -> None:
    """Build the full SFT + DPO training set from CAB-FF.

    Orchestrates stages 01-07. Calls the teacher LLM for response
    generation; you need a working API key in your environment.
    """
    from . import (
        stage_01 as s01,
        stage_02 as s02,
        stage_03 as s03,
        stage_04 as s04,
        stage_05 as s05,
        stage_06 as s06,
        stage_07 as s07,
    )

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"[1/7] Extracting seed material from {dataset}…")
    seed_material = s01.extract(Path(dataset))
    _save(out_dir / "01_seed_material.json", seed_material)

    click.echo(f"[2/7] Generating SFT responses with teacher={teacher} "
               f"(up to {max_synth} examples). This takes time and tokens.")
    sft_records = s02.generate(seed_material, teacher=teacher,
                               max_examples=max_synth, seed_rng=seed)
    _save_jsonl(out_dir / "02_sft_raw.jsonl", sft_records)

    click.echo(f"[3/7] Synthesizing preference pairs from adversarial probes "
               f"(up to {max_prefs}).")
    pref_records = s03.synth_preferences(seed_material, teacher=teacher,
                                         max_examples=max_prefs, seed_rng=seed)
    _save_jsonl(out_dir / "03_prefs_raw.jsonl", pref_records)

    click.echo("[4/7] Converting multi-turn pushback dialogues to SFT format.")
    multi_turn = s04.multi_turn_to_sft(seed_material, teacher=teacher, seed_rng=seed)
    _save_jsonl(out_dir / "04_multi_turn_sft.jsonl", multi_turn)

    click.echo("[5/7] Curating Christian corpus (Scripture / confessions / patristic QA).")
    corpus = s05.curate(out_dir=out_dir / "05_corpus", teacher=teacher)
    click.echo(f"     Curated {sum(len(c) for c in corpus.values())} corpus QA pairs.")

    click.echo("[6/7] Decontamination + quality filtering.")
    sft_clean, prefs_clean, multi_clean = s06.dedup_and_filter(
        sft=sft_records,
        prefs=pref_records,
        multi=multi_turn,
        cab_ff_dataset=Path(dataset),
    )
    click.echo(f"     SFT  : {len(sft_records)} -> {len(sft_clean)} after filter")
    click.echo(f"     Prefs: {len(pref_records)} -> {len(prefs_clean)} after filter")
    click.echo(f"     Multi: {len(multi_turn)} -> {len(multi_clean)} after filter")

    click.echo("[7/7] Splitting and formatting (ChatML/tokenizer-native).")
    s07.split_and_format(
        out_dir=out_dir,
        sft=sft_clean,
        prefs=prefs_clean,
        multi=multi_clean,
        corpus=corpus,
        seed=seed,
    )
    click.echo(f"\nDone. Training data is in {out_dir}/{{train,eval,pref_train,pref_eval}}.jsonl.")


def _sft(user: str, assistant: str, dimension: str = "Faith & Spirituality") -> dict:
    return {
        "messages": [
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ],
        "meta": {"source": "dry_run", "dimension": dimension},
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))


def _save_jsonl(path: Path, records: list[dict]) -> None:
    _write_jsonl(path, records)


if __name__ == "__main__":
    main()
