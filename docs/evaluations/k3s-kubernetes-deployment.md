# Evaluation: K3s and Kubernetes deployment option spike

Tracking: #61 (part of #10). Related: #46 (generic ARM64 container build), #58 (declarative workload specification format).

**No Kubernetes or K3s deployment has been implemented, run, or verified anywhere in this repository.**
No Kubernetes cluster or K3s control plane/agent exists in this development environment.
All statements below are design and architectural evaluations based on public K3s,
Kubernetes, and container runtime specifications, not on running or scheduling workloads
in a live cluster.

## Goal

Evaluate what a K3s or standard Kubernetes deployment option would require for Siqoq's
containerized Python application on edge/ARM64 devices and hybrid edge-cloud topologies,
without introducing cluster dependencies into the core package or compromising the
standalone single-node CLI workflow.

## K3s vs. Standard Kubernetes: Tradeoffs on Edge/ARM64

K3s is a certified, lightweight Kubernetes distribution developed by Rancher/SUSE
and maintained under the CNCF. It is specifically tailored for resource-constrained
environments, edge gateways, and IoT/ARM platforms.

### 1. Resource footprint and overhead

- **Standard Kubernetes (K8s)**: Requires separate processes for `kube-apiserver`,
  `kube-controller-manager`, `kube-scheduler`, `kubelet`, `kube-proxy`, and a dedicated
  `etcd` cluster. The control plane typically demands >1.5–2 GB RAM and persistent,
  low-latency disk I/O for `etcd` write-ahead logs. On edge devices (e.g. 4GB or 8GB
  NVIDIA Jetson Orin Nano, Raspberry Pi 5), running a full control plane consumes a
  disproportionate share of memory that should otherwise be allocated to video frame
  buffers and neural network weights.
- **K3s**: Packages all control plane components into a single binary (<100 MB on disk).
  By default, it replaces `etcd` with a lightweight SQLite datastore (via Kine), bundles
  `containerd`, Flannel CNI, CoreDNS, local path provisioner, and metrics server. A K3s
  server runs in ~512 MB RAM, and a worker agent runs in ~250–300 MB RAM. This leaves
  sufficient headroom for Siqoq's computer vision and inference pipeline on ARM64 boards.

### 2. Packaging and binary distribution

- **Standard Kubernetes**: Multi-package installation, complex certificate bootstrapping,
  and extensive infrastructure dependencies.
- **K3s**: Shipped as a standalone binary with official multi-architecture support
  (`linux/amd64`, `linux/arm64`, `linux/armv7`). Installation on edge Linux distributions
  (such as Ubuntu 22.04/24.04 or Jetson Linux L4T) requires only a single binary and a
  systemd unit file, with automated TLS certificate generation and rotation.

### 3. Edge peripheral and hardware accelerator access

In Physical AI and robotic perception workloads, containers must access physical hardware
peripherals (webcams, CSI cameras, serial ports for microcontrollers/actuators) and
hardware acceleration (CUDA/TensorRT on NVIDIA Jetson, NPU/VPU).

- **Device Passthrough**: Both standard Kubernetes and K3s rely on the Container Runtime
  Interface (CRI, standard `containerd`). Direct device access (e.g. `/dev/video0`,
  `/dev/ttyUSB0`) can be handled via host path volume mounts, container `securityContext`
  privileges, or specialized device plugins.
- **GPU / Accelerator Acceleration**:
  - In standard K8s: Requires installing the NVIDIA Container Toolkit on every node and
    deploying the NVIDIA GPU Operator or NVIDIA k8s-device-plugin DaemonSet.
  - In K3s: On NVIDIA Jetson running JetPack/L4T, containerd can be configured directly
    to use the `nvidia` runtime as the default runtime (via `/etc/rancher/k3s/config.toml.tmpl`),
    allowing pods to request GPU acceleration without heavy cluster operator overhead.

### Tradeoff Summary

