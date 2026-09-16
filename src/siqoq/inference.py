"""Portable vision inference adapters.

Keeps the inference workload interface separate from hardware/runtime-specific
acceleration (see AGENTS.md: "Keep portable inference/workload logic separate
from hardware-specific acceleration adapters"). `InferenceAdapter` is the
stable contract; `MockInferenceAdapter` is stdlib-only so tests and CI run
hardware-free, while `OnnxCvInferenceAdapter` needs the optional `vision`
extra (OpenCV + ONNX Runtime) and is only importable when installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from siqoq.events import SemanticEvent


@dataclass(slots=True, frozen=True)
class Detection:
    """A single normalized detection result, hardware/runtime independent."""

    object_name: str
    confidence: float
    source: str

    def to_semantic_event(self) -> SemanticEvent:
        return SemanticEvent.detected(
            source=self.source,
            object_name=self.object_name,
            confidence=self.confidence,
        )


class InferenceAdapter(Protocol):
    """Stable interface producing normalized detections from a frame.

    A "frame" is intentionally left as `object` at this boundary: adapters
    decide what representation they accept (e.g. a numpy array for the
    OpenCV/ONNX backend, or an opaque fixture id for the mock backend).
    """

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        """Run inference on a single frame and return normalized detections."""
        ...


class MockInferenceAdapter:
    """Deterministic, dependency-free backend for hardware-free tests/CI.

    Returns a fixed detection list regardless of frame content, so tests can
    assert on the adapter contract without OpenCV/ONNX Runtime installed.
    """

    def __init__(self, detections: list[Detection] | None = None) -> None:
        self._detections = (
            detections
            if detections is not None
            else [
                Detection(object_name="person", confidence=0.9, source="mock"),
            ]
        )

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        del frame  # unused: mock backend ignores frame content by design
        return [
            Detection(object_name=d.object_name, confidence=d.confidence, source=source)
            for d in self._detections
        ]


class OnnxCvInferenceAdapter:
    """OpenCV preprocessing + ONNX Runtime inference backend.

    Requires the optional `vision` extra (`pip install -e '.[vision]'`).
    Imports are deferred to __init__ so importing this module never requires
    OpenCV/ONNX Runtime to be installed; only instantiating this class does.
    """

    def __init__(self, model_path: str | Path, *, input_size: tuple[int, int] = (224, 224)) -> None:
        try:
            import cv2  # noqa: F401
            import onnxruntime as ort
        except ImportError as exc:  # pragma: no cover - exercised only without extra
            raise ImportError(
                "OnnxCvInferenceAdapter requires the 'vision' extra: pip install -e '.[vision]'"
            ) from exc

        self._cv2 = cv2
        self._model_path = Path(model_path)
        self._input_size = input_size
        self._session = ort.InferenceSession(str(self._model_path))

    def _preprocess(self, frame: object) -> object:
        cv2 = self._cv2
        resized = cv2.resize(frame, self._input_size)
        return resized

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        preprocessed = self._preprocess(frame)
        input_name = self._session.get_inputs()[0].name
        outputs = self._session.run(None, {input_name: preprocessed})
        return self._parse_outputs(outputs, source=source)

    def _parse_outputs(self, outputs: list[object], *, source: str) -> list[Detection]:
        # Model-specific output parsing is intentionally minimal here; concrete
        # models should subclass or wrap this adapter to interpret their own
        # output tensor layout. Left as a design seam (AGENTS.md: avoid
        # hardening one vendor/model path prematurely).
        del outputs
        return []
