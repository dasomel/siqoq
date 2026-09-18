# 엣지 배포와 롤백 v0

상태: v0 (초안). Phase 3(이슈 #50, #8의 일부)가 요구하는 배포 번들 형식과
단일 노드 배포/롤백 절차를 문서화한다.

ARM64 컨테이너 빌드(이슈 #46, 작성 시점에 아직 머지되지 않음 — 이 문서는
이 워크트리에 이미 존재하는 이미지가 아니라, 앞으로 생성될 산출물을
가리킨다)를 기반으로 한다. 플릿/오케스트레이션 메커니즘은 구현하지
**않는다**. 그것은 명확히 Phase 5 / 이슈 #10의 범위이며, AGENTS.md의
성급한 하드웨어/플릿 고정 방지 원칙에 따라 이 문서의 범위에서 제외한다.

## 범위

- 단일 엣지 디바이스만 다룬다. 플릿 매니저, Kubernetes/K3s, GitOps 없음.
- 다루는 내용: 배포 아티팩트 식별, 재현 가능한 빌드, 배포 절차, 헬스체크,
  롤백 절차.
- 다루지 않는 내용: 다중 노드 롤아웃, 선언적 플릿 스펙, 워크로드 배치 등
  Phase 5(#10)의 범위 전부.

## 배포 아티팩트

배포 단위는 이슈 #46의 Dockerfile과 CI 잡(`docker buildx build --platform
linux/amd64,linux/arm64 .`을 사용하는 멀티스테이지 빌드)이 생성하는
컨테이너 이미지다.

배포된 이미지는 가변적인 태그가 아니라 **콘텐츠 다이제스트**로 식별한다:

```bash
docker pull ghcr.io/dasomel/siqoq@sha256:<digest>
```

`latest`나 `edge` 같은 태그는 현재 권장 빌드를 가리키는 편의용 레이블로
사용할 수는 있지만, 배포/롤백 단계가 고정할 수 있는 유일한 식별자는
다이제스트뿐이다 — 태그는 실행 중인 디바이스 아래에서 움직일 수 있지만
다이제스트는 그렇지 않다.

각 이미지는 사람이 읽을 수 있는 추적성을 위해 `pyproject.toml`의 패키지
버전(현재 `version = "0.1.0.dev0"`)도 OCI 레이블로 함께 담는다:

```dockerfile
LABEL org.opencontainers.image.version="0.1.0.dev0"
```

다이제스트가 주어지면 정확한 소스 커밋과 패키지 버전은 항상 이미지 자체의
메타데이터에서 복원 가능하다 — 별도의 외부 매핑 테이블이 필요 없다.

## 재현 가능한 빌드

같은 소스 커밋은 항상 같은 이미지 콘텐츠를 만들어야 한다:

- Dockerfile은 (`python:3.12-slim` 같은 유동적인 태그가 아니라) 정확한
  베이스 이미지 다이제스트를 고정하여, 베이스 레이어가 빌드 간에 조용히
  바뀌지 않도록 한다.
- 애플리케이션 의존성은 고정되지 않은 범위의 `pip install`이 아니라
  `pyproject.toml`/그 락파일에 고정된 버전으로 설치한다.
- 빌드는 이슈 #46의 CI 잡(buildx, QEMU로 에뮬레이션된 arm64)을 표준 빌드
  경로로 사용한다. 동일 커밋과 동일 베이스 다이제스트에 대해 로컬
  `docker buildx build`를 실행하면 같은 콘텐츠가 재현된다.

이로써 소스 커밋 -> 결정론적 이미지 콘텐츠 -> 콘텐츠 다이제스트라는
검증 가능한 체인이 만들어진다. 동일 커밋을 동일 베이스에 대해 두 번
빌드하면 같은 다이제스트가 나와야 한다. 그렇지 않다면 이는 예상된 변동이
아니라 빌드 재현성 버그다.

## 배포 절차 (단일 디바이스)

플릿 매니저나 Kubernetes는 전혀 관여하지 않는다 — 한 엣지 디바이스에서
실행하는 단순한 `docker`/`podman` 시퀀스다.

1. 대상 이미지를 다이제스트로 pull한다:

   ```bash
   docker pull ghcr.io/dasomel/siqoq@sha256:<new-digest>
   ```

2. 아무것도 건드리기 전에 현재 실행 중인 이미지의 다이제스트를 기록한다
   (롤백에 필요):

   ```bash
   docker inspect --format '{{.Image}}' siqoq-runtime
   ```

3. 현재 실행 중인 컨테이너를 중지한다:

   ```bash
   docker stop siqoq-runtime
   ```

4. pull한 다이제스트로 새 컨테이너를 시작한다:

   ```bash
   docker run -d --name siqoq-runtime ghcr.io/dasomel/siqoq@sha256:<new-digest>
   ```

5. 패키지 자체의 데모 진입점을 실행하고 종료 코드를 확인하여 새
   컨테이너를 헬스체크한다:

   ```bash
   docker exec siqoq-runtime siqoq demo
   echo "exit code: $?"
   ```

   종료 코드 `0`만이 통과 조건이다. 데모 경로는 하드웨어 없이 동작하므로
   (`docs/development.md` 참고), 연결된 센서와 무관하게 어떤 엣지
   디바이스에서도 이 체크는 유효하다.

헬스체크를 통과하면 배포가 완료된다. 실패하면 디바이스에서 직접 디버깅하지
말고 아래 롤백 절차로 진행한다.

## 롤백 절차

롤백에는 이전 이미지 다이제스트가 이미 사용 가능해야 한다. 로컬에 캐시되어
있거나 레지스트리에서 pull 가능해야 한다:

```bash
docker pull ghcr.io/dasomel/siqoq@sha256:<previous-digest>
```

위 5단계의 헬스체크가 실패한 경우의 단계:

1. 실패한 컨테이너를 중지한다:

   ```bash
   docker stop siqoq-runtime
   docker rm siqoq-runtime
   ```

2. (배포 절차 2단계에서 기록했거나 배포 이력/로그에서 확인한) 이전
   정상 작동 다이제스트로 컨테이너를 시작한다:

   ```bash
   docker run -d --name siqoq-runtime ghcr.io/dasomel/siqoq@sha256:<previous-digest>
   ```

3. 동일한 헬스체크를 다시 실행한다:

   ```bash
   docker exec siqoq-runtime siqoq demo
   echo "exit code: $?"
   ```

디바이스 운영자는 항상 현재와 이전 다이제스트를 최소한 로컬에 pull해
두어야 한다. 그래야 롤백이 필요한 순간에 레지스트리 가용성에 의존하지
않는다.

## 명시적으로 범위 밖

- 플릿 매니저, K3s/Kubernetes 배포, GitOps 플로우 — Phase 5 / 이슈 #10에서
  추적한다.
- Jetson 전용 베이스 이미지나 CUDA 레이어 — 이슈 #46이나 이 문서에서
  도입하지 않는, 별도의 Jetson 배포 프로필이다.
- 자동/무인 롤백 트리거 — 여기의 헬스체크는 감독 프로세스가 아니라
  운영자가 직접 실행하는 수동 게이트다.
