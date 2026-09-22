from __future__ import annotations

import json
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from siqoq.ui import DashboardConfig, build_snapshot, make_handler


def test_snapshot_reports_unconfigured_sources_without_error() -> None:
    snapshot = build_snapshot(DashboardConfig())

    assert snapshot["fleet_inventory"] == {"configured": False}
    assert snapshot["fleet_observability"] == {"configured": False}
    assert snapshot["scenario_catalog"] == {"configured": False}
    assert "gpu_probe_tool_available" in snapshot["capabilities"]
    assert any(s["name"] == "object-detection" for s in snapshot["skills"])


def test_snapshot_reports_missing_configured_source_as_unavailable(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.jsonl"
    snapshot = build_snapshot(DashboardConfig(fleet_inventory_path=str(missing)))

    assert snapshot["fleet_inventory"]["configured"] is True
    assert snapshot["fleet_inventory"]["available"] is False


def test_snapshot_reads_real_fleet_inventory() -> None:
    snapshot = build_snapshot(
        DashboardConfig(fleet_inventory_path="examples/fleet/inventory.jsonl")
    )

    assert snapshot["fleet_inventory"]["available"] is True
    assert len(snapshot["fleet_inventory"]["entries"]) >= 1


def test_snapshot_reads_real_scenario_catalog() -> None:
    snapshot = build_snapshot(
        DashboardConfig(scenario_catalog_path="examples/scenarios/catalog.json")
    )

    assert snapshot["scenario_catalog"]["available"] is True
    assert len(snapshot["scenario_catalog"]["results"]) >= 1


def test_server_serves_html_and_json_snapshot() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DashboardConfig()))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.1)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as response:
            assert response.status == 200
            assert b"siqoq dashboard" in response.read()

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/snapshot") as response:
            assert response.status == 200
            payload = json.loads(response.read())
            assert "capabilities" in payload

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/nope") as response:
            pass
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    finally:
        server.shutdown()
        server.server_close()
