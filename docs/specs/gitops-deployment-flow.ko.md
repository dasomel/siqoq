# GitOps 배포 흐름 (플릿 규모) v0

상태: v0 (초안, 문서 전용). Phase 5 (이슈 #62, #10의 일부)에서 요구하는
플릿 규모 GitOps 흐름 제안을 문서화한다.

**이 저장소에는 GitOps 컨트롤러, 리컨실러, 클러스터가 구현되거나
검증된 바 없다.** 아래 내용은 지향할 패턴을 설명하는 것이며 동작하는
코드가 아니다. 여기 나오는 어떤 명령이나 파일 형태도 테스트된 것으로
취급하지 말 것 — `docs/specs/edge-deployment.md`가 자신의 절차를 다루는
방식과 같지만, 한 단계 더 추측적이다. 그 문서의 `docker` 명령은 지금
당장 실행 가능하지만, 이 문서의 리컨실러는 그렇지 않기 때문이다.

`docs/specs/edge-deployment.md`(#50)의 단일 노드 모델을 "한 명의
운영자가 한 대의 장치에서 `docker` 명령을 실행하는 것"에서 "여러 노드의
원하는 상태(desired state)가 Git에 있고, 운영자가 장치마다 직접 손대지
않고도 수렴(converge)하는 것"으로 확장한다. 그 문서를 대체하지는 않는다:
배포/롤백이 컨테이너에 실제로 수행하는 작업(digest 기준 pull, `siqoq
demo`를 통한 헬스체크, stop/start)에 대한 근본 진실은 여전히 단일 노드
절차다. 이 문서는 그 위에 "언제, 어떤 노드에 대해" 그 절차를 실행할지
결정하는 층만 추가한다.

## 범위

- Git을 통해 표현되는 플릿 규모 롤아웃/롤백과, 그 상태를 어떻게
  관찰 가능하게 만드는지.
- 리컨실러, 컨트롤러, 클러스터를 구현하지 않는다. ArgoCD, Flux 등
  특정 GitOps 도구를 강제하지 않는다.
- `docs/specs/edge-deployment.md`에 정의된 단일 노드 배포 메커니즘
  (digest 고정, 헬스체크, stop/start 시맨틱)은 변경하지 않고 노드 단위로
  그대로 재사용한다.
- 노드별 워크로드 스펙 파일의 정확한 스키마는 전제하되 정의하지 않는다.
  그 스키마는 형제 이슈인 declarative-workload-spec의 책임이다 (이
  워크트리에는 아직 존재하지 않을 수 있음). 여기서는 일반적으로
  "노드별 WorkloadSpec JSON 파일"이라고만 지칭한다.

## Desired-state 저장소

Git 저장소(또는 이 저장소 내의 한 디렉터리 — 이는 구현 세부사항일 뿐
설계 제약은 아니다)가 노드 또는 플릿 세그먼트별로 하나씩 선언적
WorkloadSpec 파일을 보관한다. 각 파일은 최소한 해당 노드가 실행해야
할 이미지 digest를 지정한다 — `docs/specs/edge-deployment.md`의
"Deployment artifact" 절에서 이미 정의된 digest 식별 방식과 동일하다:

```text
fleet/
  node-jetson-01.json   # WorkloadSpec: 이 노드가 실행해야 할 digest
  node-jetson-02.json
  segment-warehouse-a.json
```

Git이 원하는 상태(desired state)의 단일 진실 공급원이다. 노드의 실제
실행 중 digest는 런타임 사실이며, 단일 노드 롤백 절차에서 이미 사용하는
동일한 `docker inspect` 조회로 확인한다 — 절대 별도 경로로 직접 수정하지
않는다.

## 리컨실리에이션 모델

운영자 또는 컨트롤러 프로세스(여기서는 명시하지 않음 — 이는 구현이
아니라 패턴이다)가 다음을 담당한다:

1. 원하는 상태 읽기: 특정 노드의 Git상 WorkloadSpec 파일.
2. 실제 상태 읽기: 노드가 현재 실행 중인 이미지 digest.
3. 두 상태를 비교(diff).
4. 차이가 있으면 `docs/specs/edge-deployment.md`의 단일 노드 배포
   절차(digest로 pull, stop, start, 헬스체크)를 적용해 실제 상태를
   원하는 상태로 수렴시킨다.
5. 헬스체크가 실패하면 동일 문서의 단일 노드 롤백 절차를 적용한다.

이는 리컨실리에이션 *패턴*에 대한 설명이다 — pull 기반(노드/에이전트가
Git을 폴링)이든 push 기반(외부 프로세스가 노드에 push)이든 둘 다
호환되는 구현이며, 이 문서는 그 사이에서 입장을 취하지 않는다. 지금
컨트롤러를 선택할 필요는 없으며, 향후 구현될 컨트롤러가 Git을 원하는
상태로, 기존 단일 노드 절차를 노드의 실행 이미지를 바꾸는 유일한 승인된
방법으로 취급하기만 하면 된다.

## Git 연산으로서의 롤아웃과 롤백

- **롤아웃** = 노드(또는 세그먼트)의 WorkloadSpec 파일을 새 이미지
  digest로 바꾸는 Git 커밋. 커밋 메시지와 diff 자체가 변경 기록이며,
  무엇이 언제 누구에 의해 바뀌었는지 알기 위한 별도 배포 티켓이
  필요하지 않다.
- **롤백** = 그 커밋에 대한 Git revert(또는 이에 상응하는 감사 가능한
  되돌리기 연산)로, WorkloadSpec 파일의 이전 digest를 복원한다. 롤백은
  항상 desired-state 저장소에 대한 `git revert`여야 하며 — 장치에서의
  추적되지 않은 수동 편집이나 실행 중인 컨테이너에 대한 기록되지 않은
  변경이어서는 **절대** 안 된다. 이는 단일 노드 롤백 절차가 "이전에
  기록된 known-good digest로만 이동한다"는 요구사항을, 그 기록이
  운영자의 기억이나 셸 히스토리가 아니라 Git 히스토리에 있어야 한다는
  형태로 확장한 것이다.

두 연산 모두 desired-state 저장소에 대한 평범한 `git log` / `git show`로
완전히 감사 가능하다 — 단일 노드 문서의 "무언가 손대기 전에 현재 실행
중인 이미지의 digest를 기록한다"에 대응하는 플릿 규모 버전이며, 다만
그 기록이 한 번의 `docker inspect` 캡처가 아니라 Git 히스토리라는 점이
다르다.

## 관찰 가능성 훅 포인트

여기서 새 텔레메트리 코드를 제안하지 않는다. `src/siqoq/telemetry.py`는
실제 리컨실러가 통과시켜야 할 패턴을 이미 정의하고 있다:

- `start_span(name)` — 실제 리컨실러라면 각 리컨실리에이션 패스와 각
  노드별 수렴 단계를 스팬(예: `"gitops.reconcile"`,
  `"gitops.reconcile.node"`)으로 감쌀 것이다. perception-action 루프의
  각 단계를 이미 스팬으로 감싸는 방식과 동일하다.
- `get_events_emitted_counter()` 형태의 카운터 — 실제 리컨실러라면 기존
  `siqoq.events.emitted` 카운터의 형태를 따르는 자매 카운터(예:
  `siqoq.gitops.rollout.applied`, `siqoq.gitops.rollback.applied`)를
  추가할 것이다: 선택적이며, `observability` extra가 설치되지 않았을 때
  no-op이고, 노드/세그먼트 식별자로 속성이 부여된다.
- 두 방식 모두 `opentelemetry` extra 없이 no-op으로 저하되며, 이 코드
  베이스의 다른 모든 텔레메트리 훅과 일관된다 — GitOps 리컨실러는
  OpenTelemetry 설치를 강한 의존성으로 만들어서는 안 된다.

이들은 향후 구현을 위한 의도된 훅 포인트일 뿐, 이 문서가 추가하는 새
인터페이스가 아니다. 이 저장소의 어떤 코드도 현재 이를 실제로
방출하지 않는다.

## 명시적 범위 제외

- GitOps 컨트롤러, 리컨실러, 에이전트, 클러스터(Kubernetes/K3s 등)는
  이 저장소에서 구현되거나 검증되지 않았다. 위 내용은 모두 문서화된
  패턴일 뿐이다.
- 특정 GitOps 도구(ArgoCD, Flux 등)를 강제하지 않는다. 참조 구현으로
  하나를 명명하는 것은 향후 연구가 이를 강하게 지지할 경우로
  남겨둔다.
- WorkloadSpec 파일의 정확한 스키마 — 형제 이슈
  declarative-workload-spec의 소유.
- 단일 노드 배포/롤백 메커니즘 자체의 변경; 이는
  `docs/specs/edge-deployment.md`에 정의된 그대로 유지된다.
