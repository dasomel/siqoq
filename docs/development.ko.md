# Siqoq 개발 가이드

[English](development.md) | **한국어**

## 개발 환경 기본 원칙

초기 개발 경험은 macOS와 Linux 노트북을 기준으로 하며 Jetson, GPU, 카메라, 로봇을 필수 요구사항으로 두지 않습니다.

### 기본 요구사항

- Python 3.12+
- Git
- 선택: Docker 또는 Podman

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
siqoq demo
siqoq inspect
```

`siqoq demo`는 generated sensor → static inference → semantic event → no-op policy → mock-safe action path를 실행합니다. 카메라나 accelerator가 필요하지 않습니다.

`siqoq inspect`는 vendor SDK 없이 현재 runtime manifest와 기본 host capability를 출력합니다.

## 현재 스켈레톤 경계

```text
GeneratedSensor
      ↓
StaticInference
      ↓
SemanticEvent
      ↓
MemoryTransport
      ↓
NoOpPolicy
      ↓
AllowListSafetyGate
      ↓
MockActionAdapter
```

이 구조는 최종 구현을 미리 확정한 것이 아니라 recorded video, webcam, ONNX Runtime, NATS/MQTT, simulator, Jetson/TensorRT, physical action adapter를 순차적으로 붙이기 위한 실행 가능한 seam입니다.

## 개발 순서

1. 작업할 GitHub Issue를 선택하거나 먼저 작성합니다.
2. 바로 코드를 수정하지 않고 관련 architecture, contract, 기존 구현과 test를 확인합니다.
3. 가장 작은 단위의 coherent change를 구현합니다.
4. 정상 경로뿐 아니라 failure path에 대한 test를 추가합니다.
5. interface/behavior가 바뀌면 영문 문서를 먼저 또는 함께 수정하고 한국어 문서를 동기화합니다.
6. local checks를 실행합니다.
7. issue와 연결된 작은 PR을 만듭니다.

## 기본 검사

```bash
ruff check .
pytest
python -m build
siqoq demo
siqoq inspect
```

## 저장소 구조

```text
src/siqoq/
  contracts.py      vendor-neutral data/protocol contract
  events.py         semantic-event envelope
  adapters.py       generated/mock adapter
  pipeline.py       perception-to-action composition
  runtime.py        runtime manifest/capability bootstrap
  cli.py            local CLI
examples/           실행 가능한 예제
docs/               설계/운영/개발 문서
.github/             CI 및 contributor automation
tests/               자동화 테스트
```

구현이 커지기 전에는 디렉터리 구조를 미래 아키텍처에 맞춰 과도하게 쪼개지 않습니다. 실제 adapter와 runtime 경계가 검증되면 package 구조를 단계적으로 확장합니다.

## Adapter 원칙

hardware/vendor/simulator 의존성은 가능한 한 adapter 뒤에 둡니다.

새 hardware 기능은 최소 하나를 함께 제공해야 합니다.

- simulator implementation
- fake/mock implementation
- recorded test fixture

이 원칙으로 일반 CI와 contributor 개발 환경을 실제 장비로부터 분리합니다.

## Contract-first 변경

Sensor Sample, Semantic Event, Action Request 같은 공통 계약을 변경할 때는 다음을 확인합니다.

- backward compatibility 필요 여부
- schema versioning
- simulator/real adapter 영향
- observability field 영향
- raw sensitive data가 event에 불필요하게 포함되는지 여부

## Physical Action 관련 개발

실제 actuator를 제어하는 코드는 일반 feature보다 보수적으로 다룹니다.

- 기본값은 mock/no-op 또는 safe state
- 명시적 opt-in 없이 physical action 금지
- timeout과 input validation
- 가능한 경우 allow-list/range limit
- action request/result telemetry
- 실제 장비가 없어도 검증할 test path 제공

현재 skeleton 역시 `NoOpPolicy`와 빈 allow-list를 기본으로 사용해 **명시적으로 허용하지 않은 action은 실행되지 않도록** 구성되어 있습니다.

## 문서 언어 정책

핵심 문서는 **English + 한국어**를 함께 유지합니다.

- `README.md` ↔ `README.ko.md`
- `docs/vision.md` ↔ `docs/vision.ko.md`
- `docs/architecture.md` ↔ `docs/architecture.ko.md`
- `docs/roadmap.md` ↔ `docs/roadmap.ko.md`
- `docs/development.md` ↔ `docs/development.ko.md`
- `docs/specs/README.md` ↔ `docs/specs/README.ko.md`

영문 문서는 국제 OSS 사용자를 위한 canonical technical description으로 사용하고, 한국어 문서는 단순 직역보다 이해하기 쉬운 설명을 허용합니다. 다만 architecture contract와 명령어, 버전, 기능 상태는 두 문서가 서로 모순되지 않아야 합니다.

## AI Coding Tools

AI coding assistant 사용을 허용하지만 contributor가 correctness, license, security, tests에 대한 책임을 가집니다. secret, proprietary code, 출처가 불명확한 대량 생성 asset을 commit하지 않습니다.

AI 도구가 생성한 변경도 일반 변경과 동일하게 issue 분석 → test → documentation → review 절차를 따릅니다.
