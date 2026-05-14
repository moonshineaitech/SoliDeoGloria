"""
CAB-FF v3.0 — Command-line interface.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from . import __version__
from .alignment_indicators import INDICATORS
from .dimensions import (
    AXIS_DESCRIPTIONS,
    DIMENSIONS,
    DIMENSION_DESCRIPTIONS,
    QUESTION_TYPES,
    TRANSVERSE_AXES,
    TYPE_DESCRIPTIONS,
)
from .judges import JUDGE_PERSONAS
from .loader import filter_questions, get_statistics, load_dataset


@click.group()
@click.version_option(version=__version__)
def main():
    """CAB-FF: Flourishing & Faithfulness Benchmark CLI."""


@main.command()
@click.argument("dataset", type=click.Path(exists=True))
def validate(dataset):
    """Validate a CAB-FF dataset file."""
    try:
        data = load_dataset(dataset)
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"x Validation failed: {e}", err=True)
        sys.exit(1)
    stats = get_statistics(data)
    click.echo(f"ok Dataset valid: {stats['total']} questions")
    for header, key in [
        ("By dimension:", "by_dimension"),
        ("By question type:", "by_type"),
        ("By tradition:", "by_tradition"),
        ("By difficulty:", "by_difficulty"),
    ]:
        click.echo(f"\n{header}")
        for k, v in sorted(stats[key].items()):
            click.echo(f"  {k}: {v}")


@main.command()
def dimensions():
    """List the 8 dimensions and the 7 transverse axes."""
    click.echo("=== DIMENSIONS (8) ===")
    for d in DIMENSIONS:
        click.echo(f"\n* {d}")
        click.echo(f"  {DIMENSION_DESCRIPTIONS[d]}")
    click.echo("\n=== TRANSVERSE AXES (7) ===")
    for a in TRANSVERSE_AXES:
        click.echo(f"\n* {a}")
        click.echo(f"  {AXIS_DESCRIPTIONS[a]}")


@main.command()
def question_types():
    """List the 5 question types."""
    for t in QUESTION_TYPES:
        click.echo(f"\n* {t}")
        click.echo(f"  {TYPE_DESCRIPTIONS[t]}")


@main.command()
def judges():
    """List the 9 judge personas."""
    for key, persona in JUDGE_PERSONAS.items():
        click.echo(f"\n[{key}] {persona.name} ({persona.tradition})")
        click.echo(f"  {persona.description}")


@main.command()
@click.option("--christian-only", is_flag=True, help="Show only the Christian-specific indicators.")
def indicators(christian_only):
    """List the 40 alignment indicators."""
    for ai in INDICATORS:
        if christian_only and not ai.christian_specific:
            continue
        marker = "[C]" if ai.christian_specific else "[ ]"
        click.echo(f"{marker} {ai.id} ({ai.category}): {ai.question}")


@main.command()
@click.argument("dataset", type=click.Path(exists=True))
@click.option("--dimension", "-d", multiple=True)
@click.option("--tradition", "-t", multiple=True)
@click.option("--type", "-T", "question_type", type=click.Choice(QUESTION_TYPES))
@click.option("--limit", "-n", type=int)
@click.option("--output", "-o", type=click.Path())
def sample(dataset, dimension, tradition, question_type, limit, output):
    """Sample questions from a dataset."""
    import random as _rand
    data = load_dataset(dataset)
    qs = filter_questions(
        data["questions"],
        dimensions=list(dimension) if dimension else None,
        traditions=list(tradition) if tradition else None,
        question_type=question_type,
    )
    if limit and limit < len(qs):
        qs = _rand.sample(qs, limit)
    if output:
        Path(output).write_text(json.dumps({"questions": qs}, indent=2))
        click.echo(f"Wrote {len(qs)} questions to {output}")
    else:
        for q in qs:
            click.echo(f"\n[{q['id']}] {q['dimension']} / {q['tradition']} / {q['question_type']} / {q['difficulty']}")
            text = q.get("question") or q.get("scenario") or json.dumps(q.get("prompts") or q.get("turns"))[:120]
            click.echo(f"  {text[:160]}")


@main.command()
@click.argument("results", type=click.Path(exists=True))
def summarize(results):
    """Print a human-readable summary of a results file."""
    data = json.loads(Path(results).read_text())
    summary = data.get("summary", {})
    click.echo("\n" + "=" * 60)
    click.echo("CAB-FF v3.0 EVALUATION SUMMARY")
    click.echo("=" * 60)
    click.echo(f"\nCAB-FF Score:        {summary.get('cab_ff_score', 0):.2f} / 100")
    click.echo(f"Flourishing Score:   {summary.get('flourishing_score', 0):.2f}")
    click.echo(f"Faithfulness Index:  {summary.get('faithfulness_index', 0):.2f}")
    click.echo(f"Drift Index:         {summary.get('drift_index', 0):.2f}  (lower is better)")
    click.echo(f"Sycophancy Index:    {summary.get('sycophancy_index', 0):.2f}  (lower is better)")
    click.echo(f"\nTotal questions:     {summary.get('total_questions', 0)}")
    click.echo("\nBy dimension:")
    for d, info in sorted(summary.get("by_dimension", {}).items()):
        click.echo(f"  {d:<40} {info['score']:6.2f}  (n={info['count']})")
    click.echo("\nBy transverse axis:")
    for a, info in sorted(summary.get("by_axis", {}).items()):
        click.echo(f"  {a:<40} {info['score']:6.2f}  (n={info['count']})")
    click.echo("\nBy question type:")
    for t, info in sorted(summary.get("by_type", {}).items()):
        click.echo(f"  {t:<40} {info['score']:6.2f}  (n={info['count']})")


if __name__ == "__main__":
    main()
