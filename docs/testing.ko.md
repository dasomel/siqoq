# 테스트 방법

상태: v0. 아래 내용은 명시하지 않는 한 전부 하드웨어 불필요 경로입니다. `make verify`가
통과해도 카메라/디바이스, ONNX/TensorRT, NATS/MQTT, ROS 2, Kubernetes/K3s, 실제
액추에이터 동작을 증명하지는 않습니다(`AGENTS.md` 참고).

## 기본 검증 (CI와 동일)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
make install   # pip install -e '.[dev]'
make verify    # ruff check . && pytest && python -m build
```

개별 실행: `make lint`, `make test`, `make build`.

## 옵션 extra (vision / transport / observability)

기본 설치는 zero-dependency를 유지합니다(`pyproject.toml`의 `dependencies = []`).
`inference.py`의 ONNX/OpenCV 백엔드, `transport.py`의 NATS/MQTT 어댑터,
`telemetry.py`의 OpenTelemetry span/counter는 해당 extra가 설치되지 않으면
실제 백엔드 테스트를 스킵합니다.

```bash
make install-full   # pip install -e '.[dev,vision,transport,observability]'
make verify-full    # install-full 후 verify
```

## CLI로 직접 확인

```bash
siqoq demo                                                    # 생성/시뮬레이션 시나리오
siqoq scenario run --config examples/scenario.json            # fixture 기반 시나리오
siqoq scenario run --config examples/scenarios/scene_multi_step_sequence.json
siqoq capabilities                                            # 현재 노드의 RuntimeCapabilities
siqoq workload validate --spec examples/workloads/fixture_detection_workload.json
siqoq fleet list --inventory examples/fleet/inventory.jsonl
siqoq fleet query --inventory examples/fleet/inventory.jsonl --require vision_extra_available
siqoq fleet observe --results-dir examples/fleet/results
siqoq placement check --nodes examples/nodes.json --require vision_extra_available
siqoq skills list
siqoq skills classify --event-type object.detected
siqoq trace build --event-json <path> [--action-json <path>] [--include-metadata]
siqoq ui serve [--port 8000] [--fleet-inventory <path>] [--scenario-catalog <path>]
```

`trace build`는 기본적으로 이벤트 메타데이터를 리댁션합니다. 디버깅을 위해 원본
메타데이터가 정말 필요할 때만 `--include-metadata`를 명시적으로 붙이세요
(`docs/specs/decision-trace.md` 참고).

## 시뮬레이션 회귀 게이트

`tests/test_scenario_catalog.py`는 `examples/scenarios/catalog.json`의 모든
항목을 실행하고 각각의 `sequence_hash`/결과를 검증합니다. 항목 하나라도 실패하면
`pytest`가 실패하고, 이는 CI의 `test` 잡을 실패시킵니다 — Phase 6(#66)에서 언급된
"시뮬레이션 검증이 위험한 변경을 게이팅한다"는 요구사항이 바로 이 기존 메커니즘으로
충족되며, 별도의 게이팅 잡은 없고 필요하지도 않습니다.

## 컨테이너 빌드

```bash
make container              # docker buildx build --platform linux/amd64,linux/arm64 .
make container-run          # amd64 이미지를 빌드하고 그 안에서 `siqoq demo` 실행 (CI와 동일)
make container-run-native   # 현재 호스트 아키텍처로 빌드+실행, 에뮬레이션 없음
```

CI는 QEMU 에뮬레이션으로 두 아키텍처를 모두 빌드하지만, 실제 실행 테스트는
amd64만 합니다(`.github/workflows/ci.yml`의 `container` 잡과, arm64/Jetson이
왜 빌드까지만 머무는지는 `docs/evaluations/jetson-deployment-profile.md` 참고).
`container-run`은 CI와 동일하게 amd64를 강제하므로, arm64 호스트(예: Apple
Silicon)에서는 QEMU로 에뮬레이션되면서 `platform ... does not match the
detected host platform`이라는 무해한 경고가 출력됩니다. 로컬에서 반복 테스트할
때는 `container-run-native`를 쓰세요 — `uname -m`을 감지해서 해당 아키텍처로
바로 빌드/실행하므로 에뮬레이션 경고가 없습니다.

## 통과가 증명하는 것 / 증명하지 않는 것

| 명령 | 증명하는 것 | 증명하지 않는 것 |
|---|---|---|
| `make verify` | 린트 통과, 단위 테스트 통과, 패키지 빌드 성공 | 실제 하드웨어/디바이스/네트워크 경로 |
| `siqoq scenario run` | 결정론적 시뮬레이션/fixture 파이프라인 | 실제 카메라/추론/액추에이터 동작 |
| `make container` | 두 아키텍처 모두 이미지 빌드 성공 | 실제 ARM64 하드웨어에서의 정확성(QEMU 에뮬레이션만) |

하드웨어/엣지/시뮬레이션 관련 주장을 할 때는 어떤 경로를 실제로 실행했는지
`AGENTS.md`의 검증 섹션에 따라 명시하세요.
