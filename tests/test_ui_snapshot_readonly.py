"""Regression test for issue #75: GET /api/snapshot must never write to disk.

``_scenario_catalog_snapshot`` runs every catalog entry to build the
dashboard snapshot; before the fix, a catalog entry whose scenario config
set ``output_path`` caused that GET request to write a file as a side
effect (see docs/evaluations/sandbox-execution-boundary.md). This mirrors
the server-request approach in tests/test_ui.py.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from siqoq.ui import DashboardConfig, make_handler


def test_get_snapshot_does_not_write_scenario_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "out.jsonl"
    # Pre-existing content: the pre-fix bug truncated/overwrote this path.
    output_path.write_text("operator-owned\n", encoding="utf-8")
    scenario_config_path = tmp_path / "scenario.json"
    scenario_config_path.write_text(
        json.dumps({"adapter": "generated", "steps": 3, "output_path": str(output_path)}),
        encoding="utf-8",
    )
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "scenarios": [
                    {
                        "id": "tmp-generated",
                        "description": "tmp scenario for read-only GET test",
                        "config_path": "scenario.json",
                        "expected_outcome": "success",
                        "min_event_count": 3,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    config = DashboardConfig(scenario_catalog_path=str(catalog_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(config))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.1)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/snapshot") as response:
            assert response.status == 200
            payload = json.loads(response.read())
    finally:
        server.shutdown()
        server.server_close()

    catalog_snapshot = payload["scenario_catalog"]
    assert catalog_snapshot["available"] is True
    results = catalog_snapshot["results"]
    assert len(results) == 1
    assert results[0]["entry_id"] == "tmp-generated"
    assert results[0]["passed"] is True, results[0]["detail"]

    assert output_path.read_text(encoding="utf-8") == "operator-owned\n"
