# Edge Deployment and Rollback v0 / 엣지 배포와 롤백 v0

Status: v0 (draft). Documents the deployment bundle format and single-node
deployment/rollback procedure required by Phase 3 (issue #50, part of #8).

Builds on the ARM64 container build (issue #46, not yet merged at time of
writing — this doc names the artifact it will produce, not an image already
present in this worktree). Does **not** implement fleet/orchestration
mechanics; that is explicitly Phase 5 / issue #10 and is out of scope here
per AGENTS.md's anti-premature-hardware/fleet-hardening principle.

## Scope

- Single edge device only. No fleet manager, no Kubernetes/K3s, no GitOps.
- Covers: deployment artifact identity, reproducible build, deploy
  procedure, health check, rollback procedure.
- Does not cover: multi-node rollout, declarative fleet specs, workload
  placement, or any of Phase 5 (#10)'s scope.

## Deployment artifact

The deployment unit is the container image built by issue #46's Dockerfile
and CI job (multi-stage build, `docker buildx build --platform
linux/amd64,linux/arm64 .`).

A deployed image is identified by its **content digest**, not a mutable tag:

```bash
docker pull ghcr.io/dasomel/siqoq@sha256:<digest>
```

A tag like `latest` or `edge` MAY label the current recommended build for
convenience, but the digest is the only identifier a deployment or rollback
step is allowed to pin to — a tag can move out from under a running device,
a digest cannot.

Each image also carries the package version from `pyproject.toml` (`version
= "0.1.0.dev0"` at present) as an OCI label, for human-readable traceability
alongside the digest:

```dockerfile
LABEL org.opencontainers.image.version="0.1.0.dev0"
```

Given a digest, the exact source commit and package version are always
recoverable from the image's own metadata — no external mapping table is
needed.

## Reproducible build

The same source commit must always produce the same image content:

- The Dockerfile pins an exact base image digest (not a floating tag such as
  `python:3.12-slim`), so the base layer cannot change silently between
  builds.
- Application dependencies are installed from the pinned versions in
  `pyproject.toml` / its lockfile, not from an unpinned `pip install` range.
- The build is run through issue #46's CI job (buildx, QEMU-emulated arm64),
  which is the canonical build path; local `docker buildx build` reproduces
  the same content when run against the same commit and base digest.

This gives a verifiable chain: source commit -> deterministic image content
-> content digest. Two builds of the same commit against the same pinned
base MUST produce the same digest; if they don't, that is a build
reproducibility bug, not an expected variation.

## Deployment procedure (single device)

No fleet manager or Kubernetes involved — this is a plain `docker`/`podman`
sequence run on one edge device.

1. Pull the target image by digest:

   ```bash
   docker pull ghcr.io/dasomel/siqoq@sha256:<new-digest>
   ```

2. Record the currently running image's digest before touching anything
   (needed for rollback):

   ```bash
   docker inspect --format '{{.Image}}' siqoq-runtime
   ```

3. Stop the currently running container:

   ```bash
   docker stop siqoq-runtime
   ```

4. Start the new container from the pulled digest:

   ```bash
   docker run -d --name siqoq-runtime ghcr.io/dasomel/siqoq@sha256:<new-digest>
   ```

5. Health-check the new container by running the package's own demo
   entrypoint and checking its exit code:

   ```bash
   docker exec siqoq-runtime siqoq demo
   echo "exit code: $?"
   ```

   Exit code `0` is the only pass condition; the demo path is hardware-free
   (see `docs/development.md`), so this check is valid on any edge device
   regardless of attached sensors.

If the health check passes, the deployment is done. If it fails, proceed to
rollback below rather than debugging in place on the edge device.

## Rollback procedure

Rollback requires the previous image digest to already be available, either
still cached locally on the device or pullable from the registry:

```bash
docker pull ghcr.io/dasomel/siqoq@sha256:<previous-digest>
```

Steps, once the health check in step 5 above fails:

1. Stop the failed container:

   ```bash
   docker stop siqoq-runtime
   docker rm siqoq-runtime
   ```

2. Start a container from the previous known-good digest (recorded in step 2
   of the deployment procedure, or from deployment history/logs):

   ```bash
   docker run -d --name siqoq-runtime ghcr.io/dasomel/siqoq@sha256:<previous-digest>
   ```

3. Re-run the same health check:

   ```bash
   docker exec siqoq-runtime siqoq demo
   echo "exit code: $?"
   ```

A device operator should always keep at least the current and previous
digest pulled locally, so rollback does not depend on registry availability
at the moment it's needed.

## Explicitly out of scope

- Any fleet manager, K3s/Kubernetes deployment, or GitOps flow — tracked in
  Phase 5 / issue #10.
- Jetson-specific base image or CUDA layer — a separate Jetson deployment
  profile, not introduced by issue #46 or this doc.
- Automated/unattended rollback triggers — the health check here is a manual
  gate an operator runs, not a supervisor process.
