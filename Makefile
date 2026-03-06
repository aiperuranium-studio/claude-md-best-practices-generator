.PHONY: setup test lint fetch freshness

PYTHON := .venv/bin/python3
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff
DOCS_DIR := docs
SCRIPTS := skills/refresh-guidelines/scripts

setup:
	bash setup.sh

test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check $(SCRIPTS)/fetch-guidelines.py $(SCRIPTS)/parse-insights.py tests/

fetch:
	$(PYTHON) $(SCRIPTS)/fetch-guidelines.py --docs-dir $(DOCS_DIR)

freshness:
	$(PYTHON) $(SCRIPTS)/fetch-guidelines.py --check-freshness --docs-dir $(DOCS_DIR)
