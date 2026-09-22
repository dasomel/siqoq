"""Local, read-only web dashboard for siqoq's existing data (issue #70).

Stdlib-only (`http.server`) so the base install stays zero-dependency. Binds
to localhost by default. Serves live data from the existing modules
(capabilities, fleet, scenario catalog, skills) directly — never fabricated
placeholder content. There are no write endpoints and no authentication;
exposing this beyond localhost is an explicit operator choice outside this
module's scope (see docs/specs/web-dashboard.md).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .capabilities import discover
from .fleet import FleetInventory, aggregate_results
from .scenario import load_catalog, run_catalog_entry
from .skills import list_catalog


@dataclass(slots=True, frozen=True)
class DashboardConfig:
    """Optional local data sources the dashboard reads from.

    Every field is optional: a source that isn't configured, or whose file
    doesn't exist, is reported as unavailable rather than causing an error.
    """

    fleet_inventory_path: str | None = None
    fleet_results_dir: str | None = None
    scenario_catalog_path: str | None = None


def _fleet_inventory_snapshot(path: str | None) -> dict[str, Any]:
    if path is None:
        return {"configured": False}
    if not Path(path).exists():
        return {"configured": True, "available": False, "reason": f"not found: {path}"}
    inventory = FleetInventory.from_jsonl(path)
    return {
        "configured": True,
        "available": True,
        "entries": [entry.to_dict() for entry in inventory.entries],
    }


def _fleet_observability_snapshot(results_dir: str | None) -> dict[str, Any]:
    if results_dir is None:
        return {"configured": False}
    if not Path(results_dir).is_dir():
        return {"configured": True, "available": False, "reason": f"not found: {results_dir}"}
    summary = aggregate_results(results_dir).to_dict()
    return {"configured": True, "available": True, "summary": summary}


def _scenario_catalog_snapshot(catalog_path: str | None) -> dict[str, Any]:
    if catalog_path is None:
        return {"configured": False}
    path = Path(catalog_path)
    if not path.exists():
        return {"configured": True, "available": False, "reason": f"not found: {catalog_path}"}
    entries = load_catalog(path)
    results = [run_catalog_entry(entry, base_dir=path.parent) for entry in entries]
    return {
        "configured": True,
        "available": True,
        "results": [
            {"entry_id": r.entry_id, "passed": r.passed, "detail": r.detail} for r in results
        ],
    }


def build_snapshot(config: DashboardConfig) -> dict[str, Any]:
    """Gather all dashboard data as one JSON-serializable snapshot."""
    return {
        "capabilities": discover().to_dict(),
        "skills": [
            {"name": s.name, "event_types": list(s.event_types), "description": s.description}
            for s in list_catalog()
        ],
        "fleet_inventory": _fleet_inventory_snapshot(config.fleet_inventory_path),
        "fleet_observability": _fleet_observability_snapshot(config.fleet_results_dir),
        "scenario_catalog": _scenario_catalog_snapshot(config.scenario_catalog_path),
    }


_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>siqoq dashboard (read-only)</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; }}
h1 {{ font-size: 1.25rem; }}
h2 {{ font-size: 1rem; margin-top: 2rem; border-bottom: 1px solid #ccc; }}
pre {{ background: #f5f5f5; padding: 0.75rem; overflow-x: auto; }}
.note {{ color: #666; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>siqoq dashboard</h1>
<p class="note">Read-only. Localhost by default. Data below is live from this
process's modules, not fabricated.</p>
<h2>Capabilities</h2>
<pre id="capabilities"></pre>
<h2>Skill catalog</h2>
<pre id="skills"></pre>
<h2>Fleet inventory</h2>
<pre id="fleet_inventory"></pre>
<h2>Fleet observability</h2>
<pre id="fleet_observability"></pre>
<h2>Scenario catalog results</h2>
<pre id="scenario_catalog"></pre>
<script>
fetch("/api/snapshot").then(r => r.json()).then(data => {{
  for (const key of Object.keys(data)) {{
    const el = document.getElementById(key);
    if (el) el.textContent = JSON.stringify(data[key], null, 2);
  }}
}});
</script>
</body>
</html>
"""


def make_handler(config: DashboardConfig) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib method name
            if self.path == "/":
                body = _PAGE_TEMPLATE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path == "/api/snapshot":
                body = json.dumps(build_snapshot(config)).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - stdlib signature
            pass  # keep stdout limited to the CLI's own output

    return DashboardHandler


def serve(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    config: DashboardConfig | None = None,
) -> None:
    """Run the dashboard HTTP server until interrupted (blocking call)."""
    resolved_config = config if config is not None else DashboardConfig()
    server = ThreadingHTTPServer((host, port), make_handler(resolved_config))
    print(f"siqoq dashboard (read-only) at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
