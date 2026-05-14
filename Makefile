.PHONY: help install dev test quickstart smoke validate build clean docs stats ci

help:
	@echo "CAB-FF — common tasks"
	@echo ""
	@echo "  make install        Install core package (pip install -e .)"
	@echo "  make dev            Install with dev extras (pytest, linters)"
	@echo "  make smoke          Run quickstart against the mock model (~5s)"
	@echo "  make test           Run the pytest suite (~10s)"
	@echo "  make validate       Validate data/CAB_FF_v3_dataset.json"
	@echo "  make build          Rebuild dataset from seed + banks"
	@echo "  make stats          Print dataset breakdown by dim / type / difficulty"
	@echo "  make ci             Full check: build + validate + test"
	@echo "  make clean          Remove pyc, caches, and run artifacts"
	@echo ""
	@echo "Provider examples (install the corresponding extras first):"
	@echo "  pip install -e .[anthropic]   # for Claude"
	@echo "  pip install -e .[openai]      # for GPT"
	@echo "  pip install -e .[litellm]     # for ~100 providers incl. Ollama"
	@echo "  pip install -e .[all-providers]"
	@echo ""
	@echo "  python examples/quickstart.py --provider anthropic --model claude-sonnet-4-6"
	@echo "  python examples/quickstart.py --provider openai --model gpt-4o"
	@echo "  python examples/quickstart.py --provider litellm --model ollama/llama3"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest -q tests/

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
