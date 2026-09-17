# Scenario and benchmark catalog / 시나리오·벤치마크 카탈로그

Implements the reproducible-demonstration goal of issue #20. The catalog is a
small JSON manifest listing named scenarios; each scenario is an existing
`ScenarioConfig` file (see `docs/specs/scenario-fixtures.md`) plus an
expected outcome. A pytest-based runner executes the whole catalog and
reports pass/fail per scenario, so results are both human-readable test
output and machine-readable via `ScenarioSummary.to_json()`.

이슈 #20의 "재현 가능한 시나리오/벤치마크 카탈로그" 목표를 구현한다. 카탈로그는
이름이 있는 시나리오 목록을 담은 작은 JSON 매니페스트이며, 각 시나리오는 기존
`ScenarioConfig` 파일(`docs/specs/scenario-fixtures.md` 참고)과 기대 결과로
구성된다. pytest 기반 러너가 카탈로그 전체를 실행하고 시나리오별 pass/fail을
보고하므로, 결과는 사람이 읽을 수 있는 테스트 출력과 `ScenarioSummary.to_json()`을
통한 기계 판독 가능한 형태를 모두 가진다.

## Catalog format / 카탈로그 형식

`examples/scenarios/catalog.json`:

```json
{
  "scenarios": [
    {
      "id": "recorded-video-detection",
      "description": "...",
      "config_path": "fixture_detection.json",
      "expected_outcome": "success",
      "min_event_count": 3
    }
  ]
}
```

- `config_path` is resolved relative to the catalog file's own directory
  (`examples/scenarios/`), and that file is a normal `ScenarioConfig` JSON
  document.
  `config_path`는 카탈로그 파일이 위치한 디렉터리(`examples/scenarios/`)를
  기준으로 해석되며, 해당 파일은 일반적인 `ScenarioConfig` JSON 문서다.
- `expected_outcome` is `"success"` or `"error"`.
  `expected_outcome`은 `"success"` 또는 `"error"`다.
- For `"error"`, `error_type` must be one of the runner's known exception
  names (`FileNotFoundError`, `ValueError`) — an explicit allowlist, never an
  arbitrary type reference from catalog data.
  `"error"`인 경우 `error_type`은 러너가 알고 있는 예외 이름(`FileNotFoundError`,
  `ValueError`) 중 하나여야 한다. 카탈로그 데이터로부터 임의 타입을 참조하지 않는
  명시적 허용 목록이다.
- For `"success"`, `min_event_count` and/or `expect_all_actions_rejected`
  narrow the pass condition.
  `"success"`인 경우 `min_event_count`, `expect_all_actions_rejected`로 통과
  조건을 좁힐 수 있다.

## Implemented scenarios / 구현된 시나리오

All five run hardware-free and deterministically, satisfying issue #20's "at
least 3 deterministic scenarios runnable without hardware" acceptance
criterion:

다섯 개 모두 하드웨어 없이 결정론적으로 실행되며, 이슈 #20의 "하드웨어 없이
실행 가능한 결정론적 시나리오 최소 3개" 인수 조건을 만족한다.

| id | Stands in for / 대응하는 시나리오 | Outcome |
|---|---|---|
| `recorded-video-detection` | recorded video person/object detection | success, >= 3 events |
| `simulated-camera-detection` | simulated camera producing the same contract | success, >= 3 events |
| `sensor-disconnect` | sensor disconnect (missing fixture source) | error: `FileNotFoundError` |
| `inference-fallback-on-bad-input` | inference timeout/fallback (malformed input surfaces a clear error instead of a fabricated detection) | error: `ValueError` |
| `action-rejected-by-safety-gate` | action request rejected by safety gate | success, all actions `noop` |

`sensor-disconnect` and `inference-fallback-on-bad-input` are proxies built on
the existing fixture-validation error path (`sensors.py`'s
`SensorSample.from_record`), not a live reconnect/timeout harness — there is
no long-running sensor connection or inference call to time out yet. They
verify the same required property (a clear, typed error instead of
fabricated events) without inventing infrastructure this codebase does not
have.

`sensor-disconnect`와 `inference-fallback-on-bad-input`은 실시간 재연결/타임아웃
하네스가 아니라 기존 픽스처 검증 오류 경로(`sensors.py`의
`SensorSample.from_record`)를 이용한 대체 시나리오다. 아직 타임아웃될 수 있는
장시간 센서 연결이나 추론 호출이 존재하지 않기 때문이다. 존재하지 않는 인프라를
가정하지 않고, 같은 필수 속성(허구 이벤트 대신 명확한 타입의 오류)을 검증한다.

## Metrics captured / 수집하는 지표

Only what is measurable hardware-free and deterministically in CI:

CI에서 하드웨어 없이 결정론적으로 측정 가능한 지표만 수집한다:

