# 선언적 워크로드 스펙 (이슈 #58)

상태: 구현됨 (`siqoq.workload.WorkloadSpec`).

워크로드 스펙은 노드에서 실행할 작업 단위 하나를 기술하는 작고 이동 가능한
선언적 JSON 문서다: 어떤 시나리오를 실행할지, 리소스 힌트, 그리고 노드가
갖춰야 하는 런타임 능력을 담는다. "무엇을 실행할지"는 `siqoq.scenario.ScenarioConfig`
(이슈 #24)를, "이 노드가 무엇을 할 수 있는지"는
`siqoq.capabilities.RuntimeCapabilities` (이슈 #45)를 그대로 재사용하며, 두
개념 모두를 위한 별도 형식을 새로 만들지 않는다.

워크로드 스펙을 작성/검증/실행하는 데 Kubernetes는 필요하지 않다: 평범한
JSON 파일로 작성되고, `siqoq` CLI 또는 `siqoq.workload` 모듈로 직접
검증/실행되며, `RuntimeCapabilities`가 일치하는 어떤 엣지 프로파일에서도
(원리상) 랩톱에서와 동일하게 동작한다.

## 필드

```python
@dataclass(slots=True, frozen=True)
class WorkloadSpec:
    name: str
    scenario_config_path: str
    required_capabilities: dict[str, bool]
    resource_hints: dict[str, Any] | None = None
```

- `name: str` — 워크로드를 식별하는 사람이 읽을 수 있는 이름.
- `scenario_config_path: str` — `ScenarioConfig` JSON 파일 경로
  (`docs/specs/scenario-fixtures.md` 참고). 주어진 그대로(현재 작업 디렉터리
  기준으로) 해석되며, `ScenarioConfig.from_json`의 관례를 그대로 따른다.
  워크로드 스펙은 시나리오 설정을 재발명하지 않는다.
- `required_capabilities: dict[str, bool]` — `RuntimeCapabilities.to_dict()`의
  불리언 키(예: `vision_extra_available`, `transport_nats_available`,
  `transport_mqtt_available`, `observability_extra_available`,
  `gpu_probe_tool_available`) 중 대상 노드에서 주어진 불리언 값과 일치해야
  하는 항목들의 부분집합. `RuntimeCapabilities`에 없는 키는 그 자체로
  불충족 사유로 보고되며, 결코 조용히 무시되지 않는다.
- `resource_hints: dict[str, Any] | None` — 자유 형식, 예:
  `{"min_memory_mb": 512}`. **참고용일 뿐**: 이 형식의 어떤 부분도 리소스
  힌트를 강제하지 않는다. 사람이나 향후 스케줄러가 읽도록 존재하며,
  `validate_against`가 검사하지 않는다.

## 예시

`examples/workloads/fixture_detection_workload.json`:

```json
{
  "name": "fixture-detection-laptop",
  "scenario_config_path": "examples/scenarios/fixture_detection.json",
  "required_capabilities": {
    "vision_extra_available": false
  },
  "resource_hints": {
    "min_memory_mb": 512
  }
}
```

## 검증

`WorkloadSpec.validate_against(capabilities: RuntimeCapabilities) -> list[str]`은
스펙이 충족 가능하면 빈 리스트를, 그렇지 않으면 불일치하거나 알 수 없는 키마다
하나씩 명시적이고 실행 가능한 사유를 담은 리스트를 반환한다 — 능력 불일치는
항상 명시된 사유이며, 조용한 무동작(no-op)이 아니다.

## CLI

```
siqoq workload validate --spec examples/workloads/fixture_detection_workload.json
```

stdout에 JSON을 출력한다. 예 (통과 사례, GPU/비전 확장이 없는 랩톱에서):

```json
{
  "name": "fixture-detection-laptop",
  "satisfiable": true,
  "reasons": []
}
```

실패 사례 (비전 확장이 설치되지 않은 노드에서 `vision_extra_available: true`를
요구하는 스펙):

```json
{
  "name": "needs-vision",
  "satisfiable": false,
  "reasons": [
    "required capability 'vision_extra_available' is False on this node (needed: True)"
  ]
}
```

## 호환성 규칙

- **호환성 파괴(Breaking)**: `WorkloadSpec` 필드 제거/이름 변경, 또는
  `validate_against`의 빈 리스트 의미 변경.
- **호환/추가(Compatible / additive)**: 기본값이 있는 새 선택적 필드 추가,
  또는 스펙이 참조할 수 있는 새 `RuntimeCapabilities` 필드 추가.

## 비목표 (이 이슈 범위 밖)

- 스케줄러, 노드 레지스트리, 능력 협상 프로토콜은 없다.
- `resource_hints`는 절대 강제되지 않는다.
- Kubernetes 매니페스트 생성은 없다.
