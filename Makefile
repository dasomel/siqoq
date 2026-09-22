.PHONY: help install install-full lint test build verify verify-full container container-run

help:
	@printf '%s\n' \
	  'make install       Install the base package (editable, dev extra)' \
	  'make install-full  Also install vision/transport/observability extras' \
	  'make verify        Run the same lint/test/build gates as CI (base install)' \
	  'make verify-full   Run verify against install-full (exercises optional extras)' \
	  'make lint          Run Ruff' \
	  'make test          Run pytest' \
	  'make build         Build the Python package' \
	  'make container      Build the multi-arch image (docker buildx, amd64+arm64)' \
	  'make container-run  Build the amd64 image and run `siqoq demo` inside it'

install:
	pip install -e '.[dev]'

install-full:
	pip install -e '.[dev,vision,transport,observability]'

lint:
	ruff check .

test:
	pytest

build:
	python -m build

verify: lint test build

verify-full: install-full verify

container:
	docker buildx build --platform linux/amd64,linux/arm64 -t siqoq:ci .

container-run:
	docker buildx build --platform linux/amd64 --load -t siqoq:amd64 .
	docker run --rm siqoq:amd64 demo
