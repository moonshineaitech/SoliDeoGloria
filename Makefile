.PHONY: install dev test quickstart smoke validate build clean docs

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest -q tests/

quickstart:
	python examples/quickstart.py

smoke: quickstart

# Smoke + the build script + the validator
validate:
	python -m cab_ff.cli validate data/CAB_FF_v3_dataset.json

build:
	python scripts/build_dataset.py

# Rebuild the dataset and re-run the full test suite
ci: build validate test

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f quickstart_results.json
	rm -f examples/.quickstart_sample.json

docs:
	@echo "Docs index:"
	@ls -1 docs/ | sed 's/^/  docs\//'
	@ls -1 rubrics/ | sed 's/^/  rubrics\//'

stats:
	@python -c "import json; from collections import Counter; \
        d=json.load(open('data/CAB_FF_v3_dataset.json'))['questions']; \
        print('Total:', len(d)); \
        print('By dim:', dict(sorted(Counter(q['dimension'] for q in d).items()))); \
        print('By type:', dict(sorted(Counter(q['question_type'] for q in d).items()))); \
        print('By difficulty:', dict(sorted(Counter(q['difficulty'] for q in d).items())))"
