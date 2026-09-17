# 액션 계약 v0

상태: v0 (`siqoq.policy`의 `CONTRACT_VERSION = 0`).

`MockAction`은 `siqoq.policy.decide()`의 출력이며, 정책/결정 로직과 액션
어댑터 사이의 경계입니다 (`docs/architecture.md`의 "액션 어댑터" 참고).

## 필드

```python
@dataclass(slots=True, frozen=True)
class MockAction:
    action: str
    event_type: str
    mock: bool = True
```

- `action: str` — 결정된 액션 이름 (`"log_detection"`, `"noop"`, 또는
  `_ACTION_BY_TYPE`에 추가될 향후 값들).
- `event_type: str` — 이 결정을 만들어낸 `SemanticEvent.type`.
- `mock: bool` — **안전에 민감한 필드, 명시적으로 검토됨** (아래 참고).

## 안전성 검토 (명시적)

AGENTS.md의 규칙("액추에이터 동작은 설계 변경 사항으로 취급한다")에서
요구하는 명시적인 안전성 검토입니다:

- `mock`은 기본값이 `True`이며, 이 계약 버전 기준으로 코드베이스 어디에서도
  `False`로 설정되지 않습니다. `decide()`는 `SemanticEvent.type`/
  `confidence`와 선택적 `SafetyGate`에 대한 순수 함수이며, `siqoq.policy`
  안이나 그로부터 도달 가능한 곳에 액추에이터 클라이언트, 네트워크 호출,
  GPIO/릴레이/모터 드라이버가 전혀 존재하지 않습니다 (grep으로 검증
  가능: 이 모듈에는 하드웨어/액추에이터 SDK의 `import`가 없습니다).
- `SafetyGate.approve()`가 권위 있는 게이트입니다: 오직 액션을
  `_DEFAULT_ACTION`("noop")으로 낮출 수만 있으며, `mock`을 올리거나
  우회하는 코드 경로는 없습니다.
- **검토 결론**: 이 계약의 v0은 구조적으로 어떤 배포 환경에서도
  안전합니다 — `decide()`의 출력에서 실제 액추에이터로 이어지는 실행
  경로가 존재하지 않습니다. `MockAction`을 소비해 실제 하드웨어를 구동하는
  향후 어댑터, 또는 `decide()`가 `mock=False`를 허용하도록 하는 변경은
  여기서 명시적으로 breaking하고 고위험(high-risk)한 설계 변경으로
  선언되며, 병합 전에 별도의 안전성 검토, 테스트, AGENTS.md 수준의 승인이
  필요합니다 — `decide()`/`MockAction`이 조용히 흡수해서는 안 됩니다.

## 호환성 규칙

- **호환성 파괴 (Breaking, `CONTRACT_VERSION` 증가 필요)**: `MockAction`
  필드 제거/이름 변경, `mock`의 기본값 변경 또는 `decide()`가 `False`를
  반환하도록 허용하는 변경, `decide()`의 파라미터 계약 변경(예:
  `minimum_confidence`/`safety_gate` 제거).
- **호환/추가적 (Additive, 증가 불필요)**: 기본값이 있는 새 선택
  `MockAction` 필드 추가, `_ACTION_BY_TYPE`에 새 매핑 추가, `decide()`에
  새로운 선택 키워드 파라미터 추가.

## Conformance

`decide()`는 결정적이고 순수한 함수입니다 (동일한 `SemanticEvent`와
파라미터 -> 동일한 `MockAction`). 이는 기존 `tests/test_policy.py`로
검증되며, `sensors.py`/`events.py`에 적용된 것과 동일한 "벤더/액추에이터
타입 부재" 검사로도 뒷받침됩니다.