- `event_count`, `type_counts`, `sequence_hash` — existing, unchanged.
  기존 지표(변경 없음).
- `action_counts` — new: how many times each mock policy action (e.g.
  `log_detection`, `noop`) was decided, letting a scenario assert that a
  safety gate rejected every action.
  신규: 모의 정책 액션(`log_detection`, `noop` 등)이 결정된 횟수. 안전 게이트가
  모든 액션을 거부했는지 검증하는 데 사용한다.
- `duration_seconds` — new: coarse wall-clock time for the whole run
  (adapter read + policy decision + optional output write). This is a **CI
  sanity signal, not a benchmark claim** — it is not isolated per stage and
  varies with machine load, so no test asserts a tight bound on it.
  신규: 전체 실행의 대략적인 실측 시간(어댑터 읽기 + 정책 결정 + 선택적 출력
  쓰기). **CI 정합성 신호일 뿐 벤치마크 주장은 아니다.** 단계별로 분리되어
  있지 않고 머신 부하에 따라 달라지므로, 어떤 테스트도 이 값에 엄격한 상한을
  단언하지 않는다.

### Deferred metrics / 보류된 지표

Not implemented — they require infrastructure this repository does not yet
have, or would require fabricating numbers that vary non-deterministically:

미구현 — 아직 존재하지 않는 인프라가 필요하거나, 비결정적으로 변동하는 값을
지어내야 하는 지표들이다:

- Inference latency/FPS, end-to-end latency, action decision latency as
  timed benchmark numbers (only the coarse `duration_seconds` sanity signal
  above is provided).
  추론 지연/FPS, 종단 지연, 액션 결정 지연의 벤치마크 수치(위의 대략적인
  `duration_seconds` 신호만 제공).
- Event loss/duplication under real reconnect conditions, reconnect/recovery
  time — require a live, interruptible sensor connection.
  실제 재연결 상황에서의 이벤트 손실/중복, 재연결·복구 시간 — 실시간으로
  중단 가능한 센서 연결이 필요하다.
- Resource usage (CPU/GPU/memory) — deferred until a profiling harness
  exists.
  리소스 사용량(CPU/GPU/메모리) — 프로파일링 하네스가 마련될 때까지 보류.

## Planned, not yet runnable / 계획됨, 아직 실행 불가

Per AGENTS.md's anti-premature-hardware-hardening principle, the following
issue #20 scenarios are explicitly **not** implemented here because they
need real hardware this repository does not assume access to. No benchmark
numbers are fabricated for them.

AGENTS.md의 성급한 하드웨어 고정 방지 원칙에 따라, 다음 이슈 #20 시나리오는
이 저장소가 접근을 가정하지 않는 실제 하드웨어가 필요하므로 여기서 구현하지
않는다. 이 항목들에 대한 벤치마크 수치는 조작하지 않는다.

- Webcam detection with semantic-event output (needs a physical webcam).
  웹캠 탐지(실제 웹캠 필요).
- Laptop CPU vs. Jetson accelerated inference comparison (needs Jetson
  hardware; see `docs/maturity-tiers.md` S3).
  랩톱 CPU 대 Jetson 가속 추론 비교(Jetson 하드웨어 필요, `docs/maturity-tiers.md`
  S3 참고).

Both are expected to become runnable once the `vision` extra's
`OnnxCvInferenceAdapter` (see `src/siqoq/inference.py`) has a real model and
device to target, and should reuse this same catalog format at that point.

`vision` 확장의 `OnnxCvInferenceAdapter`(`src/siqoq/inference.py` 참고)가
실제 모델과 대상 디바이스를 갖추면 실행 가능해질 것으로 예상되며, 그 시점에도
동일한 카탈로그 형식을 재사용해야 한다.

## Running the catalog / 카탈로그 실행

```console
pytest tests/test_scenario_catalog.py -v
```

Each catalog entry is one parametrized test case; `pytest`'s per-test
pass/fail output is the report. A CI fast-subset regression gate (issue
#20's "CI can use a fast subset as regression gates" criterion) can select a
subset with `pytest tests/test_scenario_catalog.py -k "..."`; all entries
here already run in well under a second, so no subsetting is currently
required.

각 카탈로그 항목은 하나의 파라미터화된 테스트 케이스이며, `pytest`의 테스트별
pass/fail 출력이 곧 보고서다. CI 빠른 하위 집합 회귀 게이트(이슈 #20의 "CI는
빠른 하위 집합을 회귀 게이트로 사용할 수 있어야 한다" 기준)가 필요하면
`pytest tests/test_scenario_catalog.py -k "..."`로 부분 선택할 수 있다. 현재
모든 항목이 1초 미만으로 실행되므로 별도의 부분 집합 구성은 필요하지 않다.
