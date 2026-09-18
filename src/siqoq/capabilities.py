"""Best-effort runtime capability discovery.

Implements the "device capability discovery" scope item sketched in
`docs/specs/runtime-capability-outline.md`: a small, additive, pure-data
report of what the current process can actually do, so callers can branch
on real availability instead of catching `NotImplementedError` from
hardware-specific adapters.

Detection here is honest, not exhaustive: extras are checked via
`importlib.util.find_spec` (same pattern as `tests/test_transport.py`'s
`HAS_NATS`/`HAS_MQTT`), and GPU/accelerator presence is reported only as
"a known probe tool exists" or "unavailable" — never guessed. Actually
invoking `nvidia-smi` and parsing its output is out of scope (issue #49).
"""

from __future__ import annotations

import importlib.util
import platform
import shutil
from dataclasses import dataclass


def _module_available(module_name: str) -> bool:
    """Return True if `module_name` (possibly dotted) is importable right now.

    `importlib.util.find_spec` raises `ModuleNotFoundError` for a dotted name
    whose parent package isn't importable, so parent packages are checked
    first (mirrors `tests/test_transport.py`'s `HAS_MQTT` pattern).
    """
    parts = module_name.split(".")
    for i in range(1, len(parts) + 1):
        prefix = ".".join(parts[:i])
        if importlib.util.find_spec(prefix) is None:
            return False
    return True


def _extra_available(*module_names: str) -> bool:
    """Return True only if every named module is importable right now."""
    return all(_module_available(name) for name in module_names)


@dataclass(slots=True, frozen=True)
class RuntimeCapabilities:
    """Best-effort snapshot of what the current process can actually do."""

    os_name: str
    arch: str
    vision_extra_available: bool
    transport_nats_available: bool
    transport_mqtt_available: bool
    observability_extra_available: bool
    gpu_probe_tool_available: bool

    def to_dict(self) -> dict[str, bool | str]:
        return {
            "os_name": self.os_name,
            "arch": self.arch,
            "vision_extra_available": self.vision_extra_available,
            "transport_nats_available": self.transport_nats_available,
            "transport_mqtt_available": self.transport_mqtt_available,
            "observability_extra_available": self.observability_extra_available,
            "gpu_probe_tool_available": self.gpu_probe_tool_available,
        }


def discover() -> RuntimeCapabilities:
    """Discover runtime capabilities available in the current process.

    Best-effort and honest: unavailable/unverifiable capabilities report
    `False` rather than being guessed. GPU detection only checks whether a
    probe tool (`nvidia-smi`) exists on PATH; it is never invoked here.
    """
    return RuntimeCapabilities(
        os_name=platform.system(),
        arch=platform.machine(),
        vision_extra_available=_extra_available("cv2", "onnxruntime"),
        transport_nats_available=_extra_available("nats"),
        transport_mqtt_available=_extra_available("paho.mqtt.client"),
        observability_extra_available=_extra_available("opentelemetry"),
        gpu_probe_tool_available=shutil.which("nvidia-smi") is not None,
    )