| Dimension | Standard Kubernetes (K8s) | Lightweight Kubernetes (K3s) | Implication for Siqoq |
|---|---|---|---|
| Target Environment | Data centers, cloud clusters | Edge devices, ARM64 gateways, IoT | K3s aligns with edge/embedded hardware targets |
| Server Memory Footprint | ~1.5 GB – 2+ GB RAM | ~512 MB RAM | K3s preserves memory for inference models |
| Datastore | Dedicated `etcd` cluster | Embedded SQLite via Kine (or external etcd/Postgres) | K3s avoids etcd disk I/O bottleneck on flash/SD cards |
| Packaging & Install | Multi-binary, complex bootstrap | Single binary (<100MB), zero-dependency install | K3s simplifies edge provisioning |
| ARM64 Compatibility | Supported, but heavyweight | First-class citizen across ARM64 / Jetson | Seamless match with #46 ARM64 image |
| API Conformance | Reference implementation | CNCF-certified Kubernetes conformant | Identical manifest definitions apply to both |

Sources: [K3s Architecture — Official Docs](https://docs.k3s.io/architecture), [K3s Resource Requirements](https://docs.k3s.io/installation/requirements), [NVIDIA Container Toolkit on K3s](https://docs.k3s.io/advanced#nvidia-container-runtime-support).

## Mapping Container Images and Declarative Workloads to Manifests

### Container Image Foundation

Issue #46 established the multi-architecture container build (`Dockerfile` at repo root),
producing images for `linux/amd64` and `linux/arm64`. The runtime entrypoint is the `siqoq`
CLI:
```dockerfile
ENTRYPOINT ["siqoq"]
CMD ["demo"]
```

### Declarative Workload Mapping (#58)

Sibling issue #58 defines a portable, declarative workload specification format (YAML/JSON)
specifying:
1. Workload target: scenario configuration or pipeline run parameters
2. Resource hints: requested CPU and memory
3. Target capability requirements: required sensors (webcam, recorded media), acceleration
   (CPU, TensorRT), or transports (in-process, NATS, MQTT).

In a K3s or Kubernetes environment, these workload declarations map naturally to standard
Kubernetes API primitives without requiring custom orchestration code in Python:

| Workload Concept (#58) | Kubernetes Primitive | Manifest Mapping |
|---|---|---|
| Continuous perception service | `Deployment` or `DaemonSet` | Long-running pod restarting on failure |
| Finite scenario / benchmark | `Job` | Single-shot pod running to completion (`restartPolicy: Never`) |
| Scenario / pipeline config | `ConfigMap` | Mounted as a configuration volume under `/etc/siqoq/` |
| Resource requirements | `resources.requests` / `limits` | Direct mapping to container CPU and memory constraints |
| Capability: Camera / Sensor | `volumeMounts` / `securityContext` | Mount `/dev/video*` or CSI device nodes via hostPath |
| Capability: GPU / Accelerator | Device limits / runtimeClassName | `resources.limits: { nvidia.com/gpu: 1 }` or runtime class |
| Node capability matching | `nodeSelector` / `affinity` | Target nodes labeled with required hardware profiles |

### Illustrative Manifest: Continuous Perception Deployment

Below is an illustrative Kubernetes manifest demonstrating how the existing ARM64 container
image and a declarative workload would be deployed on a K3s edge node:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: siqoq-perception-pipeline
  labels:
    app.kubernetes.io/name: siqoq
    app.kubernetes.io/component: perception
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: siqoq
  template:
    metadata:
      labels:
        app.kubernetes.io/name: siqoq
    spec:
      nodeSelector:
        kubernetes.io/arch: arm64
      containers:
        - name: siqoq
          image: siqoq:latest-arm64
          imagePullPolicy: IfNotPresent
          args: ["scenario", "run", "--config", "/etc/siqoq/workload.yaml"]
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "2Gi"
          securityContext:
            privileged: false
          volumeMounts:
            - name: scenario-config
              mountPath: /etc/siqoq
              readOnly: true
            - name: video-device
              mountPath: /dev/video0
      volumes:
        - name: scenario-config
          configMap:
            name: siqoq-workload-config
        - name: video-device
          hostPath:
            path: /dev/video0
```

### Illustrative Manifest: Scenario Benchmark Job

For deterministic verification, test suite execution, or simulation replay:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: siqoq-scenario-job
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: siqoq-scenario
          image: siqoq:latest-arm64
          args: ["scenario", "run", "--config", "/etc/siqoq/scenario.yaml"]
          volumeMounts:
            - name: scenario-config
              mountPath: /etc/siqoq
              readOnly: true
      volumes:
        - name: scenario-config
          configMap:
            name: siqoq-scenario-config
```

## Preservation of Single-Node CLI Optionality

In strict alignment with `AGENTS.md` and `docs/principles.md` (Principle 4: Stable contracts
over vendor lock-in; Architecture boundary: Do not introduce fleet/GitOps complexity before
the single-node path needs it):

1. **Zero Core Dependencies**: The core Python package (`src/siqoq`) must never import
   `kubernetes`, `k8s-client`, or communicate directly with the Kubernetes API server.
2. **Independent CLI Workflow**: Local commands (`siqoq demo`, `siqoq scenario run`, and
   future declarative workload runners) operate purely in user-space, reading local files
   or standard streams. They must function identically on a macOS developer laptop, a bare
   Linux shell, a raw container (`docker run`), or inside a Kubernetes pod.
3. **Orchestration Stays Outside**: Kubernetes/K3s manifests, Helm charts, and GitOps
   pipelines belong in an external operational directory (e.g. `deploy/k8s/` or a separate
   fleet repository), completely decoupled from the core application codebase.

### Boundary Matrix

| Component | In Core Code (`src/siqoq/`) | In External Orchestration (`deploy/`) |
|---|---|---|
| CLI commands (`siqoq demo`, `siqoq scenario run`) | Yes | No |
| Declarative workload schema and local validator (#58) | Yes | No |
| Hardware capability detection (`RuntimeCapabilities`) | Yes | No |
| Kubernetes manifest definitions (`Deployment`, `Job`) | No | Yes |
| Node scheduling, pod lifecycle, restart policies | No | Yes |
| K3s cluster installation and systemd services | No | Yes |

## Edge Realities and Practical Caveats

While K3s offers a low-overhead Kubernetes option, several edge-specific constraints must
be considered before adopting cluster orchestration on individual robotics/physical AI nodes:

1. **Sensor and IPC Latency**: In high-framerate perception pipelines, passing frames
   over network sockets or cluster service proxies introduces latency and CPU copies.
   In-process or local Unix domain socket communication (NATS/MQTT/shared memory) remains
   preferable for on-device loops.
2. **Device Nodes and Root Privileges**: Physical cameras (`/dev/video*`, CSI via Libargus)
   and hardware serial interfaces often require specific Linux group permissions (`video`,
   `dialout`) or root access. Managing dynamic hotplug devices in containerized Kubernetes
   pods requires udev rules or specialized daemonsets.
3. **Control Plane Overhead on Battery/Thermal Limits**: Even a ~500 MB RAM control plane
   draws constant CPU cycles for health checks, heartbeat probes, and metrics scraping,
   which impacts thermal budgets and battery life on mobile robots.

## Recommendation: adopt-later

- **Not do-not-adopt**: Fleet management with declarative configuration and optional
  K3s/Kubernetes integration is explicitly listed in `docs/architecture.md` as part of
  Phase 5 (Fleet mode). K3s is the industry standard for lightweight edge Kubernetes, and
  Siqoq's containerized CLI architecture cleanly maps to standard Pod/Deployment/Job models.
- **Not adopt-now**:
  - No physical edge cluster or test cluster environment currently exists in this repository
    to execute, test, or validate manifests.
  - Sibling issue #58 (declarative workload specification) has not yet landed. Writing
    hardened manifests before the underlying workload configuration schema is finalized
    would lead to churn and unverified code.
  - The single-node simulation-first pipeline is the core priority; introducing cluster
    manifests now violates the principle of avoiding premature fleet complexity.
- **Revisit Conditions**:
  Revisit when:
  1. Issue #58 declarative workload specification schema is implemented and verified.
  2. Multi-node edge fleet inventory (#59) or workload placement (#60) requires automated
     remote deployment.
  3. A lightweight verification mechanism (e.g. K3d or Kind in GitHub Actions CI) is set up
     to validate manifest syntax and pod startup deterministically.

## Explicit Non-Claim

No Kubernetes or K3s deployment, cluster, pod, deployment manifest, or service has been
implemented, executed, or verified in this repository as part of this evaluation or any prior
work. All findings, tradeoff analyses, and manifest examples presented in this document are
derived from public CNCF/K3s documentation and standard container runtime principles.
