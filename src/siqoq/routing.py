"""Local-versus-cloud inference routing with an optional mock cloud adapter."""

from __future__ import annotations

from dataclasses import dataclass

from siqoq.inference import Detection, InferenceAdapter


@dataclass(frozen=True)
class RoutingPolicy:
    """Select where inference should run.

    ``cloud`` is an explicit selection and requires a cloud adapter. ``auto``
    uses a supplied cloud adapter when present, otherwise uses local inference.
    """

    mode: str = "local"

    def __post_init__(self) -> None:
        if self.mode not in {"local", "cloud", "auto"}:
            raise ValueError("routing mode must be one of: local, cloud, auto")


class MockCloudInferenceAdapter:
    """Stub-only cloud-shaped adapter; it performs no network access.

    This class exists only to exercise the cloud adapter interface shape. It
    returns a deterministic empty result and never imports or calls any
    networking library. A real cloud backend is explicitly out of scope for
    this issue and would require a future issue with network/dependency review.
    """

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        del frame, source
        return []


class InferenceRouter:
    """Route each frame to local or optional cloud inference.

    Local mode always uses the local adapter. Cloud mode requires an explicitly
    provided cloud adapter and raises rather than falling back when absent.
    Auto mode uses cloud only when a cloud adapter was explicitly provided;
    otherwise it falls back to local inference.
    """

    def __init__(
        self,
        local_adapter: InferenceAdapter,
        cloud_adapter: InferenceAdapter | None = None,
        *,
        policy: RoutingPolicy | None = None,
    ) -> None:
        self._local_adapter = local_adapter
        self._cloud_adapter = cloud_adapter
        self._policy = policy if policy is not None else RoutingPolicy()

    def infer(self, frame: object, *, source: str) -> list[Detection]:
        """Run inference using the adapter selected by the routing policy."""

        if self._policy.mode == "local":
            return self._local_adapter.infer(frame, source=source)
        if self._policy.mode == "cloud":
            if self._cloud_adapter is None:
                raise RuntimeError("cloud routing requires a cloud inference adapter")
            return self._cloud_adapter.infer(frame, source=source)
        if self._cloud_adapter is not None:
            return self._cloud_adapter.infer(frame, source=source)
        return self._local_adapter.infer(frame, source=source)
