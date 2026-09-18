# Multi-stage build for the base siqoq package (no hardware/vendor extras).
# Targets linux/amd64 and linux/arm64 via `docker buildx build --platform ...`.
# Jetson/CUDA-specific images are a separate profile (see issues #47/#48), not this file.

FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim AS runtime

COPY --from=builder /install /usr/local

WORKDIR /app

ENTRYPOINT ["siqoq"]
CMD ["demo"]

# Override the default command to run a scenario instead of the demo, e.g.:
#   docker run --rm -v "$PWD/examples:/app/examples" <image> scenario run --config examples/scenario.json
