import pytest

from siqoq.inference import Detection, MockInferenceAdapter
from siqoq.routing import InferenceRouter, MockCloudInferenceAdapter, RoutingPolicy


def _adapter(name: str) -> MockInferenceAdapter:
    return MockInferenceAdapter([Detection(name, 1.0, "unused")])


def test_default_routing_policy_is_local() -> None:
    assert RoutingPolicy().mode == "local"


def test_local_mode_always_uses_local_adapter() -> None:
    router = InferenceRouter(_adapter("local"), _adapter("cloud"), policy=RoutingPolicy("local"))

    assert router.infer(None, source="test")[0].object_name == "local"


def test_cloud_mode_uses_cloud_adapter() -> None:
    router = InferenceRouter(_adapter("local"), _adapter("cloud"), policy=RoutingPolicy("cloud"))

    assert router.infer(None, source="test")[0].object_name == "cloud"


def test_cloud_mode_without_adapter_raises() -> None:
    router = InferenceRouter(_adapter("local"), policy=RoutingPolicy("cloud"))

    with pytest.raises(RuntimeError, match="cloud inference adapter"):
        router.infer(None, source="test")


def test_auto_mode_prefers_cloud_when_provided() -> None:
    router = InferenceRouter(_adapter("local"), _adapter("cloud"), policy=RoutingPolicy("auto"))

    assert router.infer(None, source="test")[0].object_name == "cloud"


def test_auto_mode_falls_back_to_local_without_cloud() -> None:
    router = InferenceRouter(_adapter("local"), policy=RoutingPolicy("auto"))

    assert router.infer(None, source="test")[0].object_name == "local"


def test_invalid_routing_mode_raises() -> None:
    with pytest.raises(ValueError, match="routing mode"):
        RoutingPolicy("remote")


def test_mock_cloud_adapter_is_deterministic_stub() -> None:
    adapter = MockCloudInferenceAdapter()

    assert adapter.infer(object(), source="test") == []
