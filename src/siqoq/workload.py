"""Declarative workload specification format (issue #58).

A `WorkloadSpec` names which scenario config to run (reusing `ScenarioConfig`
from `siqoq.scenario`, not reinventing it) plus the runtime capabilities
that must be `True` on the target node (checked against
`siqoq.capabilities.RuntimeCapabilities`, from `siqoq.capabilities.discover()`).
It does not require Kubernetes to author, validate, or run: it is a plain
JSON file plus a pure-data validation function.

See docs/specs/workload-spec.md for the format contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .capabilities import RuntimeCapabilities


@dataclass(slots=True, frozen=True)
class WorkloadSpec:
    """A portable, declarative unit of work.

    ``required_capabilities`` is a subset of `RuntimeCapabilities`' boolean
    fields that must be `True` on the target node (e.g.
    ``{"vision_extra_available": true}``). ``resource_hints`` is free-form
    and advisory only — it is never enforced by `validate_against`.
    """

    name: str
    scenario_config_path: str
    required_capabilities: dict[str, bool]
    resource_hints: dict[str, Any] | None = None

    @classmethod
    def from_json(cls, path: str | Path) -> WorkloadSpec:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            name=data["name"],
            scenario_config_path=data["scenario_config_path"],
            required_capabilities=data.get("required_capabilities", {}),
            resource_hints=data.get("resource_hints"),
        )

    def validate_against(self, capabilities: RuntimeCapabilities) -> list[str]:
        """Return human-readable reasons this spec is NOT satisfiable.

        An empty list means the spec is satisfiable on `capabilities`. Each
        `required_capabilities` key must name an existing
        `RuntimeCapabilities` field; an unknown key is itself reported as a
        reason (fail loud, not silently ignored).
        """
        known = capabilities.to_dict()
        reasons: list[str] = []
        for key, required_value in self.required_capabilities.items():
            if key not in known:
                reasons.append(
                    f"unknown required capability {key!r} (not a RuntimeCapabilities field)"
                )
                continue
            actual_value = known[key]
            if required_value and not actual_value:
                reasons.append(
                    f"required capability {key!r} is False on this node (needed: True)"
                )
            elif not required_value and actual_value:
                reasons.append(
                    f"required capability {key!r} is True on this node (needed: False)"
                )
        return reasons
