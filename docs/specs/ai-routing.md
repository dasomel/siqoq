# AI Routing v0

Status: v0 (draft; library-level routing only).

`siqoq.routing` provides a small boundary for choosing between a local
`InferenceAdapter` and an optional cloud-shaped adapter. `InferenceRouter`
accepts a required local adapter, an optional cloud adapter, and a
`RoutingPolicy` whose mode is `local`, `cloud`, or `auto`.

- `local` always selects the local adapter.
- `cloud` requires a cloud adapter and raises `RuntimeError` when none was
  supplied; it never silently falls back.
- `auto` selects cloud only when a cloud adapter was explicitly supplied,
  otherwise it selects local.

The default routing policy requires zero network access. The repository's
`MockCloudInferenceAdapter` is a stub-only interface shape that returns an
empty deterministic result and performs no network calls. Cloud inference
never runs unless explicitly selected with `RoutingPolicy(mode="cloud")`, or
with `mode="auto"` and a cloud adapter supplied. A real cloud backend is out
of scope and requires a future issue with network and dependency review.

This module is intentionally not wired into the CLI. It preserves the same
frame/source and normalized detection contract as `siqoq.inference` so local,
simulated, and future edge adapters remain interchangeable.
