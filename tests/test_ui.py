from __future__ import annotations

import importlib.resources
import json
import re
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from siqoq.ui import DashboardConfig, _resource_bytes, build_snapshot, make_handler

_SECTION_IDS = (
    "kpis",
    "fleet",
    "scenarios",
    "observability",
    "host",
    "skills",
)

_PAGE_RESOURCES = {
    "/": "ui_page.html",
    "/guide": "guide_page.html",
}

_ASSET_PATHS = {
    "/assets/app.css": "text/css",
    "/assets/app.js": "javascript",
    "/assets/i18n.js": "javascript",
}


def _served_pages() -> list[str]:
    return [_resource_bytes(name).decode("utf-8") for name in _PAGE_RESOURCES.values()]


def _i18n_dict() -> dict[str, dict[str, str]]:
    text = _resource_bytes("assets/i18n.js").decode("utf-8")
    match = re.search(r"var DICT = (\{.*?\n\});", text, re.S)
    assert match, "could not find `var DICT = {...};` literal in assets/i18n.js"
    return json.loads(match.group(1))


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


def test_pages_have_no_literal_template_braces() -> None:
    for page in _served_pages():
        assert "{{" not in page
        assert "}}" not in page


def test_pages_are_loaded_from_the_packaged_resources() -> None:
    for route, name in _PAGE_RESOURCES.items():
        resource_text = importlib.resources.files("siqoq").joinpath(name).read_text(
            encoding="utf-8"
        )
        assert _resource_bytes(name) == resource_text.encode("utf-8"), route


def test_dashboard_page_has_all_expected_section_landmarks() -> None:
    page = _resource_bytes("ui_page.html").decode("utf-8")

    for section_id in _SECTION_IDS:
        assert f'id="{section_id}"' in page, f"missing section id={section_id!r}"


def test_pages_and_assets_have_no_external_urls() -> None:
    for page in _served_pages():
        assert not re.search(r"https?://", page)
    for _route, resource_path in {
        "/assets/app.css": "assets/app.css",
        "/assets/app.js": "assets/app.js",
        "/assets/i18n.js": "assets/i18n.js",
    }.items():
        text = _resource_bytes(resource_path).decode("utf-8")
        assert not re.search(r"https?://", text)


def test_i18n_dictionary_has_identical_ko_and_en_keys() -> None:
    data = _i18n_dict()

    assert set(data) == {"en", "ko"}
    en_keys, ko_keys = set(data["en"]), set(data["ko"])
    assert en_keys == ko_keys, (en_keys ^ ko_keys)
    assert len(en_keys) > 0


def test_every_data_i18n_key_in_html_exists_in_the_dictionary() -> None:
    data = _i18n_dict()
    en_keys = set(data["en"])

    key_pattern = re.compile(r'data-i18n="([^"]+)"')
    attr_pattern = re.compile(r'data-i18n-attr="([^"]+)"')

    for page in _served_pages():
        for key in key_pattern.findall(page):
            assert key in en_keys, f"data-i18n key {key!r} missing from i18n.js dictionary"
        for spec in attr_pattern.findall(page):
            for pair in spec.split(","):
                _attr, _, key = pair.partition(":")
                key = key.strip()
                assert key in en_keys, f"data-i18n-attr key {key!r} missing from i18n.js dictionary"


# Known-bad/garbled Korean tokens fixed by hand (typos or non-existent words);
# regression guard so they don't silently reappear in a future edit.
_BAD_KO_TOKENS = (
    "스텀",  # should be 스텁 (stub)
    "큓스처",  # should be 픽스처 (fixture)
    "액추어이터",  # should be 액추에이터 (actuator)
    "샹박스",  # should be 샌드박스 (sandbox)
    "캐처",  # should be 캡처 (capture)
    "mock전용",  # missing space: should be "mock 전용"
)


def test_ko_dictionary_has_no_known_bad_tokens() -> None:
    data = _i18n_dict()

    for key, value in data["ko"].items():
        for token in _BAD_KO_TOKENS:
            msg = f"ko[{key!r}] still contains garbled token {token!r}: {value!r}"
            assert token not in value, msg

    # "액추어" alone (not part of "액추에이터") is also wrong; every occurrence
    # of the substring must be part of the correct word "액추에이터".
    for key, value in data["ko"].items():
        remainder = value.replace("액추에이터", "")
        assert "액추어" not in remainder, f"ko[{key!r}] still contains garbled 액추어: {value!r}"


def test_server_serves_dashboard_and_guide_pages_and_json_snapshot() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DashboardConfig()))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.1)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "text/html; charset=utf-8"
            assert b"siqoq" in response.read()

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/guide") as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "text/html; charset=utf-8"
            assert b"guide" in response.read().lower()

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/snapshot") as response:
            assert response.status == 200
            payload = json.loads(response.read())
            assert "capabilities" in payload
    finally:
        server.shutdown()
        server.server_close()


def test_server_serves_allowlisted_assets_with_correct_content_type() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DashboardConfig()))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.1)
        for route, expect_substring in _ASSET_PATHS.items():
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{route}") as response:
                assert response.status == 200
                assert expect_substring in response.headers["Content-Type"]
                assert len(response.read()) > 0
    finally:
        server.shutdown()
        server.server_close()


def test_server_404s_unknown_and_traversal_paths() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DashboardConfig()))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.1)
        not_found_paths = [
            "/nope",
            "/assets/../ui.py",
            "/assets/%2e%2e/ui.py",
            "/assets/nope.js",
        ]
        for path in not_found_paths:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}{path}")
                raise AssertionError(f"expected 404 for {path!r}")
            except urllib.error.HTTPError as exc:
                assert exc.code == 404, path
    finally:
        server.shutdown()
        server.server_close()
