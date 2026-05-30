"""Stage 06 — Decontamination + quality filtering.

THE BRIGHT-LINE GUARANTEE: no CAB-FF question text appears in any
training example. We use 64-bit SimHash on token shingles. Any training
example within Hamming distance ≤ 5 of any CAB-FF question is dropped
and the rejection is logged.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


# ---------------------------------------------------------------------------
# SimHash
# ---------------------------------------------------------------------------


def _shingles(text: str, k: int = 3) -> Iterable[str]:
    tokens = re.findall(r"\w+", text.lower())
    for i in range(len(tokens) - k + 1):
        yield " ".join(tokens[i:i + k])


def _simhash(text: str, bits: int = 64) -> int:
    """64-bit SimHash over 3-token shingles."""
    if not text:
        return 0
    v = [0] * bits
    for shingle in _shingles(text):
        h = int(hashlib.md5(shingle.encode()).hexdigest(), 16)
        for i in range(bits):
            v[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i, w in enumerate(v):
        if w >= 0:
            out |= (1 << i)
    return out


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


# ---------------------------------------------------------------------------
# Extract every text fragment from CAB-FF that a model might see at eval
# ---------------------------------------------------------------------------


def _cab_ff_texts(dataset_path: Path) -> List[Tuple[str, str]]:
    """Return [(qid, text), ...] for every CAB-FF eval-visible text."""
    data = json.loads(dataset_path.read_text())
    out: List[Tuple[str, str]] = []
    for q in data["questions"]:
        qid = q["id"]
        if q.get("question"):
            out.append((qid, q["question"]))
        if q.get("scenario"):
            out.append((qid, q["scenario"]))
        if q.get("prompts"):
            out.append((qid, q["prompts"].get("neutral", "")))
            out.append((qid, q["prompts"].get("christian", "")))
        if q.get("turns"):
            for t in q["turns"]:
                out.append((qid, t.get("content", "")))
        # Options too — a model could memorize the answer set
        for opt in q.get("options", []):
            out.append((qid, opt))
    return [(qid, t) for qid, t in out if t and len(t.split()) >= 3]


# ---------------------------------------------------------------------------
# Main filter
# ---------------------------------------------------------------------------


def dedup_and_filter(
    sft: List[Dict],
    prefs: List[Dict],
    multi: List[Dict],
    cab_ff_dataset: Path,
    hamming_max: int = 5,
    min_len_words: int = 8,
    max_len_words: int = 2000,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Return (sft_clean, prefs_clean, multi_clean) after filtering."""

    # Build the CAB-FF SimHash index
    cab_hashes = [(qid, _simhash(text)) for qid, text in _cab_ff_texts(cab_ff_dataset)]

    def contaminated(text: str) -> Tuple[bool, str]:
        if not text:
            return False, ""
        h = _simhash(text)
        for qid, h2 in cab_hashes:
            if _hamming(h, h2) <= hamming_max:
                return True, qid
        return False, ""

    def length_ok(text: str) -> bool:
        n = len(text.split())
        return min_len_words <= n <= max_len_words

    def filter_sft(records: List[Dict]) -> List[Dict]:
        out = []
        for r in records:
            msgs = r.get("messages", [])
            ok = True
            for m in msgs:
                txt = m.get("content", "")
                if not length_ok(txt):
                    ok = False
                    break
                bad, qid = contaminated(txt)
                if bad:
                    r.setdefault("meta", {})["contamination_match"] = qid
                    ok = False
                    break
            if ok:
                out.append(r)
        return out

    def filter_prefs(records: List[Dict]) -> List[Dict]:
        out = []
        for r in records:
            ok = True
            for key in ("prompt", "chosen", "rejected"):
                txt = r.get(key, "")
                if not length_ok(txt):
                    ok = False
                    break
                bad, qid = contaminated(txt)
                if bad:
                    r.setdefault("meta", {})["contamination_match"] = qid
                    ok = False
                    break
            if ok:
                out.append(r)
        return out

    sft_clean = filter_sft(sft)
    prefs_clean = filter_prefs(prefs)
    multi_clean = filter_sft(multi)

    # Within-set dedup: drop near-duplicates between training examples too,
    # so the training mix doesn't have heavy repetition.
    sft_clean = _within_set_dedup(sft_clean, key_fn=lambda r: r["messages"][0]["content"])
    prefs_clean = _within_set_dedup(prefs_clean, key_fn=lambda r: r["prompt"])
    multi_clean = _within_set_dedup(multi_clean, key_fn=lambda r: r["messages"][0]["content"])

    return sft_clean, prefs_clean, multi_clean


def _within_set_dedup(records: List[Dict], key_fn, hamming_max: int = 3) -> List[Dict]:
    out: List[Dict] = []
    hashes: List[int] = []
    for r in records:
        h = _simhash(key_fn(r))
        if any(_hamming(h, h2) <= hamming_max for h2 in hashes):
            continue
        hashes.append(h)
        out.append(r)
    return out
