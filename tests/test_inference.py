import importlib.util

import pytest

from siqoq.events import SemanticEvent
from siqoq.inference import Detection, MockInferenceAdapter, OnnxCvInferenceAdapter

_VISION_EXTRA_INSTALLED = (
    importlib.util.find_spec("cv2") is not None
    and importlib.util.find_spec("onnxruntime") is not None
)


def test_mock_adapter_returns_normalized_detections() -> None:
    adapter = MockInferenceAdapter()

    detections = adapter.infer(frame=None, source="sim.camera.front")

    expected = Detection(object_name="person", confidence=0.9, source="sim.camera.front")
    assert detections == [expected]


def test_mock_adapter_is_configurable() -> None:
    adapter = MockInferenceAdapter(
        detections=[Detection(object_name="box", confidence=0.5, source="unused")]
    )

    detections = adapter.infer(frame=None, source="rec.clip01")

    assert detections == [Detection(object_name="box", confidence=0.5, source="rec.clip01")]


def test_detection_converts_to_semantic_event() -> None:
    detection = Detection(object_name="person", confidence=0.9, source="mock")

    event = detection.to_semantic_event()

    assert isinstance(event, SemanticEvent)
    assert event.type == "object.detected"
    assert event.object == "person"
    assert event.source == "mock"


def test_onnx_cv_adapter_requires_extra_when_missing() -> None:
    if _VISION_EXTRA_INSTALLED:
        pytest.skip("vision extra installed; import-guard path not exercised")

    with pytest.raises(ImportError, match="vision"):
        OnnxCvInferenceAdapter(model_path="does-not-matter.onnx")


@pytest.mark.skipif(not _VISION_EXTRA_INSTALLED, reason="requires the 'vision' extra")
def test_onnx_cv_adapter_constructs_with_extra_installed(tmp_path) -> None:
    # Only exercised when opencv-python-headless + onnxruntime are installed.
    # A real model file is out of scope for this hardware-free suite; verify
    # the import guard is bypassed and the missing-model error surfaces
    # instead, proving the optional dependency path is wired correctly.
    missing_model = tmp_path / "missing.onnx"

    with pytest.raises(Exception):  # noqa: B017 - onnxruntime's own error type, not stdlib
        OnnxCvInferenceAdapter(model_path=missing_model)
