"""Local, read-only web dashboard for siqoq's existing data (issue #70).

Stdlib-only (`http.server`) so the base install stays zero-dependency. Binds
to localhost by default. Serves live data from the existing modules
(capabilities, fleet, scenario catalog, skills) directly — never fabricated
placeholder content. There are no write endpoints and no authentication;
exposing this beyond localhost is an explicit operator choice outside this
module's scope (see docs/specs/web-dashboard.md).

Routes are a fixed allowlist (``_PAGE_RESOURCES`` / `_ASSET_RESOURCES``), not
a filesystem path derived from the request: an unrecognized path — including
any `../` traversal attempt — can never match a dict key, so it always falls
through to 404 rather than reading an arbitrary package file.
"""

from __future__ import annotations

import importlib.resources
import json
from dataclasses import dataclass
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

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
    # GET /api/snapshot must stay read-only (see module docstring): never let
    # a catalog-referenced scenario config's output_path write to the host.
    results = [
        run_catalog_entry(entry, base_dir=path.parent, write_output=False) for entry in entries
    ]
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


#: GET routes that serve a full HTML page, mapped to their packaged resource
#: filename (kept flat in the package root, alongside ui.py).
_PAGE_RESOURCES: dict[str, str] = {
    "/": "ui_page.html",
    "/guide": "guide_page.html",
}

#: GET routes under /assets/, mapped to (packaged resource path, Content-Type).
#: This dict IS the allowlist: `do_GET` only ever loads a name found here, so
#: no request-derived string ever reaches a filesystem/resource lookup.
_ASSET_RESOURCES: dict[str, tuple[str, str]] = {
    "/assets/app.css": ("assets/app.css", "text/css; charset=utf-8"),
    "/assets/app.js": ("assets/app.js", "text/javascript; charset=utf-8"),
    "/assets/i18n.js": ("assets/i18n.js", "text/javascript; charset=utf-8"),
}


@cache
def _resource_bytes(relative_path: str) -> bytes:
    """Load one packaged resource file, cached by its fixed relative path.

    Cached: pages/assets are static per-process (only `/api/snapshot` is
    live), so re-reading them from disk on every request would be wasted
    I/O. `relative_path` is always one of the literal strings in
    `_PAGE_RESOURCES`/`_ASSET_RESOURCES` above, never request-derived.
    """
    resource = importlib.resources.files("siqoq")
    for part in relative_path.split("/"):
        resource = resource.joinpath(part)
    return resource.read_text(encoding="utf-8").encode("utf-8")


def make_handler(config: DashboardConfig) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib method name
            path = urlsplit(self.path).path

            if path in _PAGE_RESOURCES:
                self._send(_resource_bytes(_PAGE_RESOURCES[path]), "text/html; charset=utf-8")
                return
            if path == "/api/snapshot":
                body = json.dumps(build_snapshot(config)).encode("utf-8")
                self._send(body, "application/json")
                return
            if path in _ASSET_RESOURCES:
                resource_path, content_type = _ASSET_RESOURCES[path]
                self._send(_resource_bytes(resource_path), content_type)
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
