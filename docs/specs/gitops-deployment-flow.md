# GitOps Deployment Flow (Fleet Scale) v0 / GitOps 배포 흐름 (플릿 규모) v0

Status: v0 (draft, documentation-only). Documents a proposed fleet-scale
GitOps flow required by Phase 5 (issue #62, part of #10).

**No GitOps controller, reconciler, or cluster is implemented or verified in
this repository.** Everything below describes a pattern to design toward,
not working code. Do not treat any command or file shape here as tested;
treat it the way `docs/specs/edge-deployment.md` treats its own procedures,
but one layer more speculative, since that doc's `docker` commands are
runnable today and this doc's reconciler is not.

Extends the single-node model in `docs/specs/edge-deployment.md` (#50) from
"one operator running `docker` commands on one device" to "many nodes whose
desired state lives in Git and converges without an operator touching each
device by hand." It does not replace that doc: the single-node procedure
remains the ground truth for what a deployment or rollback actually *does*
to a container (pull-by-digest, health check via `siqoq demo`, stop/start).
This doc only adds a layer above it that decides *when* and *for which
nodes* that procedure runs.

## Scope

- Fleet-scale rollout/rollback expressed through Git, and how its status
  becomes observable.
- Does not implement a reconciler, controller, or cluster. Does not mandate
  ArgoCD, Flux, or any other specific GitOps tool.
- Does not change the underlying single-node deployment mechanics in
  `docs/specs/edge-deployment.md` — digest pinning, health check, and
  stop/start semantics there are unchanged and reused as-is per node.
- Assumes but does not define the exact schema of a per-node workload spec
  file; that schema is the sibling declarative-workload-spec issue's
  responsibility (may not exist yet in this worktree). Here it is referred
  to generically as "a WorkloadSpec JSON file per node."

## Desired-state repository

A Git repository (or a directory within this repository — the choice is an
implementation detail, not a design constraint) holds one declarative
WorkloadSpec file per node or fleet segment. Each file specifies, at
minimum, the image digest that node should be running — the same digest
identity already defined in `docs/specs/edge-deployment.md`'s "Deployment
artifact" section:

```text
fleet/
  node-jetson-01.json   # WorkloadSpec: which digest this node should run
  node-jetson-02.json
  segment-warehouse-a.json
```

Git is the single source of truth for desired state. A node's actual
running digest is runtime fact, discovered by the same `docker inspect`
query already used in the single-node rollback procedure — never edited
directly as a side channel.

## Reconciliation model

An operator or controller process (unspecified here — this is the pattern,
not an implementation) is responsible for:

1. Reading desired state: the WorkloadSpec file for a given node from Git.
2. Reading actual state: the node's currently running image digest.
3. Diffing the two.
4. When they differ, applying the single-node deployment procedure from
   `docs/specs/edge-deployment.md` (pull by digest, stop, start, health
   check) to converge actual state toward desired state.
5. If the health check fails, applying the single-node rollback procedure
   from the same doc.

This is a description of the reconciliation *pattern* — pull-based
(node/agent polls Git) or push-based (external process pushes to nodes) are
both compatible implementations, and this doc takes no position between
them. Nothing here requires choosing a controller now; it requires only
that whatever controller is eventually built treats Git as desired state
and the existing single-node procedure as the only sanctioned way to change
a node's running image.

## Rollout and rollback as Git operations

- **Rollout** = a Git commit that changes a node's (or segment's)
  WorkloadSpec file to a new image digest. The commit message and diff are
  the change record; no separate deployment ticket is required to know
  what changed, when, or by whom.
- **Rollback** = a Git revert of that commit, restoring the previous
  digest in the WorkloadSpec file. Rollback is always a `git revert` (or
  equivalent auditable revert operation) against the desired-state
  repository — **never** an untracked manual edit on a device or an
  unrecorded change to a running container. This mirrors the single-node
  rollback procedure's requirement to only ever move to a previously
  recorded known-good digest, extended to require that the record live in
  Git history rather than an operator's memory or shell history.

Both operations are fully auditable via ordinary `git log` /
`git show` on the desired-state repository — the fleet-scale equivalent of
"record the currently running image's digest before touching anything" in
the single-node doc, except the record is Git history instead of a
one-off `docker inspect` capture.

## Observability hook points

No new telemetry code is proposed here. `src/siqoq/telemetry.py` already
defines the pattern any real reconciler should emit through:

- `start_span(name)` — a real reconciler would wrap each reconciliation
  pass, and each individual node's converge step, in a span (e.g.
  `"gitops.reconcile"`, `"gitops.reconcile.node"`), the same way spans
  already wrap stages of the perception-action loop.
- `get_events_emitted_counter()`-style counters — a real reconciler would
  add sibling counters (e.g. `siqoq.gitops.rollout.applied`,
  `siqoq.gitops.rollback.applied`) following the existing
  `siqoq.events.emitted` counter's shape: optional, no-op when the
  `observability` extra isn't installed, attributed with node/segment
  identifiers.
- Both degrade to no-ops without the `opentelemetry` extra, consistent with
  every other telemetry hook in this codebase — a GitOps reconciler must
  not introduce a hard dependency on OpenTelemetry being installed.

These are intended hook points for a future implementation, not new
interfaces added by this doc. No code in this repository currently emits
them.

## Explicitly out of scope

- No GitOps controller, reconciler, agent, or cluster (Kubernetes/K3s or
  otherwise) is implemented or verified in this repository. Everything
  above is a documented pattern only.
- No specific GitOps tool (ArgoCD, Flux, or otherwise) is mandated. Naming
  one as a reference implementation is left to future work if research
  later favors it.
- The WorkloadSpec file's exact schema — owned by the sibling
  declarative-workload-spec issue.
- Any change to the single-node deployment/rollback mechanics themselves;
  those remain exactly as defined in `docs/specs/edge-deployment.md`.
