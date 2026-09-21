# 스킬 카탈로그 v0

상태: v0 (`src/siqoq/skills.py`).

스킬 카탈로그는 기존 `SemanticEvent.type` 값(`docs/specs/semantic-event-contract.md`
참고)을 이름이 붙은 "스킬" — 런타임/에이전트가 자신이 처리할 수 있다고
알릴 수 있는 능력 — 에 매핑합니다. 이는 향후 스킬 기반 라우팅/에이전트
통합의 기반입니다 (이슈 #63, #11의 일부).

## 데이터 모델

```python
@dataclass(frozen=True, slots=True)
class SkillDefinition:
    name: str
    event_types: tuple[str, ...]
    description: str
```

- `name: str` — 스킬 식별자, 예: `"object-detection"`.
- `event_types: tuple[str, ...]` — 이 스킬이 처리하는 `SemanticEvent.type`
  값들.
- `description: str` — 사람이 읽을 수 있는 설명.

## 기본 카탈로그

`list_catalog()`는 기본 레지스트리를 반환합니다. 현재는 이 코드베이스
전체에서 생성되는 유일한 이벤트 타입(`SemanticEvent.detected()`는 항상
`type="object.detected"`를 설정)에 대응하는 항목 하나만 포함합니다.

```python
SkillDefinition(
    name="object-detection",
    event_types=("object.detected",),
    description="Detects and classifies objects in a frame",
)
```

여기서는 가상의 이벤트 타입을 만들어내지 않습니다. 새로운 스킬은 코드베이스
다른 곳에서 실제로 새로운 이벤트 타입이 도입될 때만 추가됩니다.

## 조회

```python
def classify(event: SemanticEvent) -> list[str]:
    ...
```

카탈로그 정의 순서대로, `event_types`에 `event.type`이 포함된 모든 카탈로그
스킬의 이름을 반환합니다. 일치하는 스킬이 없으면 빈 리스트를 반환합니다.
조회는 `event.type`과 정적 카탈로그 내용에만 의존하므로 결정적(deterministic)
입니다.

## CLI

```
siqoq skills list
siqoq skills classify --event-type object.detected
```

`list`는 카탈로그를 JSON으로 출력하고, `classify`는 일치하는 스킬 이름의
JSON 배열을 출력합니다 (일치하는 항목이 없으면 빈 배열 `[]`).

## 명시적 비목표 / 범위

- **이 카탈로그는 데이터이며, 새로운 이벤트 스키마가 아닙니다.**
  `SemanticEvent`의 어떤 필드도 추가·제거·이름 변경하지 않으며,
  `siqoq.events`의 `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, `SCHEMA_VERSION`도
  변경하지 않습니다. 카탈로그 항목을 추가/제거/수정하는 것은 데이터 변경이며
  스키마/계약 변경이 아닙니다.
- 라우팅, 디스패치, 에이전트 호출을 구현하지 않습니다 — "이 이벤트에 어떤
  스킬이 일치하는가"만 답하며, 그 답으로 무엇을 할지는 향후 작업으로
  남겨둡니다.
