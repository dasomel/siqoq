"""Optional OpenTelemetry tracing/metrics for the perception-action loop.

`opentelemetry-api`/`opentelemetry-sdk` are an optional extra (`.[observability]`), not
a base dependency, so the base install and test suite must work without them. Every
entry point here degrades to a no-op when the extra isn't installed.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import metrics, trace

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when extra is not installed
    _OTEL_AVAILABLE = False

_INSTRUMENTATION_NAME = "siqoq"


def is_available() -> bool:
    """Return True when the opentelemetry extra is installed."""
    return _OTEL_AVAILABLE


@contextmanager
def start_span(name: str) -> Iterator[None]:
    """Start a span named `name`, or do nothing when OpenTelemetry isn't installed."""
    if not _OTEL_AVAILABLE:
        yield
        return
    tracer = trace.get_tracer(_INSTRUMENTATION_NAME)
    with tracer.start_as_current_span(name):
        yield


class _NoOpCounter:
    """Stand-in for an OpenTelemetry Counter when the extra isn't installed."""

    def add(self, amount: int | float, attributes: dict[str, Any] | None = None) -> None:
        pass


def get_events_emitted_counter() -> Any:
    """Return a counter for emitted semantic events (no-op without the extra)."""
    if not _OTEL_AVAILABLE:
        return _NoOpCounter()
    meter = metrics.get_meter(_INSTRUMENTATION_NAME)
    return meter.create_counter(
        "siqoq.events.emitted",
        description="Count of semantic events emitted",
    )
