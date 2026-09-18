# Evaluation: NVIDIA Jetson deployment profile spike

Tracking: #47 (part of #8). Related: #46 (generic ARM64 container build).

**No Jetson hardware verification has been performed anywhere in this repository.**
Everything below is based on public NVIDIA documentation and container catalog
metadata, not on running or benchmarking anything on a physical Jetson device.

## Goal

Evaluate what an *optional* Jetson-specific deployment profile would require,
layered on top of the generic ARM64 container image from #46, without ever
replacing the CPU-only baseline path.

## What a Jetson profile would look like

Jetson devices run L4T (Linux for Tegra), NVIDIA's board-specific OS/driver
stack, not stock Ubuntu. CUDA/cuDNN/TensorRT builds on Jetson are tied to the
L4T version (JetPack release), so a Jetson image cannot be "just" the generic
arm64 image plus `pip install onnxruntime-gpu` — it needs an L4T-matched base.

Current (as of JetPack 6, L4T r36.x) NVIDIA-published container layering:

- `nvcr.io/nvidia/l4t-base` — minimal L4T runtime (multimedia, core libs). No
  CUDA/TensorRT since r34.1+.
- `nvcr.io/nvidia/l4t-cuda` — L4T base + CUDA runtime/devel variants.
- `nvcr.io/nvidia/l4t-tensorrt` — built on `l4t-cuda`, adds TensorRT runtime.
- `nvcr.io/nvidia/l4t-jetpack` — full JetPack SDK (CUDA, cuDNN, TensorRT, VPI,
  multimedia) in one image; largest footprint.

A siqoq Jetson profile would be a **second, additive Dockerfile stage or
separate image tag** (e.g. `Dockerfile.jetson` or a multi-stage target
`jetson`), built `FROM nvcr.io/nvidia/l4t-tensorrt:<r36.x-tag>` (or
`l4t-cuda` if TensorRT isn't needed at the base layer), installing the siqoq
Python package on top and adding a TensorRT-backed inference adapter that
implements the same inference-runtime interface the CPU/ONNX Runtime adapter
implements today.

Sources: [NVIDIA L4T TensorRT — NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/l4t-tensorrt/-), [NVIDIA L4T Base — NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/l4t-base/-), [NVIDIA L4T JetPack — NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/l4t-jetpack/-), [jetson-containers build docs](https://github.com/dusty-nv/jetson-containers/blob/master/docs/build.md)

## Adapter/profile boundary vs. core code

Per `AGENTS.md`'s hardware-optionality principle, the following must stay
behind the adapter/profile boundary and must never leak into core code:

| Behind the boundary (profile-specific) | Stays in core |
|---|---|
| `Dockerfile.jetson` / jetson build target, base image pin (`l4t-*:r36.x`) | Generic ARM64/amd64 Dockerfile from #46 |
| TensorRT engine build/load, `.engine`/`.plan` artifact handling | Inference-runtime interface (input tensor contract, output → semantic event mapping) |
| CUDA/cuDNN/TensorRT version pinning tied to L4T release | ONNX Runtime baseline adapter (already runtime-agnostic) |
| Jetson-specific device queries (e.g. `jetson_clocks`, power mode, `tegrastats`) | Semantic event schema, event transport (NATS/MQTT), policy/action layers |
| Jetson-specific CI job (buildx target selection, or self-hosted Jetson runner if ever added) | Existing amd64/arm64 QEMU CI job from #46 |

Concretely: a new `JetsonTensorRTInferenceAdapter` (or similar) implements the
same interface as the existing ONNX Runtime adapter and is selected only by
explicit profile/config, never by default and never by branching on
architecture inside shared application code.

## Baseline CPU path when Jetson profile isn't selected

The generic ARM64 image from #46 remains the default arm64 artifact. The
Jetson profile is an opt-in, separately tagged image (e.g.
`siqoq:latest-arm64` vs. `siqoq:latest-jetson`) built from a distinct
Dockerfile/stage. Nothing in the default build, CI matrix, or runtime
adapter selection changes when the Jetson profile doesn't exist or isn't
built — the ONNX Runtime/CPU baseline continues to satisfy "must work on a
normal development laptop" and on generic arm64 hardware without any L4T
base image or CUDA/TensorRT dependency present.

## Licensing and footprint

- L4T container images bundle NVIDIA's proprietary Tegra binary blobs
  alongside Debian-style packaging; each image ships its own license terms
  rather than a single unified open-source license. Using them means
  accepting NVIDIA's L4T/JetPack container terms, distinct from the
  permissive/open licensing implied by a generic Debian/Ubuntu arm64 base.
- Images are large relative to the generic base: `l4t-base` alone bundles
  multimedia/Gstreamer/Vulkan/Weston components; `l4t-tensorrt` adds a full
  CUDA + TensorRT runtime on top; `l4t-jetpack` (full SDK) is larger still.
  This repo did not measure exact byte sizes (no registry pull was
  performed) — treat "multi-GB, meaningfully larger than the generic arm64
  image" as the planning assumption, not a verified number.
- Images are versioned per L4T/JetPack release (currently r36.x for JetPack
  6), so the Jetson profile would need its own version-pin and update
  cadence independent of the generic ARM64 image's OS/package updates.

Sources: [What Is NVIDIA L4T Base — Medium](https://rragesh.medium.com/what-is-nvidia-l4t-base-and-why-matters-for-robotics-on-jetson-28017b1a181a), [NVIDIA L4T Base — NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/l4t-base/-)

## Recommendation: adopt-later

- **Not do-not-adopt**: Jetson is named in `docs/architecture.md` as an
  important accelerated-inference target, and the adapter boundary needed to
  support it (swap-in TensorRT inference adapter) is compatible with the
  existing architecture without core changes.
- **Not adopt-now**: no Jetson hardware exists in this environment to build,
  boot, or verify against, so any Dockerfile/adapter written now would be
  untested against real L4T/CUDA/TensorRT behavior and would risk
  masquerading as verified when it isn't. The generic ARM64 image (#46) has
  not yet landed, and the Jetson profile depends on it existing first.
- Revisit once: (a) #46's generic ARM64 image build/CI is merged, and (b)
  either physical Jetson hardware or an NVIDIA-provided Jetson emulation
  path becomes available for actual boot/inference verification. Until
  then, this document is the design record; no `Dockerfile.jetson`, CUDA/
  TensorRT dependency, or CI job should be added.

## Explicit non-claim

No Jetson hardware verification, boot test, inference benchmark, or image
build against an L4T base has been performed in this repository as part of
this evaluation or any prior work. All statements above are derived from
NVIDIA's public NGC catalog pages and third-party documentation, not from
running anything on this repo's code.
