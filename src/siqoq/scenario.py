from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .policy import SafetyGate, decide
from .sensors import FixtureSensorAdapter, GeneratedSensorAdapter, SensorAdapter

#: Exception names the catalog runner is allowed to match on. Kept as an
#: explicit allowlist (not eval/getattr on arbitrary names) so a catalog file
#: can never be used to reference or construct an arbitrary type.
_KNOWN_ERROR_TYPES: dict[str, type[Exception]] = {
    "FileNotFoundError": FileNotFoundError,
    "ValueError": ValueError,
}


@dataclass(slots=True, frozen=True)
class ScenarioConfig:
    """Runtime configuration for a hardware-free scenario run.

    ``adapter`` selects the sensor source: "generated" for the synthetic demo
    behavior, or "fixture" to read recorded samples from ``source_path``.
    ``minimum_confidence``/``allow_mock_actions`` are forwarded to the mock
    policy gate so catalog scenarios can exercise the safety-gate-rejected
    path deterministically (see AGENTS.md: policy stays mock-only).
    """

    adapter: str
    steps: int
    source_path: str | None = None
    output_path: str | None = None
    minimum_confidence: float = 0.0
    allow_mock_actions: bool = True

    @classmethod
    def from_json(cls, path: str | Path) -> ScenarioConfig:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            adapter=data["adapter"],
            steps=data["steps"],
            source_path=data.get("source_path"),
            output_path=data.get("output_path"),
            minimum_confidence=data.get("minimum_confidence", 0.0),
            allow_mock_actions=data.get("allow_mock_actions", True),
        )

    def build_adapter(self) -> SensorAdapter:
        if self.adapter == "generated":
            return GeneratedSensorAdapter()
        if self.adapter == "fixture":
            if not self.source_path:
                raise ValueError("fixture adapter requires source_path")
            return FixtureSensorAdapter(path=Path(self.source_path))
        raise ValueError(f"unknown adapter: {self.adapter!r}")


@dataclass(slots=True, frozen=True)
class ScenarioSummary:
    event_count: int
    type_counts: dict[str, int]
    sequence_hash: str
    action_counts: dict[str, int]
    #: Coarse CI sanity signal only, not a benchmark measurement: wall-clock
    #: seconds for the whole run (adapter read + mock policy + optional
    #: output write). Varies with machine load, so never assert a tight bound
    #: on it in tests, only that it is a non-negative number.
    duration_seconds: float

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_count": self.event_count,
                "type_counts": self.type_counts,
                "sequence_hash": self.sequence_hash,
                "action_counts": self.action_counts,
                "duration_seconds": self.duration_seconds,
            },
            ensure_ascii=False,
            sort_keys=True,
        )


def _sequence_hash(payloads: list[str]) -> str:
    digest = hashlib.sha256()
    for payload in payloads:
        digest.update(payload.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def run_scenario(config: ScenarioConfig) -> ScenarioSummary:
    """Run a scenario end-to-end: read events, apply the mock policy, emit output.

    Writes each SemanticEvent as one JSONL line to ``config.output_path`` when
    set, and returns a machine-readable summary for regression assertions.
    """
    adapter = config.build_adapter()
    safety_gate = SafetyGate(allow_mock_actions=config.allow_mock_actions)
    payloads: list[str] = []
    type_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()

    output_handle = (
        Path(config.output_path).open("w", encoding="utf-8") if config.output_path else None
    )
    started = time.monotonic()
    try:
        for event in adapter.read(count=config.steps):
            action = decide(
                event,
                minimum_confidence=config.minimum_confidence,
                safety_gate=safety_gate,
            )
            action_counts[action.action] += 1
            payload = event.to_json()
            payloads.append(payload)
            type_counts[event.type] += 1
            if output_handle is not None:
                output_handle.write(payload + "\n")
    finally:
        if output_handle is not None:
            output_handle.close()
    duration_seconds = time.monotonic() - started

    return ScenarioSummary(
        event_count=len(payloads),
        type_counts=dict(type_counts),
        sequence_hash=_sequence_hash(payloads),
        action_counts=dict(action_counts),
        duration_seconds=duration_seconds,
    )


@dataclass(slots=True, frozen=True)
class CatalogEntry:
    """One row of the scenario/benchmark catalog (docs/specs/scenario-catalog.md).

    ``expected_outcome`` is "success" or "error". For "error", ``error_type``
    must name one of ``_KNOWN_ERROR_TYPES``. For "success", ``min_event_count``
    and/or ``expect_all_actions_rejected`` narrow what counts as a pass.
    """

    id: str
    description: str
    config_path: str
    expected_outcome: str
    min_event_count: int | None = None
    error_type: str | None = None
    expect_all_actions_rejected: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> CatalogEntry:
        return cls(
            id=data["id"],
            description=data["description"],
            config_path=data["config_path"],
            expected_outcome=data["expected_outcome"],
            min_event_count=data.get("min_event_count"),
            error_type=data.get("error_type"),
            expect_all_actions_rejected=data.get("expect_all_actions_rejected", False),
        )


@dataclass(slots=True, frozen=True)
class CatalogResult:
    entry_id: str
    passed: bool
    detail: str
    summary: ScenarioSummary | None


def load_catalog(path: str | Path) -> list[CatalogEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [CatalogEntry.from_dict(item) for item in data["scenarios"]]


def run_catalog_entry(entry: CatalogEntry, *, base_dir: str | Path) -> CatalogResult:
    """Run one catalog entry's scenario and check it against its expectation.

    ``base_dir`` resolves ``entry.config_path`` (catalog entries reference
    scenario config files by a path relative to the catalog file itself).
    """
    config_path = Path(base_dir) / entry.config_path
    config = ScenarioConfig.from_json(config_path)

    try:
        summary = run_scenario(config)
    except Exception as exc:  # noqa: BLE001 - re-classified against the catalog expectation below
        if entry.expected_outcome != "error":
            return CatalogResult(
                entry_id=entry.id,
                passed=False,
                detail=f"unexpected {type(exc).__name__}: {exc}",
                summary=None,
            )
        expected_type = _KNOWN_ERROR_TYPES.get(entry.error_type or "")
        if expected_type is None:
            return CatalogResult(
                entry_id=entry.id,
                passed=False,
                detail=f"catalog entry names unknown error_type {entry.error_type!r}",
                summary=None,
            )
        if not isinstance(exc, expected_type):
            return CatalogResult(
                entry_id=entry.id,
                passed=False,
                detail=f"expected {expected_type.__name__}, got {type(exc).__name__}: {exc}",
                summary=None,
            )
        return CatalogResult(entry_id=entry.id, passed=True, detail=str(exc), summary=None)

    if entry.expected_outcome != "success":
        return CatalogResult(
            entry_id=entry.id,
            passed=False,
            detail=f"expected outcome {entry.expected_outcome!r} but scenario succeeded",
            summary=summary,
        )
    if entry.min_event_count is not None and summary.event_count < entry.min_event_count:
        return CatalogResult(
            entry_id=entry.id,
            passed=False,
            detail=f"expected >= {entry.min_event_count} events, got {summary.event_count}",
            summary=summary,
        )
    if entry.expect_all_actions_rejected:
        non_noop = {
            action: count for action, count in summary.action_counts.items() if action != "noop"
        }
        if non_noop:
            return CatalogResult(
                entry_id=entry.id,
                passed=False,
                detail=f"expected all actions rejected (noop), got {non_noop}",
                summary=summary,
            )
    return CatalogResult(entry_id=entry.id, passed=True, detail="ok", summary=summary)
