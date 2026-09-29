# 웹 대시보드 v0

상태: v0. 이제 페이지 내 설명, 한국어/English 다국어 지원, `/guide` 페이지가 추가되었습니다.

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

- `GET /` — 대시보드: `/api/snapshot`을 불러와 렌더링합니다
- `GET /guide` — "동작 흐름"을 설명하는 정적 페이지: 핵심 루프, 배포 모드,
  대시보드 섹션이 그 흐름에 어떻게 대응되는지를 인라인 SVG 다이어그램과 함께
  보여줍니다. 실시간 데이터는 없습니다
- `GET /api/snapshot` — 전체 스냅샷을 JSON으로
- `GET /assets/app.css`, `/assets/app.js`, `/assets/i18n.js` — 두 페이지가
  공유하는 정적 자산

모두 읽기 전용 `GET`이며, 이 모듈에는 쓰기 엔드포인트가 전혀 없습니다.
`/`, `/guide`, 세 개의 `/assets/*` 경로는 `ui.py`에 고정된 허용 목록
(`_PAGE_RESOURCES`/`_ASSET_RESOURCES`)입니다 — 요청 경로는 파일 시스템 경로가
아니라 딕셔너리 키 하나만 선택할 뿐이므로, 알 수 없는 경로나 `../` 형태의
경로 조작 시도는 항상 임의의 패키지 파일을 읽는 대신 `404`로 떨어집니다.

## 설명과 언어

각 대시보드 섹션에는 한 줄짜리 부제와, 더 자세한 정보를 위한 펼침형 "?"가
있습니다(무엇을 보여주는지, 어떤 CLI 플래그/모듈에서 읽는지, "가장 오래됨"이나
"error" 유형 시나리오의 통과처럼 값을 어떻게 읽어야 하는지) — 모두 실제로
그 섹션을 렌더링하는 모듈에 근거하며, 지어낸 내용은 없습니다.

헤더의 EN/한국어 토글은 `/assets/i18n.js`의 사전을 통해 모든 UI 문자열(뼈대,
라벨, 설명, 비어있음/오류 상태, 상대 시각)을 전환합니다. 데이터 값(노드
ID, 항목 ID, 상세 텍스트, 이벤트 유형)은 절대 번역하지 않습니다. 기본 언어는
`navigator.language`에서 결정되며(`ko`로 시작하지 않으면 English로 대체),
선택한 언어는 `localStorage`에 저장되고, `?lang=ko`/`?lang=en`으로 한 번의
로드에 한해 덮어쓸 수 있습니다.

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
`/guide`, `/assets/*`, i18n 사전은 추가적인 UI 전용 요소입니다: 새 데이터
소스나 새 의존성을 추가하지 않습니다(여전히 stdlib 전용, 오프라인, 외부
URL 없음).
