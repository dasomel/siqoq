# 웹 대시보드 v0

상태: v0.

## 범위

기존 siqoq 데이터를 JSON을 직접 파싱하지 않고 볼 수 있는 로컬 읽기 전용 웹
대시보드(`siqoq ui serve`)입니다. 표준 라이브러리(`http.server`)만 사용하며
기본 설치에 새 의존성을 추가하지 않습니다.

## 보여주는 것

전부 기존 모듈에서 실시간으로 가져온 값이며, 조작된 데이터는 없습니다:

- `capabilities` — 현재 프로세스의 `RuntimeCapabilities`(`siqoq.capabilities.discover()`)
- `skills` — 내장 스킬 카탈로그(`siqoq.skills.list_catalog()`)
- `fleet_inventory` — `--fleet-inventory`를 넘기면 해당 fleet inventory JSONL 파일의 항목들
- `fleet_observability` — `--fleet-results-dir`를 넘기면 그 디렉토리의 집계 결과
- `scenario_catalog` — `--scenario-catalog`를 넘기면 해당 카탈로그의 항목별 성공/실패

각 옵션 소스는 넘기지 않으면 `{"configured": false}`, 경로가 없으면
`{"configured": true, "available": false, "reason": ...}`을 반환합니다 —
데이터가 없는 상태를 조작된 값이나 빈 값처럼 오인하게 하지 않습니다.

## 엔드포인트

- `GET /` — `/api/snapshot`을 불러와 렌더링하는 HTML 페이지
- `GET /api/snapshot` — 전체 스냅샷을 JSON으로

둘 다 읽기 전용 `GET`이며, 이 모듈에는 쓰기 엔드포인트가 전혀 없습니다.

## 보안 경계

- 기본값은 `127.0.0.1`(로컬호스트)만 바인딩합니다(`--host`로 변경 가능).
  localhost 외부에 바인딩하는 것은 운영자의 명시적 선택입니다 — 이 모듈은
  인증을 추가하지 않으므로, localhost 밖으로 노출할 경우 리버스 프록시/인증
  계층을 앞에 두는 책임은 운영자에게 있으며 이 이슈의 범위 밖입니다.
- 비밀 정보는 제공하지 않습니다: `RuntimeCapabilities`는 불리언 플래그와
  OS/아키텍처뿐이고, 플릿/시나리오 데이터는 운영자가 이미 갖고 있으면서
  명시적으로 지정한 로컬 파일일 뿐입니다.

## 사용법

```bash
siqoq ui serve
siqoq ui serve --port 9000 --fleet-inventory examples/fleet/inventory.jsonl \
  --scenario-catalog examples/scenarios/catalog.json
```

## 호환성 규칙

오직 추가적(additive)입니다: 새 옵션 CLI 플래그와 새 모듈뿐입니다.
`SemanticEvent`, `RuntimeCapabilities`, `FleetInventory` 등 기존 계약을
절대 변경하지 않습니다. 이 스펙에서의 breaking change는 기존
대시보드/스크립트가 의존하는 스냅샷 키를 제거하거나 이름을 바꾸는 것입니다.
