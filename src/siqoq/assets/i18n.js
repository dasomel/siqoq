/* Shared Korean/English dictionary + tiny translation engine for the siqoq
 * dashboard (/) and guide (/guide) pages. Served as a static asset at
 * /assets/i18n.js (see ui.py's route allowlist).
 *
 * The DICT literal below is deliberately valid JSON (double-quoted keys and
 * values, no comments, no trailing commas) so tests/test_ui.py can extract
 * it with a regex + json.loads and assert the "en" and "ko" key sets match
 * exactly, without needing a JS parser. Keep it that way when editing.
 */
var DICT = {
  "en": {
    "app.badge": "read-only · local",
    "nav.dashboard": "Dashboard",
    "nav.guide": "Guide",
    "nav.aria": "Primary",
    "skip.link": "Skip to main content",
    "lang.aria": "Language",
    "lang.en": "EN",
    "lang.ko": "한국어",
    "header.hostPrefix": "host: ",
    "header.hostDetecting": "detecting…",
    "header.updatedNotLoaded": "not loaded yet",
    "header.updatedPrefix": "updated ",
    "header.autoRefresh": "auto-refresh",
    "header.refresh": "Refresh",
    "header.intervalAria": "auto-refresh interval",
    "header.interval15": "15s",
    "header.interval30": "30s",
    "header.interval60": "60s",
    "common.moreInfoLabel": "More information",
    "common.retry": "Retry",
    "common.enableWith": "Enable with: ",
    "common.errorFetchPrefix": "Could not reach this dashboard's own server: ",
    "time.justNow": "just now",
    "time.secondsAgo": "{n}s ago",
    "time.minutesAgo": "{n}m ago",
    "time.hoursAgo": "{n}h ago",
    "time.daysAgo": "{n}d ago",
    "time.future": "in the future",
    "sec.kpis.title": "Summary",
    "sec.kpis.subtitle": "Top-line counts, recomputed on every refresh from the sections below.",
    "sec.kpis.more": "\"fleet nodes\" is the entry count from --fleet-inventory. \"scenarios passing\" is passed/total from --scenario-catalog — an entry can pass either by succeeding or by raising the specific error its catalog row expects. \"events observed\" and \"non-noop actions\" come from --fleet-results-dir: non-noop actions are every recorded action outcome except \"noop\".",
    "kpi.fleetNodes": "fleet nodes",
    "kpi.scenariosPassing": "scenarios passing",
    "kpi.eventsObserved": "events observed",
    "kpi.nonNoopActions": "non-noop actions",
    "sec.fleet.title": "Fleet",
    "sec.fleet.subtitle": "Nodes from --fleet-inventory, each showing its last reported capability snapshot.",
    "sec.fleet.more": "Each card is one line of the fleet inventory JSONL file: a node_id, a RuntimeCapabilities snapshot, and when it was last_seen. \"stalest\" marks whichever node has the oldest last_seen timestamp (only shown when there is more than one node). The chips below are the same five capability flags as \"This host\", reported for that node instead of this process.",
    "fleet.notConfigured": "No fleet inventory configured for this run.",
    "fleet.unavailablePrefix": "Fleet inventory unavailable: ",
    "fleet.emptyConfigured": "Fleet inventory is configured but has no entries.",
    "fleet.hintCountOne": "{n} node",
    "fleet.hintCountMany": "{n} nodes",
    "fleet.stalest": "stalest",
    "fleet.lastSeenPrefix": "last seen ",
    "cap.os_name": "OS",
    "cap.arch": "architecture",
    "cap.vision_extra_available": "vision extra",
    "cap.transport_nats_available": "NATS transport",
    "cap.transport_mqtt_available": "MQTT transport",
    "cap.observability_extra_available": "observability extra",
    "cap.gpu_probe_tool_available": "GPU probe tool",
    "sec.scenarios.title": "Scenario results",
    "sec.scenarios.subtitle": "Pass/fail per entry in --scenario-catalog, run fresh on every load.",
    "sec.scenarios.more": "Every entry runs its scenario config and is checked against what the catalog row expects. A \"success\" entry passes on event-count/action thresholds; an \"error\" entry passes when the run raises exactly the named error_type — so a pass does not always mean nothing went wrong, it can mean the expected failure happened. \"Observed\" is the run's own detail text (the raised error, or \"ok\").",
    "scenarios.notConfigured": "No scenario catalog configured for this run.",
    "scenarios.unavailablePrefix": "Scenario catalog unavailable: ",
    "scenarios.emptyConfigured": "Scenario catalog is configured but defines no entries.",
    "scenarios.hintPassing": "{passed} / {total} passing",
    "scenario.pillPass": "pass",
    "scenario.pillFail": "fail",
    "scenario.observedPrefix": "Observed: ",
    "sec.observability.title": "Observability",
    "sec.observability.subtitle": "Aggregated from per-node result files under --fleet-results-dir.",
    "sec.observability.more": "Counts every SemanticEvent type and every MockAction outcome recorded across all result files in the directory. There is no live event stream here — it is a static aggregate of whatever result files already exist on disk.",
    "obs.notConfigured": "No fleet results directory configured for this run.",
    "obs.unavailablePrefix": "Observability data unavailable: ",
    "obs.emptyConfigured": "Results directory is configured but has no per-node results yet.",
    "obs.eventTypesTitle": "Event types ({total} total)",
    "obs.actionOutcomesTitle": "Action outcomes",
    "obs.noData": "No data recorded.",
    "sec.host.title": "This host",
    "sec.host.subtitle": "This process's own RuntimeCapabilities, from siqoq.capabilities.discover().",
    "sec.host.more": "A best-effort snapshot, not a guarantee: each flag is true only when the matching optional extra is importable right now (vision, transport, observability) or, for the GPU flag, when a known probe tool is on PATH — nothing here is actively exercised or benchmarked.",
    "sec.skills.title": "Skill catalog",
    "sec.skills.subtitle": "The built-in registry mapping SemanticEvent types to named skills.",
    "sec.skills.more": "A skill declares which event_types it handles; siqoq.skills.classify() looks up which skills match a given event's type. This is a data registry, not a live process — it does not run anything by itself.",
    "skills.empty": "No skills registered.",
    "footer.text": "Served from this process's own modules — nothing here is fabricated. No write endpoints exist; this page cannot change device or fleet state.",
    "guide.title": "How it works",
    "guide.subtitle": "The end-to-end path from a sensor sample to an action, and where the dashboard fits.",
    "guide.intro": "Siqoq connects a replaceable sensor source to a replaceable actuator through one stable contract: a SemanticEvent in the middle. This page traces that path stage by stage, shows the deployment modes it runs in, and marks plainly what exists in code today versus what is still a design proposal.",
    "guide.status.title": "Reading the diagrams",
    "guide.status.implemented": "Implemented",
    "guide.status.stub": "Stub / mock",
    "guide.status.proposed": "Proposed, not implemented",
    "guide.loop.title": "Core loop",
    "guide.loop.desc": "Every stage below is a real module boundary in src/siqoq; the dashed line marks that observability and the decision trace can span every stage, not just the ones shown as \"implemented\".",
    "guide.loop.diagramTitle": "Diagram: sensor to action core loop, with observability spanning every stage",
    "guide.loop.sensor.label": "Sensor adapter",
    "guide.loop.sensor.desc": "simulated / recorded / physical",
    "guide.loop.inference.label": "Inference",
    "guide.loop.inference.desc": "frame → detection",
    "guide.loop.event.label": "Semantic event",
    "guide.loop.event.desc": "SemanticEvent contract",
    "guide.loop.transport.label": "Transport",
    "guide.loop.transport.desc": "in-process / NATS / MQTT",
    "guide.loop.policy.label": "Policy decide",
    "guide.loop.policy.desc": "MockAction contract",
    "guide.loop.safety.label": "Safety gate",
    "guide.loop.safety.desc": "SafetyGate.approve()",
    "guide.loop.action.label": "Action adapter",
    "guide.loop.action.desc": "executes / rejects / no-ops",
    "guide.loop.observability.label": "Observability / decision trace",
    "guide.loop.sensorNote": "Implemented: generated + recorded/fixture sensors (siqoq/sensors.py, video_sensors.py) and real USB/UVC webcam capture (UsbWebcamFrameSensor, OpenCV via the optional vision extra). Mock: MockWebcamFrameSensor for hardware-free runs.",
    "guide.loop.inferenceNote": "OnnxCvInferenceAdapter (siqoq/inference.py) exists behind the optional vision extra, but is not wired to any CLI command yet — a caller must instantiate it directly with a model path.",
    "guide.loop.eventNote": "SemanticEvent (siqoq/events.py) is the stable contract every stage above and below actually depends on.",
    "guide.loop.transportNote": "In-process/stdout/file transports are core and dependency-free; NATS and MQTT adapters exist but need their optional extras installed (siqoq/transport.py).",
    "guide.loop.policyNote": "siqoq.policy.decide() is deterministic and mock-only by construction (see the D1 comments in policy.py and actuation.py).",
    "guide.loop.actionNote": "MockActuatorAdapter (siqoq/actuation.py) never performs I/O. RealGpioAdapter (siqoq/gpio.py) documents the real-hardware contract but raises NotImplementedError on open() — granting real actuator authority is an explicit, separately authorized design change per AGENTS.md.",
    "guide.modes.title": "Deployment modes",
    "guide.modes.desc": "The same contracts run in four modes from docs/architecture.md; only the adapters and runtime change. Fleet is the least built out today.",
    "guide.modes.diagramTitle": "Diagram: laptop, simulation, edge and fleet deployment modes",
    "guide.modes.col.mode": "Mode",
    "guide.modes.col.input": "Input",
    "guide.modes.col.runtime": "Runtime",
    "guide.modes.col.transport": "Transport",
    "guide.modes.col.output": "Output",
    "guide.modes.col.status": "Status here",
    "guide.modes.laptop": "Laptop",
    "guide.modes.laptop.input": "Recorded media or webcam",
    "guide.modes.laptop.runtime": "CPU baseline",
    "guide.modes.laptop.transport": "In-process / stdout",
    "guide.modes.laptop.output": "Mock or local action",
    "guide.modes.simulation": "Simulation",
    "guide.modes.simulation.input": "Isaac Sim or Gazebo",
    "guide.modes.simulation.runtime": "CPU/GPU as available",
    "guide.modes.simulation.transport": "Pluggable event bus",
    "guide.modes.simulation.output": "Virtual actuator",
    "guide.modes.edge": "Edge",
    "guide.modes.edge.input": "Physical sensors",
    "guide.modes.edge.runtime": "ONNX or accelerator adapter",
    "guide.modes.edge.transport": "NATS / MQTT / local",
    "guide.modes.edge.output": "Hardware adapter",
    "guide.modes.fleet": "Fleet",
    "guide.modes.fleet.input": "Multiple edge nodes",
    "guide.modes.fleet.runtime": "Declarative workloads",
    "guide.modes.fleet.transport": "Managed messaging",
    "guide.modes.fleet.output": "GitOps-managed adapters",
    "guide.modes.laptop.status": "Implemented for recorded/fixture input, real webcam capture (UsbWebcamFrameSensor, vision extra) and mock actions; webcam frames are not yet wired to a CLI command.",
    "guide.modes.simulation.status": "Proposed, not implemented — no Isaac Sim/Gazebo adapter exists in src/siqoq today.",
    "guide.modes.edge.status": "Partially implemented: ONNX inference adapter and NATS/MQTT transports exist as optional extras but aren't wired to a CLI command; real GPIO output is a stub.",
    "guide.modes.fleet.status": "Proposed, not implemented — today's fleet.py only aggregates local JSONL result files; no GitOps/Kubernetes wiring exists.",
    "guide.mapping.title": "How the dashboard maps to this flow",
    "guide.mapping.desc": "Every dashboard section reads one slice of the flow above, never a live stream — all of it is computed fresh per request in siqoq.ui.build_snapshot().",
    "guide.mapping.fleet.term": "Fleet section",
    "guide.mapping.fleet.desc": "One card per node in --fleet-inventory: the node_id, capability flags and last_seen from that node's own capability discovery. This is the input side of Edge/Fleet mode above.",
    "guide.mapping.scenarios.term": "Scenario results",
    "guide.mapping.scenarios.desc": "Runs the Core loop's sensor → event → policy path for each --scenario-catalog entry and checks the outcome, standing in for a repeatable end-to-end test of that loop.",
    "guide.mapping.observability.term": "Observability panel",
    "guide.mapping.observability.desc": "Aggregates the event-type and action-outcome counts recorded in --fleet-results-dir — the same two facts the decision trace (siqoq/trace.py) correlates per event.",
    "guide.mapping.host.term": "This host / capabilities",
    "guide.mapping.host.desc": "The Sensor adapter and Transport stages' available backends on this process, from siqoq.capabilities.discover().",
    "guide.mapping.skills.term": "Skill catalog",
    "guide.mapping.skills.desc": "The Policy / agent layer's registry of which SemanticEvent types have a named handler, from siqoq.skills.list_catalog().",
    "guide.notes.title": "Notes and open items",
    "guide.notes.actuation": "Actuation is mock-only today by explicit design: MockActuatorAdapter performs no I/O, and RealGpioAdapter raises NotImplementedError on open(). Any real actuator authority requires a separate, explicitly authorized design change (AGENTS.md, actuation.py, gpio.py).",
    "guide.notes.sandbox": "A pre-execution sandbox stage (running untrusted model/policy code in an isolated microVM before it can reach an action) is under evaluation in issue #74 and docs/evaluations/sandbox-execution-boundary.md — proposed, not implemented. Today's inventory found no dynamic code-execution path in src/siqoq at all.",
    "guide.sourcePrefix": "Source: "
  },
  "ko": {
    "app.badge": "읽기 전용 · 로컬",
    "nav.dashboard": "대시보드",
    "nav.guide": "가이드",
    "nav.aria": "주요 네비게이션",
    "skip.link": "본문으로 건너뛰기",
    "lang.aria": "언어",
    "lang.en": "EN",
    "lang.ko": "한국어",
    "header.hostPrefix": "호스트: ",
    "header.hostDetecting": "확인 중…",
    "header.updatedNotLoaded": "아직 불러오지 않음",
    "header.updatedPrefix": "업데이트: ",
    "header.autoRefresh": "자동 새로고침",
    "header.refresh": "새로고침",
    "header.intervalAria": "자동 새로고침 주기",
    "header.interval15": "15초",
    "header.interval30": "30초",
    "header.interval60": "60초",
    "common.moreInfoLabel": "자세히 보기",
    "common.retry": "다시 시도",
    "common.enableWith": "활성화 방법: ",
    "common.errorFetchPrefix": "이 대시보드의 자체 서버에 접속할 수 없음: ",
    "time.justNow": "방금 전",
    "time.secondsAgo": "{n}초 전",
    "time.minutesAgo": "{n}분 전",
    "time.hoursAgo": "{n}시간 전",
    "time.daysAgo": "{n}일 전",
    "time.future": "미래 시각",
    "sec.kpis.title": "요약",
    "sec.kpis.subtitle": "아래 섹션들에서 새로고침마다 다시 계산되는 핵심 지표입니다.",
    "sec.kpis.more": "\"플릿 노드\"는 --fleet-inventory의 항목 수입니다. \"통과한 시나리오\"는 --scenario-catalog의 통과/전체 개수로, 항목은 성공해서 통과하거나 카탈로그 항목이 기대한 특정 오류가 그대로 발생해도 통과합니다. \"관측된 이벤트\"와 \"no-op이 아닌 액션\"은 --fleet-results-dir에서 옵니다 — no-op이 아닌 액션은 기록된 액션 결과 중 \"noop\"을 제외한 모든 것입니다.",
    "kpi.fleetNodes": "플릿 노드",
    "kpi.scenariosPassing": "통과한 시나리오",
    "kpi.eventsObserved": "관측된 이벤트",
    "kpi.nonNoopActions": "no-op이 아닌 액션",
    "sec.fleet.title": "플릿",
    "sec.fleet.subtitle": "--fleet-inventory에 있는 노드들이며, 각각 마지막으로 보고된 기능 스냅샷을 보여줍니다.",
    "sec.fleet.more": "카드 하나는 플릿 inventory JSONL 파일의 한 줄입니다: node_id, RuntimeCapabilities 스냅샷, 마지막으로 확인된 시각(last_seen). \"가장 오래됨\"은 last_seen이 가장 오래된 노드를 표시합니다(노드가 2개 이상일 때만 표시). 아래 칩은 \"이 호스트\" 섹션과 동일한 5개 기능 플래그를 해당 노드 기준으로 보여줍니다.",
    "fleet.notConfigured": "이번 실행에 플릿 inventory가 설정되지 않았습니다.",
    "fleet.unavailablePrefix": "플릿 inventory를 사용할 수 없음: ",
    "fleet.emptyConfigured": "플릿 inventory가 설정되어 있지만 항목이 없습니다.",
    "fleet.hintCountOne": "노드 {n}개",
    "fleet.hintCountMany": "노드 {n}개",
    "fleet.stalest": "가장 오래됨",
    "fleet.lastSeenPrefix": "마지막 확인 ",
    "cap.os_name": "OS",
    "cap.arch": "아키텍처",
    "cap.vision_extra_available": "vision 확장",
    "cap.transport_nats_available": "NATS 전송",
    "cap.transport_mqtt_available": "MQTT 전송",
    "cap.observability_extra_available": "observability 확장",
    "cap.gpu_probe_tool_available": "GPU 프로브 도구",
    "sec.scenarios.title": "시나리오 결과",
    "sec.scenarios.subtitle": "--scenario-catalog의 항목별 성공/실패를 매 로드마다 다시 실행해 보여줍니다.",
    "sec.scenarios.more": "각 항목은 자신의 시나리오 설정을 실행한 뒤 카탈로그에 명시된 기대값과 비교됩니다. \"success\" 항목은 이벤트 수/액션 기준으로 통과하고, \"error\" 항목은 명시된 error_type이 그대로 발생해야 통과합니다 — 즉, 통과가 문제 없음을 의미하지 않고 기대한 실패가 일어났다는 뜻일 수도 있습니다. \"관측 결과\"는 실행 자체의 상세 텍스트입니다(발생한 오류 또는 \"ok\").",
    "scenarios.notConfigured": "이번 실행에 시나리오 카탈로그가 설정되지 않았습니다.",
    "scenarios.unavailablePrefix": "시나리오 카탈로그를 사용할 수 없음: ",
    "scenarios.emptyConfigured": "시나리오 카탈로그가 설정되어 있지만 항목이 없습니다.",
    "scenarios.hintPassing": "{passed} / {total} 통과",
    "scenario.pillPass": "통과",
    "scenario.pillFail": "실패",
    "scenario.observedPrefix": "관측 결과: ",
    "sec.observability.title": "Observability",
    "sec.observability.subtitle": "--fleet-results-dir 아래의 노드별 결과 파일을 집계합니다.",
    "sec.observability.more": "디렉토리 안의 모든 결과 파일에 기록된 SemanticEvent 유형과 MockAction 결과를 모두 집계합니다. 실시간 이벤트 스트림이 아니라, 디스크에 이미 있는 결과 파일을 정적으로 집계한 값입니다.",
    "obs.notConfigured": "이번 실행에 플릿 결과 디렉토리가 설정되지 않았습니다.",
    "obs.unavailablePrefix": "observability 데이터를 사용할 수 없음: ",
    "obs.emptyConfigured": "결과 디렉토리가 설정되어 있지만 아직 노드별 결과가 없습니다.",
    "obs.eventTypesTitle": "이벤트 유형 (총 {total}건)",
    "obs.actionOutcomesTitle": "액션 결과",
    "obs.noData": "기록된 데이터가 없습니다.",
    "sec.host.title": "이 호스트",
    "sec.host.subtitle": "siqoq.capabilities.discover()가 보고하는 이 프로세스 자체의 RuntimeCapabilities입니다.",
    "sec.host.more": "최선을 다한 추정치이지 보장값이 아닙니다: 해당 옵션 확장(vision, transport, observability)이 지금 import 가능할 때만, GPU 플래그는 알려진 프로브 도구가 PATH에 있을 때만 참입니다 — 실제로 실행하거나 벤치마크하지는 않습니다.",
    "sec.skills.title": "스킬 카탈로그",
    "sec.skills.subtitle": "SemanticEvent 유형을 이름 있는 스킬에 매핑하는 내장 레지스트리입니다.",
    "sec.skills.more": "스킬은 자신이 처리하는 event_types를 선언하며, siqoq.skills.classify()는 주어진 이벤트 유형과 일치하는 스킬을 찾습니다. 이것은 데이터 레지스트리일 뿐, 스스로 실행되는 프로세스가 아닙니다.",
    "skills.empty": "등록된 스킬이 없습니다.",
    "footer.text": "이 프로세스 자체의 모듈에서 제공되며, 조작된 데이터는 없습니다. 쓰기 엔드포인트는 존재하지 않으며, 이 페이지는 장치나 플릿 상태를 바꾸지 못합니다.",
    "guide.title": "동작 흐름",
    "guide.subtitle": "센서 샘플하나가 액션이 되기까지의 전 과정과, 그 안에서 대시보드가 차지하는 위치입니다.",
    "guide.intro": "Siqoq는 교체 가능한 센서 소스와 교체 가능한 액추에이터를 중간의 안정적인 계약인 SemanticEvent 하나로 연결합니다. 이 페이지는 그 경로를 단계별로 추적하고, 실행 중인 배포 모드를 보여주며, 오늘 코드에 있는 것과 설계 제안에 그치는 것을 명확히 구분합니다.",
    "guide.status.title": "다이어그램 보는 법",
    "guide.status.implemented": "구현됨",
    "guide.status.stub": "스텁 / 목(mock)",
    "guide.status.proposed": "제안됨 (미구현)",
    "guide.loop.title": "핵심 루프",
    "guide.loop.desc": "아래 단계는 모두 src/siqoq의 실제 모듈 경계입니다. 점선은 observability와 decision trace가 \"구현됨\"으로 표시된 단계뿐 아니라 모든 단계에 걸쳐 있음을 나타냅니다.",
    "guide.loop.diagramTitle": "다이어그램: 센서에서 액션까지의 핵심 루프와 모든 단계를 관통하는 observability",
    "guide.loop.sensor.label": "센서 어댑터",
    "guide.loop.sensor.desc": "시뮬레이션 / 녹화 / 실물",
    "guide.loop.inference.label": "추론",
    "guide.loop.inference.desc": "프레임 → 탐지",
    "guide.loop.event.label": "시맨틱 이벤트",
    "guide.loop.event.desc": "SemanticEvent 계약",
    "guide.loop.transport.label": "전송",
    "guide.loop.transport.desc": "프로세스 내 / NATS / MQTT",
    "guide.loop.policy.label": "정책 결정",
    "guide.loop.policy.desc": "MockAction 계약",
    "guide.loop.safety.label": "안전 게이트",
    "guide.loop.safety.desc": "SafetyGate.approve()",
    "guide.loop.action.label": "액션 어댑터",
    "guide.loop.action.desc": "실행 / 거부 / no-op",
    "guide.loop.observability.label": "Observability / decision trace",
    "guide.loop.sensorNote": "구현됨: 생성된 센서, 녹화/픽스처 센서(siqoq/sensors.py, video_sensors.py), 실제 USB/UVC 웹카메라 캡처(UsbWebcamFrameSensor, vision 옵션 확장의 OpenCV 사용). 목(mock): 하드웨어 없는 실행용 MockWebcamFrameSensor.",
    "guide.loop.inferenceNote": "OnnxCvInferenceAdapter(siqoq/inference.py)는 옵션 vision 확장 뒤에 존재하지만 아직 어떤 CLI 명령에도 연결되어 있지 않습니다 — 호출자가 모델 경로를 직접 전달해 생성해야 합니다.",
    "guide.loop.eventNote": "SemanticEvent(siqoq/events.py)는 위아래 모든 단계가 실제로 의존하는 안정적인 계약입니다.",
    "guide.loop.transportNote": "프로세스 내/stdout/파일 전송은 핵심이며 의존성이 없습니다. NATS와 MQTT 어댑터는 존재하지만 옵션 확장 설치가 필요합니다(siqoq/transport.py).",
    "guide.loop.policyNote": "siqoq.policy.decide()는 설계상 결정론적이고 mock 전용입니다(policy.py와 actuation.py의 D1 주석 참고).",
    "guide.loop.actionNote": "MockActuatorAdapter(siqoq/actuation.py)는 어떤 I/O도 수행하지 않습니다. RealGpioAdapter(siqoq/gpio.py)는 실제 하드웨어 계약을 문서화하지만 open()에서 NotImplementedError를 발생시킵니다 — 실제 액추에이터 권한을 부여하는 것은 AGENTS.md에 따라 별도로 승인받아야 하는 설계 변경입니다.",
    "guide.modes.title": "배포 모드",
    "guide.modes.desc": "docs/architecture.md에 정의된 4가지 모드 모두 동일한 계약을 사용하며 어댑터와 런타임만 달라집니다. Fleet이 현재 가장 덜 구축된 모드입니다.",
    "guide.modes.diagramTitle": "다이어그램: 노트북, 시뮬레이션, 에지, 플릿 배포 모드",
    "guide.modes.col.mode": "모드",
    "guide.modes.col.input": "입력",
    "guide.modes.col.runtime": "런타임",
    "guide.modes.col.transport": "전송",
    "guide.modes.col.output": "출력",
    "guide.modes.col.status": "현재 상태",
    "guide.modes.laptop": "노트북",
    "guide.modes.laptop.input": "녹화 미디어 또는 웹카메라",
    "guide.modes.laptop.runtime": "CPU 기본",
    "guide.modes.laptop.transport": "프로세스 내 / stdout",
    "guide.modes.laptop.output": "목 또는 로컬 액션",
    "guide.modes.simulation": "시뮬레이션",
    "guide.modes.simulation.input": "Isaac Sim 또는 Gazebo",
    "guide.modes.simulation.runtime": "가능한 경우 CPU/GPU",
    "guide.modes.simulation.transport": "교체 가능한 이벤트 버스",
    "guide.modes.simulation.output": "가상 액추에이터",
    "guide.modes.edge": "에지",
    "guide.modes.edge.input": "실물 센서",
    "guide.modes.edge.runtime": "ONNX 또는 가속기 어댑터",
    "guide.modes.edge.transport": "NATS / MQTT / 로컬",
    "guide.modes.edge.output": "하드웨어 어댑터",
    "guide.modes.fleet": "플릿",
    "guide.modes.fleet.input": "여러 에지 노드",
    "guide.modes.fleet.runtime": "선언적 워크로드",
    "guide.modes.fleet.transport": "관리형 메시징",
    "guide.modes.fleet.output": "GitOps로 관리되는 어댑터",
    "guide.modes.laptop.status": "녹화/픽스처 입력, 실제 웹캠 캡처(UsbWebcamFrameSensor, vision 옵션 확장), mock 액션은 구현됨. 웹캠 프레임은 아직 CLI 명령에 연결되어 있지 않음.",
    "guide.modes.simulation.status": "제안됨, 미구현 — 현재 src/siqoq에는 Isaac Sim/Gazebo 어댑터가 존재하지 않음.",
    "guide.modes.edge.status": "부분 구현: ONNX 추론 어댑터와 NATS/MQTT 전송은 옵션 확장으로 존재하지만 CLI 명령에는 연결되어 있지 않음. 실제 GPIO 출력은 스텁.",
    "guide.modes.fleet.status": "제안됨, 미구현 — 현재 fleet.py는 로컬 JSONL 결과 파일을 집계할 뿐이며 GitOps/Kubernetes 연동은 없음.",
    "guide.mapping.title": "대시보드가 이 흐름과 대응되는 방식",
    "guide.mapping.desc": "대시보드의 각 섹션은 위 흐름의 한 조각만 읽을 뿐 실시간 스트림이 아닙니다 — 모두 siqoq.ui.build_snapshot()에서 요청마다 새로 계산됩니다.",
    "guide.mapping.fleet.term": "플릿 섹션",
    "guide.mapping.fleet.desc": "--fleet-inventory의 노드당 카드 하나: node_id, 해당 노드 자체의 기능 플래그, last_seen. 위 Edge/Fleet 모드의 입력 측에 해당합니다.",
    "guide.mapping.scenarios.term": "시나리오 결과",
    "guide.mapping.scenarios.desc": "각 --scenario-catalog 항목에 대해 핵심 루프의 센서 → 이벤트 → 정책 경로를 실행하고 결과를 확인해, 해당 루프의 반복 가능한 종단 간 테스트 역할을 합니다.",
    "guide.mapping.observability.term": "Observability 패널",
    "guide.mapping.observability.desc": "--fleet-results-dir에 기록된 이벤트 유형과 액션 결과 건수를 집계합니다 — decision trace(siqoq/trace.py)가 이벤트별로 연결하는 것과 동일한 두 가지 정보입니다.",
    "guide.mapping.host.term": "이 호스트 / 기능",
    "guide.mapping.host.desc": "siqoq.capabilities.discover()가 보고하는, 이 프로세스에서 사용 가능한 센서 어댑터와 전송 백엔드입니다.",
    "guide.mapping.skills.term": "스킬 카탈로그",
    "guide.mapping.skills.desc": "siqoq.skills.list_catalog()에서 가져온, 어떤 SemanticEvent 유형에 이름 있는 핸들러가 있는지에 대한 정책/에이전트 계층의 레지스트리입니다.",
    "guide.notes.title": "참고 사항과 미결 항목",
    "guide.notes.actuation": "액추에이터는 명시적인 설계에 따라 오늘날 mock 전용입니다: MockActuatorAdapter는 I/O를 수행하지 않고, RealGpioAdapter는 open()에서 NotImplementedError를 발생시킵니다. 실제 액추에이터 권한은 별도로 명시적 승인을 받는 설계 변경이 필요합니다(AGENTS.md, actuation.py, gpio.py).",
    "guide.notes.sandbox": "신뢰할 수 없는 모델/정책 코드를 액션에 도달하기 전에 격리된 microVM에서 먼저 실행하는 실행 전 샌드박스 단계는 이슈 #74와 docs/evaluations/sandbox-execution-boundary.md에서 검토 중입니다 — 제안되었을 뿐 구현되지 않았습니다. 현재 조사에서 src/siqoq에는 동적 코드 실행 경로가 전혀 발견되지 않았습니다.",
    "guide.sourcePrefix": "출처: "
  }
};

