from siqoq.adapters import AllowListSafetyGate, GeneratedSensor, MemoryTransport, MockActionAdapter, StaticInference
from siqoq.pipeline import NoOpPolicy, SiqoqPipeline


def test_hardware_free_pipeline_emits_semantic_event() -> None:
    transport = MemoryTransport()
    pipeline = SiqoqPipeline(
        sensor=GeneratedSensor(count=1),
        inference=StaticInference(),
        transport=transport,
        policy=NoOpPolicy(),
        safety=AllowListSafetyGate(),
        action=MockActionAdapter(),
    )

    result = pipeline.run_once()

    assert len(result.events) == 1
    assert result.events[0].type == "object.detected"
    assert result.events[0].object == "person"
    assert result.events[0].source == "sim.camera.front"
    assert len(transport.messages) == 1
    assert result.action_results == []


def test_pipeline_stops_when_sensor_is_exhausted() -> None:
    pipeline = SiqoqPipeline(
        sensor=GeneratedSensor(count=0),
        inference=StaticInference(),
        transport=MemoryTransport(),
        policy=NoOpPolicy(),
        safety=AllowListSafetyGate(),
        action=MockActionAdapter(),
    )

    result = pipeline.run_once()

    assert result.events == []
    assert result.action_results == []
