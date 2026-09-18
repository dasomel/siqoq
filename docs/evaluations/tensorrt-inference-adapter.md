# Evaluation: TensorRT Inference Adapter Spike

Tracks: #48 (part of #8).

> **No TensorRT capability is implemented or verified anywhere in this repo.**
> No NVIDIA GPU is available in this environment. Everything below is
> desk research (NVIDIA docs + community reports as of 2026-09), not tested
> behavior.

## Goal

Evaluate what a `TensorRtInferenceAdapter` would need to implement the
existing `InferenceAdapter` protocol (`src/siqoq/inference.py`), analogous to
the existing `OnnxCvInferenceAdapter`, without adding code or dependencies.

## How it would fit the existing protocol

`InferenceAdapter` is a `Protocol` with one method:
`infer(self, frame: object, *, source: str) -> list[Detection]`. `Detection`
is a frozen dataclass of `object_name: str`, `confidence: float`,
`source: str` — no framework types leak into it.

`OnnxCvInferenceAdapter` establishes the pattern to copy:

- Deferred imports inside `__init__` (`import cv2`, `import onnxruntime`),
  with an `ImportError` re-raised as a clear "install the optional extra"
  message. Importing `inference.py` itself never requires the dependency;
  only instantiating the adapter does.
- Adapter owns preprocessing (`_preprocess`) and output parsing
  (`_parse_outputs`), converting whatever the backend returns into
  `Detection` objects before returning from `infer`.

A `TensorRtInferenceAdapter` would follow the same shape:

```python
class TensorRtInferenceAdapter:
    def __init__(self, engine_path: str | Path, *, input_size: tuple[int, int] = (224, 224)) -> None:
        try:
            import tensorrt as trt          # NVIDIA TensorRT Python bindings
            import pycuda.driver as cuda     # or cuda-python; needed for device buffers
        except ImportError as exc:
            raise ImportError(
                "TensorRtInferenceAdapter requires the 'tensorrt' extra: "
                "pip install -e '.[tensorrt]' (see docs/evaluations/tensorrt-inference-adapter.md "
                "for why this extra cannot be a plain pip dependency on most platforms)"
            ) from exc
        # load a pre-built serialized engine (.engine/.plan), NOT an ONNX
        # model directly (that's the trtexec/build step, out of scope here)
        ...

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        # 1. preprocess frame into the engine's expected input layout
        # 2. copy to GPU, run trt execution context, copy output back
        # 3. parse raw output tensors into Detection list (source-tagged)
        ...
```

Key difference from the ONNX adapter: TensorRT engines are **hardware- and
version-locked serialized artifacts** (built via `trtexec` or the builder API
against a specific TensorRT/CUDA/GPU-arch combination), not portable model
files you can just load anywhere. Engine build would need to be a separate,
explicitly out-of-repo-scope concern (a build step run on target hardware),
not something this adapter does at runtime.

## Dependency footprint

TensorRT is **not** a simple, always-installable pip package, unlike
`onnxruntime`/`opencv-python`:

- NVIDIA does publish `pip install tensorrt` wheels for x86_64 + certain CUDA
  versions, but pip wheels ship bindings/libraries only — no `trtexec`, and
  they require a matching CUDA toolkit already present on the machine.
- On Jetson/JetPack (the project's actual edge target per AGENTS.md), pip
  wheels for Tegra/ARM are not reliably published; TensorRT is normally
  installed as part of the JetPack SDK image itself (bundled with CUDA,
  cuDNN, and the OS), not via `pip install` at all. Community reports
  (NVIDIA developer forums) describe recurring friction getting `pip install
  tensorrt` to work on Jetson.
- Net effect: an optional `tensorrt` extra in `pyproject.toml` would install
  fine on some x86_64+CUDA dev boxes but likely fail or be irrelevant on the
  actual Jetson target, where TensorRT should instead come from the base
  JetPack image rather than pip.

This reinforces the existing pattern rather than breaking it: keep the
dependency **fully optional and lazily imported** (same as `vision` extra),
document that on Jetson the extra may be a no-op/unnecessary because
TensorRT is already system-provided, and never let `tensorrt`/`pycuda`
imports leak into `pyproject.toml`'s base install or into any module-level
import in `inference.py`.

## What must stay behind the adapter boundary

- No `tensorrt`, `pycuda`, or CUDA-specific types anywhere in `Detection` or
  in the `InferenceAdapter` protocol signature. `frame: object` and
  `list[Detection]` stay unchanged.
- No engine-build/`trtexec` invocation inside `infer()` — engine loading only
  loads a pre-built serialized artifact; building belongs to an offline
  hardware-specific step, not the runtime adapter.
- GPU memory / CUDA context lifecycle (device buffers, stream sync) stays
  entirely inside the adapter's private methods, same as `_preprocess` /
  `_parse_outputs` in `OnnxCvInferenceAdapter`.

## Recommendation: adopt-later

- **Not adopt-now**: no GPU/Jetson hardware available to build or verify an
  engine; the dependency story on the actual target (JetPack) is murky
  enough (bundled vs. pip) that any extra written today would be unverified
  guesswork.
- **Not do-not-adopt**: the existing `InferenceAdapter` protocol already
  accommodates this cleanly (same lazy-import, optional-extra pattern as
  `OnnxCvInferenceAdapter`); no protocol change is needed later, so there's
  no architectural reason to reject it outright.
- Revisit when either (a) Jetson hardware becomes available to verify actual
  install/engine-build/runtime behavior, or (b) a concrete performance need
  (ONNX Runtime too slow on target) justifies the added complexity.
