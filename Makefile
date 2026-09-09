.PHONY: help lint test build verify

help:
	@printf '%s\n' \
	  'make verify  Run the same lint/test/build gates as CI' \
	  'make lint    Run Ruff' \
	  'make test    Run pytest' \
	  'make build   Build the Python package'

lint:
	ruff check .

test:
	pytest

build:
	python -m build

verify: lint test build
