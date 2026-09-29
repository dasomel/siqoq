# Web dashboard v0

Status: v0, now with in-page explanations, ko/en i18n, and a `/guide` page.

## Scope

A local, read-only web dashboard (`siqoq ui serve`) so a human can view
existing siqoq data without parsing JSON by hand. It is stdlib-only
(`http.server`) — no new dependency in the base install.

## What it shows

Served live from the existing modules, never fabricated:

- `capabilities` — this process's `RuntimeCapabilities` (`siqoq.capabilities.discover()`)
- `skills` — the built-in skill catalog (`siqoq.skills.list_catalog()`)
- `fleet_inventory` — entries from a fleet inventory JSONL file, if `--fleet-inventory` is passed
- `fleet_observability` — an aggregate summary from a results directory, if `--fleet-results-dir` is passed
- `scenario_catalog` — pass/fail per entry from a scenario catalog JSON file, if `--scenario-catalog` is passed

Each optional source reports `{"configured": false}` when not passed, or
`{"configured": true, "available": false, "reason": ...}` when the path
doesn't exist — never a fabricated or empty-looking result that could be
mistaken for "there is no data."

## Endpoints

- `GET /` — the dashboard: fetches `/api/snapshot` and renders it
- `GET /guide` — a static "how it works" page: the core loop, deployment
  modes, and how the dashboard's sections map onto them, with inline SVG
  diagrams; no live data
- `GET /api/snapshot` — the full snapshot as JSON
- `GET /assets/app.css`, `/assets/app.js`, `/assets/i18n.js` — shared static
  assets used by both pages

All of these are read-only `GET` requests. There is no write endpoint
anywhere in this module. `/`, `/guide`, and the three `/assets/*` paths are a
fixed allowlist in `ui.py` (`_PAGE_RESOURCES`/`_ASSET_RESOURCES`): a request
path only ever selects a dict key, never a filesystem path, so an unknown
path or a `../`-style traversal attempt always falls through to `404` rather
than reading an arbitrary package file.

## Explanations and language

Each dashboard section has a one-line subtitle plus an expandable "?" for
more detail (what it shows, which CLI flag/module it reads, how to read
values like "stalest" or a passing "error"-type scenario) — grounded in the
same modules the section renders, never invented.

The header's EN/한국어 toggle switches every UI string (chrome, labels,
descriptions, empty/error states, relative times) via `/assets/i18n.js`'s
dictionary; data values (node ids, entry ids, detail text, event types) are
never translated. Default language comes from `navigator.language` (falls
back to English for anything not starting with `ko`), the choice persists in
`localStorage`, and `?lang=ko`/`?lang=en` overrides both for one load.

## Security boundary

- Binds to `127.0.0.1` by default (`--host` to change). Binding to a
  non-localhost address is an explicit operator choice; this module does
  not add authentication, so exposing it beyond localhost without a
  reverse proxy/auth layer in front is the operator's responsibility, not
  covered by this issue's scope.
- No secrets are served: `RuntimeCapabilities` is boolean flags and
  OS/arch only; the fleet/scenario data is whatever local files the
  operator already has and explicitly points the server at.

## Usage

```bash
siqoq ui serve
siqoq ui serve --port 9000 --fleet-inventory examples/fleet/inventory.jsonl \
  --scenario-catalog examples/scenarios/catalog.json
```

## Compatibility rules

Additive only: new optional CLI flags and a new module. Never changes
`SemanticEvent`, `RuntimeCapabilities`, `FleetInventory`, or any other
existing contract. A breaking change here would be removing or renaming a
snapshot key that existing dashboards/scripts already depend on. `/guide`,
`/assets/*`, and the i18n dictionary are additive UI-only surfaces: they add
no new data sources and no new dependency (still stdlib-only, offline, no
external URLs).
