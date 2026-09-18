"""Optional OpenTelemetry tracing/metrics for the perception-action loop.

`opentelemetry-api`/`opentelemetry-sdk` are an optional extra (`.[observability]`), not
a base dependency, so the base install and test suite must work without them. Every
entry point here degrades to a no-op when the extra isn't installed.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .capabilities import discover

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


def gpu_is_present() -> bool:
    """Best-effort GPU presence check, delegating to `capabilities.discover()`.

    Does not shell out to run `nvidia-smi` or parse its output; only checks whether the
    tool exists on PATH. Real utilization parsing is a follow-up once verified on real
    GPU hardware.
    """
    return discover().gpu_probe_tool_available


class _NoOpObservableGauge:
    """Stand-in for an OpenTelemetry ObservableGauge when the extra isn't installed."""


def _read_gpu_utilization(_options: Any) -> list[Any]:
    """Callback for the GPU utilization observable gauge.

    Reports no observations when no GPU is detected, rather than fabricating a value.
    Real `nvidia-smi` output parsing is a follow-up (see `gpu_is_present`'s docstring).
    """
    if not _OTEL_AVAILABLE:  # pragma: no cover - guarded by caller before registration
        return []
    # Presence-only for now: even when a GPU is detected, real utilization parsing via
    # `nvidia-smi` output is a follow-up, so we never emit an observation here rather
    # than guessing.
    return []


def get_gpu_utilization_gauge() -> Any:
    """Return an observable gauge for GPU utilization (no-op without the extra).

    When no GPU is present (checked via `gpu_is_present`), the gauge reports no
    observations rather than a fabricated value.
    """
    if not _OTEL_AVAILABLE:
        return _NoOpObservableGauge()
    meter = metrics.get_meter(_INSTRUMENTATION_NAME)
    return meter.create_observable_gauge(
        "siqoq.gpu.utilization",
        callbacks=[_read_gpu_utilization],
        description="GPU utilization percentage (unavailable when no GPU is detected)",
    )
