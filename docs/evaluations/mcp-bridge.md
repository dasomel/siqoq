# Evaluation: Optional MCP Bridge for Agent Integration

Issue: #21 — Evaluate optional MCP bridge for agent integration.

## Goal

Explore MCP (Model Context Protocol) as an optional northbound interface so external
LLM agents can query Siqoq semantic events, without making MCP or an LLM mandatory for
core execution, and without weakening the semantic-event / safety-gate boundaries
defined in `docs/architecture.md` and `docs/principles.md`.

## Recommendation

Adopt an **MCP adapter, not a native rewrite of Siqoq's API**: a separate, optional
process that translates existing Siqoq semantic events into MCP resources/tools for
read access only. Do not build an MCP-native event or action API — Siqoq's own
contracts (semantic events, Action Requests, policy/safety gate) stay canonical, and
MCP is one more adapter consuming them, matching the "stable contracts over vendor
lock-in" principle (principles.md #4).

## Architecture Decision Record

**Decision: MCP adapter over event bus, vs. exposing a native Siqoq HTTP/gRPC API vs. no bridge**

| Option | Pros | Cons |
|---|---|---|
| MCP adapter subscribing to existing event bus/log | Reuses existing contracts; isolated blast radius; off by default; matches "integrations, not domain model" | Extra process to run; MCP schema must be kept in sync with event schema changes |
| Native Siqoq HTTP/gRPC API for agents | One less protocol | Duplicates event bus responsibilities; couples core API surface to agent-integration churn |
| No bridge (status quo) | Zero new risk | Blocks the experimentation use case in the issue's research basis |

**Chosen: MCP adapter.** It is additive, reversible (can be deleted without touching
core), and keeps the safety/action boundary intact because it is a *consumer* of
semantic events, not a producer of actions in v1.

## Scope: v1 is read-only

v1 exposes only **read** MCP resources/tools:

- `list_recent_events` — list recent semantic events (bounded, paginated)
- `get_scenario_summary` — summarize current/recorded scenario state

**No write/action-issuing tool ships in v1.** Any tool that would let an MCP client
trigger an Action Request is explicitly deferred to a follow-up issue, and that
follow-up must go through its own high-risk design review per AGENTS.md's rule that
actuator authority is a design-change trigger. This decision exists because an
MCP-driven write path is the highest-risk part of this feature (it would let an
external LLM client indirectly reach the safety gate), and separating it lets the
read-only value land now without inheriting that risk.

## Process and packaging boundary

The MCP server is a **separate, optional process/module** (e.g.
`siqoq.mcp_bridge`), not imported by the core runtime's default import path. It:

- ships as an optional extra (e.g. `pip install siqoq[mcp]` or an equivalent optional
  dependency group), so core installs never pull in MCP dependencies
- is **off by default** and only starts when explicitly enabled via a config flag
  (e.g. `SIQOQ_MCP_ENABLED=1` or `mcp.enabled: true` in config), matching the
  "optional, not mandatory" language in the issue and in principles.md #4
- reads from the existing event bus/log as a client, so it cannot bypass the policy
  or safety gate — it has no code path to Action execution in v1

## Auth / identity model for MCP clients

Because AGENTS.md flags network/filesystem authority as a design-change trigger, v1
picks the smallest-authority default:

**Default: local-only Unix domain socket, no network listener.** The MCP server binds
a Unix socket (e.g. `/run/siqoq/mcp.sock` or a user-scoped equivalent) readable only by
the OS user/group running Siqoq. This avoids introducing a network-reachable service
by default and keeps the attack surface equivalent to existing local tooling.

If a networked deployment is later needed (e.g. remote agent), it must be a separate,
explicitly-opted-in mode requiring a static API key or mTLS client cert — never enabled
by the same flag that turns on the local socket. That networked mode is out of scope
for v1 and should be its own follow-up issue with its own review, since it changes the
network-authority profile Siqoq exposes.

## Audit fields

Every MCP request the adapter serves, minimum required fields (structured, one record
per request), aligned with principles.md #5 (observable by default):

- `source_identity` — OS user (Unix socket) or API key ID (networked mode, future)
- `timestamp` — request receipt time (UTC, ISO 8601)
- `requested_tool` — MCP resource/tool name and parameters
- `outcome` — success / error / denied, plus error code if applicable

These records emit through Siqoq's existing telemetry path (OpenTelemetry per
architecture.md §7) rather than a bespoke log format.

## Edge cases

- **Nonexistent event-type resource**: requesting a resource for an event type Siqoq
  does not emit must return a **typed MCP error** (e.g. `NotFoundError` with the
  requested type named), never a silent empty list. Silent empty results are
  indistinguishable from "no events yet" and would mislead an agent client.
- **Event log read consistency**: reads must be snapshot- or append-only-consistent —
  a `list_recent_events` call must not observe a partially-written event, and a paged
  read must not skip or duplicate events due to concurrent appends. This can be
  satisfied by reading from an append-only log/offset cursor rather than a mutable
  store.

## Acceptance evidence (measurable)

- `make verify` and the full test suite pass with the MCP module **absent or
  uninstalled** (i.e., core has zero import-time dependency on `mcp` package or the
  bridge module) — proves the optionality claim, not just documents it.
- Proof-of-concept: MCP client (e.g. a minimal MCP inspector/test client) connects over
  the local Unix socket to a running instance with a **mock actuator/event source**
  and successfully lists events and fetches a scenario summary.
- For any future write-path follow-up: an automated test must demonstrate a
  policy-denied action is **rejected by the safety gate**, not merely reviewed by
  inspection — e.g. a test that submits an MCP-originated Action Request that the
  policy denies, and asserts the mock actuator never receives it.

## Follow-up issues

1. **MCP write/action tool + high-risk design review** — the deferred write path
   above; must define how MCP-originated Action Requests are distinguished/rate-limited
   from other sources and pass the policy-denied automated test.
2. **Networked MCP auth mode** — API key or mTLS option for remote agents, as its own
   design change per AGENTS.md network-authority rule.
3. **MCP schema versioning** — track how `list_recent_events` / `get_scenario_summary`
   evolve alongside the semantic event schema so the bridge doesn't silently drift.

## Non-goals

This evaluation does not implement code, add dependencies, or change any existing
module's import path. It documents the decision and design for a future implementation
issue.
