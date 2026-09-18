"""GPIO actuation adapters: mock backend and a real-hardware stub.

This module defines the GPIO-level actuator boundary described in
AGENTS.md's actuator-authority rule: any new physical side effect or
actuator authority is a high-risk design change, so this issue is scoped
mock-only. Real GPIO access (e.g. RPi.GPIO, Jetson.GPIO, periphery,
pyserial) requires a dependency not currently approved in pyproject.toml
and, more importantly, requires an explicit design review before granting
actuation authority over physical pins. To stay hardware- and
dependency-free while still exercising the adapter contract:

- ``MockGpioAdapter`` stores pin states in an in-memory dict and is the
  hardware-free backend required by docs/development.md's
  "Hardware-specific work" rule.
- ``RealGpioAdapter`` is a documented stub backend: it documents the
  intended contract and raises ``NotImplementedError`` on ``open()``,
  pointing to a follow-up issue for the real hardware backend, mirroring
  ``UsbWebcamFrameSensor`` in video_sensors.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class GpioAdapter(Protocol):
    """Common lifecycle for GPIO pin actuation backends.

    Callers must ``open()`` before ``set_pin()``/``read_pin()`` and
    ``close()`` when done, mirroring ``FrameSensor`` in video_sensors.py.
    """

    def open(self) -> None: ...

    def close(self) -> None: ...

    def set_pin(self, pin: int, state: bool) -> None: ...

    def read_pin(self, pin: int) -> bool: ...

    def __enter__(self) -> GpioAdapter:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class MockGpioAdapter:
    """Hardware-free stand-in for a GPIO backend, backed by an in-memory dict.

    Unset pins default to ``False`` on ``read_pin()``.
    """

    _opened: bool = False
    _pin_states: dict[int, bool] = field(default_factory=dict)

    def open(self) -> None:
        self._opened = True
        self._pin_states = {}

    def close(self) -> None:
        self._opened = False
        self._pin_states = {}

    def set_pin(self, pin: int, state: bool) -> None:
        if not self._opened:
            raise RuntimeError("MockGpioAdapter.set_pin() called before open()")
        self._pin_states[pin] = state

    def read_pin(self, pin: int) -> bool:
        if not self._opened:
            raise RuntimeError("MockGpioAdapter.read_pin() called before open()")
        return self._pin_states.get(pin, False)

    def __enter__(self) -> MockGpioAdapter:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class RealGpioAdapter:
    """Real GPIO adapter contract, backed by a real-hardware stub.

    A real implementation needs a GPIO access dependency (e.g. RPi.GPIO,
    Jetson.GPIO, periphery, or pyserial) that is not yet approved for this
    project (see pyproject.toml), and granting actuator authority over
    physical pins is a high-risk design change per AGENTS.md. Use
    ``MockGpioAdapter`` for hardware-free development and CI; wire this
    class to a real backend in a follow-up issue once real hardware access
    is explicitly authorized.
    """

    chip: str = "/dev/gpiochip0"

    def open(self) -> None:
        raise NotImplementedError(
            "Real GPIO access is not implemented; no approved GPIO "
            "dependency yet and actuator authority requires explicit "
            "authorization. Use MockGpioAdapter for development, or "
            "implement this backend in a follow-up issue (see module "
            "docstring)."
        )

    def close(self) -> None:
        return None

    def set_pin(self, pin: int, state: bool) -> None:
        raise NotImplementedError("RealGpioAdapter.open() must succeed first")

    def read_pin(self, pin: int) -> bool:
        raise NotImplementedError("RealGpioAdapter.open() must succeed first")

    def __enter__(self) -> RealGpioAdapter:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
