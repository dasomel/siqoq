"""Frame-level sensor adapters: recorded video and USB/UVC webcam.

This module defines the frame-oriented sensor boundary described in
docs/architecture.md ("Sensor adapters"): a source-agnostic ``FrameSensor``
interface with an explicit open/read/close lifecycle and normalized frame
metadata, so downstream inference code never sees vendor-specific types.

Real container/codec decoding (e.g. MP4/H.264) and real UVC camera capture
both require dependencies not currently approved in pyproject.toml (e.g.
opencv-python, PyAV, pyuvc). To stay hardware- and dependency-free:

- ``RecordedVideoFileSensor`` reads a deterministic JSONL frame fixture
  (one JSON object per line: width/height/format/payload) rather than
  decoding a real video container. This is enough to exercise the adapter
  contract and CI without a physical camera or new heavy dependencies.
- ``UsbWebcamFrameSensor`` is a stub backend: it documents the intended
  contract and raises ``NotImplementedError`` on ``open()``, pointing to a
  follow-up issue for the real capture backend.
- ``MockWebcamFrameSensor`` is the mock/fake backend required by
  docs/development.md's "Hardware-specific work" rule so the webcam side of
  the interface can still be exercised without hardware.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True, frozen=True)
class FrameMetadata:
    """Normalized, vendor-neutral description of one captured frame."""

    source: str
    index: int
    timestamp: str
    width: int
    height: int
    format: str = "raw"


@dataclass(slots=True, frozen=True)
class Frame:
    """A single frame: normalized metadata plus its raw payload bytes."""

    metadata: FrameMetadata
    payload: bytes


class FrameSensor(Protocol):
    """Common lifecycle for recorded-video and physical camera sources.

    Callers must ``open()`` before ``read()`` and ``close()`` when done.
    ``read()`` returns ``None`` once the source is exhausted (end of file
    or, for live sources, on graceful stop) instead of raising.
    """

    def open(self) -> None: ...

    def read(self) -> Frame | None: ...

    def close(self) -> None: ...

    def __enter__(self) -> FrameSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class RecordedVideoFileSensor:
    """Reads frames from a deterministic JSONL fixture file.

    Each line is a JSON object: ``{"timestamp": ..., "width": ..., "height":
    ..., "format": ..., "payload_b64": ...}``. This stands in for real video
    file decoding (MP4/H.264 via OpenCV or PyAV) which is not implemented
    here to avoid adding unapproved heavy dependencies; see module docstring.
    """

    path: Path
    source: str = "file.video.recorded"
    _lines: list[str] | None = None
    _index: int = 0

    def open(self) -> None:
        with self.path.open(encoding="utf-8") as handle:
            self._lines = [line for line in handle if line.strip()]
        self._index = 0

    def read(self) -> Frame | None:
        if self._lines is None:
            raise RuntimeError("RecordedVideoFileSensor.read() called before open()")
        if self._index >= len(self._lines):
            return None
        record = json.loads(self._lines[self._index])
        metadata = FrameMetadata(
            source=self.source,
            index=self._index,
            timestamp=record["timestamp"],
            width=record["width"],
            height=record["height"],
            format=record.get("format", "raw"),
        )
        payload = base64.b64decode(record["payload_b64"])
        self._index += 1
        return Frame(metadata=metadata, payload=payload)

    def close(self) -> None:
        self._lines = None
        self._index = 0

    def __enter__(self) -> RecordedVideoFileSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class UsbWebcamFrameSensor:
    """USB/UVC webcam adapter contract, backed by a real capture stub.

    A real implementation needs a UVC/camera capture dependency (e.g.
    opencv-python's VideoCapture or pyuvc) that is not yet approved for this
    project (see pyproject.toml). Use ``MockWebcamFrameSensor`` for
    hardware-free development and CI; wire this class to a real backend in
    a follow-up once a dependency is approved.
    """

    device: str = "/dev/video0"

    def open(self) -> None:
        raise NotImplementedError(
            "Real USB/UVC capture is not implemented; no approved capture "
            "dependency yet. Use MockWebcamFrameSensor for development, or "
            "implement this backend in a follow-up (see module docstring)."
        )

    def read(self) -> Frame | None:
        raise NotImplementedError("UsbWebcamFrameSensor.open() must succeed first")

    def close(self) -> None:
        return None

    def __enter__(self) -> UsbWebcamFrameSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class MockWebcamFrameSensor:
    """Hardware-free stand-in for a UVC webcam, yielding deterministic frames."""

    source: str = "webcam.mock.front"
    width: int = 4
    height: int = 4
    frame_count: int = 3
    _opened: bool = False
    _index: int = 0

    def open(self) -> None:
        self._opened = True
        self._index = 0

    def read(self) -> Frame | None:
        if not self._opened:
            raise RuntimeError("MockWebcamFrameSensor.read() called before open()")
        if self._index >= self.frame_count:
            return None
        payload = bytes([self._index]) * (self.width * self.height)
        metadata = FrameMetadata(
            source=self.source,
            index=self._index,
            timestamp=f"mock-frame-{self._index}",
            width=self.width,
            height=self.height,
            format="raw",
        )
        self._index += 1
        return Frame(metadata=metadata, payload=payload)

    def close(self) -> None:
        self._opened = False
        self._index = 0

    def __enter__(self) -> MockWebcamFrameSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
