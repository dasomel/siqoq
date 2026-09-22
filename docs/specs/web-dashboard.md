# Web dashboard v0

Status: v0.

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

- `GET /` — an HTML page that fetches `/api/snapshot` and renders it
- `GET /api/snapshot` — the full snapshot as JSON

Both are read-only `GET` requests. There is no write endpoint anywhere in
this module.

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
snapshot key that existing dashboards/scripts already depend on.
