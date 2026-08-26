import json

from siqoq.runtime import RuntimeManifest, discover_capabilities


def test_runtime_manifest_is_machine_readable() -> None:
    payload = json.loads(RuntimeManifest().to_json())

    assert payload["name"] == "siqoq"
    assert payload["profile"] == "laptop"
    assert "generated-sensor" in payload["features"]


def test_capability_discovery_has_architecture() -> None:
    capabilities = discover_capabilities()

    assert capabilities.architecture
    assert capabilities.accelerator is None
