# Model and Policy Artifact Loading Rules

Status: draft policy. No model/policy loading code exists yet (only `src/siqoq/events.py`,
`src/siqoq/cli.py`). This document defines the rules that any future loader MUST follow
before Siqoq executes downloaded model weights (e.g. ONNX) or policy/config artifacts,
especially on paths that can reach actuators. See `AGENTS.md` for the design-change gate
these rules enforce, and `SECURITY.md` for reporting/physical-safety policy this extends.

## Threat model

- Untrusted or tampered model/policy artifacts (supply-chain substitution, mirror
  compromise, MITM on download) leading to arbitrary code execution or corrupted
  inference/decision behavior.
- Unpinned "latest" references that silently drift to a different artifact between runs.
- Unsafe deserialization formats (e.g. Python `pickle`, `torch.load` in default mode,
  YAML with `!!python/object`) executing attacker-controlled code on load.
- Overly broad filesystem/network authority during load (arbitrary paths, arbitrary
  outbound hosts) used as an exfiltration or lateral-movement vector.
- Unobservable provenance: a semantic event or actuator decision cannot be traced back to
  which artifact/revision produced it.

## Rules

1. **Trusted formats / unsafe format policy.** Only load formats with no embedded
   executable code paths by default: ONNX weights, JSON/TOML/YAML (safe-load only, no
   custom tags) for policy/config. `pickle`, `torch.load` without
   `weights_only=True`, `joblib` of untrusted objects, and `eval`/`exec`-based config
   are prohibited for any artifact whose origin is not the project's own build. Any
   exception is a design change requiring review per `AGENTS.md`.
2. **Revision/digest pinning.** Artifacts MUST be referenced by immutable content
   digest (e.g. sha256) or an immutable revision (commit SHA / release tag pinned to a
   digest), never by a mutable pointer (`latest`, unpinned branch, floating tag).
3. **Provenance metadata.** Every loaded artifact's source URI, digest, and
   revision MUST be recorded in the runtime manifest and be attributable from resulting
   semantic events (extends the existing input -> inference -> semantic event ->
   decision -> action observability chain in `AGENTS.md`).
4. **Integrity verification.** Before load, the loader MUST verify the artifact's
   checksum/digest against the pinned value, and SHOULD verify a signature when the
   source publishes one. Verification failure MUST hard-fail (no silent fallback to an
   unverified copy).
5. **Provenance allowlisting.** Only sources on an explicit allowlist (specific
   registries/URLs/orgs) may be fetched from by default. Adding a new source class is a
   design change (cloud/model routing, per `AGENTS.md`).
6. **No remote code execution.** Loading a model or policy artifact MUST NOT execute
   remote code (custom `trust_remote_code`-style hooks, dynamic module loading from the
   artifact) by default. Any remote-code capability must be opt-in, off by default, and
   itself treated as a design change.
7. **Least privilege / sandboxing.** Loading MUST run with the minimum filesystem and
   network authority needed: a scoped read-only artifact cache directory, no writes
   outside it, and network access restricted to the allowlisted source during fetch only
   (no ambient network authority during inference/decision). Per `AGENTS.md`, any change
   to filesystem/network authority is itself a design change.
8. **Offline / air-gapped path.** A fully offline mode MUST exist: pre-fetched, digest
   verified artifacts loaded from a local cache with no network calls, for edge/Jetson
   deployments and reproducible laptop testing.
9. **Actuator gating.** Artifacts feeding any decision with actuator authority MUST pass
   all of the above before being eligible for that path; failure to verify MUST fail
   closed (no actuation), consistent with `SECURITY.md`'s physical-safety policy.
10. **Design-change review trigger.** Per `AGENTS.md`, any change to: sensor/event
    schema, public loader API, hardware-specific dependencies, cloud/model routing,
    actuator behavior, or filesystem/network authority — including adding a new artifact
    source, format, or relaxing pinning/verification — requires review as a design
    change, not routine implementation.

## Gaps flagged (not yet decided)

- No signature scheme is chosen yet (e.g. Sigstore vs. simple detached sha256 file);
  needs a design decision before first loader implementation.
- `docs/landscape.md`, referenced by issue #19, does not exist in this repo — the
  research-basis link is dangling and should be corrected or the file added.
- No allowlist of concrete trusted registries/orgs is defined yet (e.g. Hugging Face
  orgs, internal artifact store) — placeholder only.
- Key management/rotation for verifying signatures is unspecified.
- No decision yet on whether ONNX Runtime custom-op / execution-provider plugins count as
  "remote code" for rule 6 — flag for follow-up before ONNX loading is implemented.
