from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import platform
from typing import Sequence

from .contracts import DeviceCapabilities


@dataclass(frozen=True, slots=True)
class RuntimeManifest:
    name: str = "siqoq"
    version: str = "0.0.0-dev"
    profile: str = "laptop"
    model: str | None = None
    transports: Sequence[str] = ("memory",)
    features: Sequence[str] = ("generated-sensor", "static-inference", "mock-action")
    metadata: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))


def discover_capabilities() -> DeviceCapabilities:
    """Best-effort baseline discovery without vendor SDK dependencies."""

    return DeviceCapabilities(
        architecture=platform.machine() or "unknown",
        accelerator=None,
        sensors=(),
        actuators=(),
    )