(function (global) {
  "use strict";

  var LANG_KEY = "siqoq-dashboard-lang";

  function detectDefaultLang() {
    try {
      var nav = (navigator.language || navigator.userLanguage || "en").toLowerCase();
      return nav.indexOf("ko") === 0 ? "ko" : "en";
    } catch (e) {
      return "en";
    }
  }

  function readQueryLang() {
    try {
      var params = new URLSearchParams(window.location.search);
      var q = params.get("lang");
      return q === "ko" || q === "en" ? q : null;
    } catch (e) {
      return null;
    }
  }

  function readStoredLang() {
    try {
      var stored = localStorage.getItem(LANG_KEY);
      return stored === "ko" || stored === "en" ? stored : null;
    } catch (e) {
      return null;
    }
  }

  function writeStoredLang(lang) {
    try {
      localStorage.setItem(LANG_KEY, lang);
    } catch (e) {
      // ignore (private browsing / storage disabled)
    }
  }

  var currentLang = readQueryLang() || readStoredLang() || detectDefaultLang();

  function t(key, vars) {
    var dict = DICT[currentLang] || DICT.en;
    var value = Object.prototype.hasOwnProperty.call(dict, key)
      ? dict[key]
      : (DICT.en && DICT.en[key]) || key;
    if (vars) {
      Object.keys(vars).forEach(function (name) {
        value = value.split("{" + name + "}").join(String(vars[name]));
      });
    }
    return value;
  }

  function getLang() {
    return currentLang;
  }

  function setLang(lang) {
    if (lang !== "ko" && lang !== "en") return;
    currentLang = lang;
    writeStoredLang(lang);
    document.documentElement.setAttribute("lang", lang);
    applyStaticI18n();
    document.dispatchEvent(new CustomEvent("siqoq:lang-changed", { detail: { lang: lang } }));
  }

  function applyStaticI18n(root) {
    var scope = root || document;
    scope.querySelectorAll("[data-i18n]").forEach(function (node) {
      node.textContent = t(node.getAttribute("data-i18n"));
    });
    scope.querySelectorAll("[data-i18n-attr]").forEach(function (node) {
      node.getAttribute("data-i18n-attr").split(",").forEach(function (pair) {
        var parts = pair.split(":");
        if (parts.length === 2) node.setAttribute(parts[0].trim(), t(parts[1].trim()));
      });
    });
  }

  function relativeTime(iso) {
    var then = new Date(iso).getTime();
    if (isNaN(then)) return { text: iso, title: iso };
    var diffSec = Math.round((Date.now() - then) / 1000);
    var text;
    if (diffSec < 0) text = t("time.future");
    else if (diffSec < 5) text = t("time.justNow");
    else if (diffSec < 60) text = t("time.secondsAgo", { n: diffSec });
    else if (diffSec < 3600) text = t("time.minutesAgo", { n: Math.round(diffSec / 60) });
    else if (diffSec < 86400) text = t("time.hoursAgo", { n: Math.round(diffSec / 3600) });
    else text = t("time.daysAgo", { n: Math.round(diffSec / 86400) });
    return { text: text, title: iso, ageSec: diffSec };
  }

  document.documentElement.setAttribute("lang", currentLang);

  global.SiqoqI18n = {
    t: t,
    getLang: getLang,
    setLang: setLang,
    applyStaticI18n: applyStaticI18n,
    relativeTime: relativeTime
  };
})(window);
