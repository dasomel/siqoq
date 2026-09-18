from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

from siqoq.capabilities import discover

HAS_VISION = importlib.util.find_spec("cv2") is not None and (
    importlib.util.find_spec("onnxruntime") is not None
)
HAS_NATS = importlib.util.find_spec("nats") is not None
HAS_MQTT = importlib.util.find_spec("paho") is not None and (
    importlib.util.find_spec("paho.mqtt.client") is not None
)
HAS_OTEL = importlib.util.find_spec("opentelemetry") is not None


def test_gpu_capability_reports_unavailable_not_a_guess() -> None:
    # This environment is CPU-only, no GPU probe tool present.
    caps = discover()
    assert caps.gpu_probe_tool_available is False


def test_extras_detection_matches_actual_importability() -> None:
    caps = discover()
    assert caps.vision_extra_available == HAS_VISION
    assert caps.transport_nats_available == HAS_NATS
    assert caps.transport_mqtt_available == HAS_MQTT
    assert caps.observability_extra_available == HAS_OTEL


def test_discover_reports_os_and_arch() -> None:
    caps = discover()
    assert caps.os_name
    assert caps.arch


def test_cli_capabilities_subcommand_prints_valid_json() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "siqoq.cli", "capabilities"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert "gpu_probe_tool_available" in payload
    assert "os_name" in payload
