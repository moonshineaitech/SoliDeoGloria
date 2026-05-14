# Pull request

**What this PR does.**
One or two sentences.

**Type of change.** Check all that apply.
- [ ] New questions added (one or more bank modules)
- [ ] Existing question edited (theology / fairness / clarity)
- [ ] Scorer or aggregator change
- [ ] Provider adapter
- [ ] Documentation only
- [ ] CI / tooling
- [ ] Baseline run contribution

**For new questions / question edits:**
- [ ] I ran `python scripts/build_dataset.py` and committed the
      updated `data/CAB_FF_v3_dataset.json`.
- [ ] No duplicates (the builder confirms this).
- [ ] I added myself or a tradition reviewer's note in the PR
      description if the question touches tradition-specific theology.

**For code changes:**
- [ ] `pytest -q` passes locally.
- [ ] I added or updated tests as appropriate.

**For new banks / provider adapters:**
- [ ] Re-exported from the relevant `__init__.py`.

**Related issues:**
Closes #
