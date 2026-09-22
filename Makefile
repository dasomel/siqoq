.PHONY: help install install-full lint test build verify verify-full \
        container container-run container-run-native

# Host architecture, mapped to Docker's platform naming (amd64/arm64).
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_M),x86_64)
  DOCKER_ARCH := amd64
else ifeq ($(UNAME_M),aarch64)
  DOCKER_ARCH := arm64
else ifeq ($(UNAME_M),arm64)
  DOCKER_ARCH := arm64
else
  DOCKER_ARCH := $(UNAME_M)
endif

help:
	@printf '%s\n' \
	  'make install              Install the base package (editable, dev extra)' \
	  'make install-full         Also install vision/transport/observability extras' \
	  'make verify               Run the same lint/test/build gates as CI (base install)' \
	  'make verify-full          Run verify against install-full (exercises optional extras)' \
	  'make lint                 Run Ruff' \
	  'make test                 Run pytest' \
	  'make build                Build the Python package' \
	  'make container            Build the multi-arch image (docker buildx, amd64+arm64)' \
	  'make container-run        Build the amd64 image and run `siqoq demo` inside it (matches CI; QEMU-emulated on non-amd64 hosts)' \
	  'make container-run-native Build+run for the detected host architecture ($(DOCKER_ARCH)) — no emulation'

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

container-run-native:
	docker buildx build --platform linux/$(DOCKER_ARCH) --load -t siqoq:$(DOCKER_ARCH) .
	docker run --rm siqoq:$(DOCKER_ARCH) demo
