# Project Principles

Siqoq follows the OSS engineering baseline maintained in OpenForge, adapted for simulation-first Physical AI development.

## 1. Design before implementation

Significant features should start with an issue that explains the problem, affected architecture, alternatives, and acceptance criteria before implementation.

## 2. Small, reviewable changes

Prefer focused issues and pull requests over large mixed changes. Keep architecture, runtime, hardware support, and documentation changes independently reviewable where practical.

## 3. Simulation before hardware dependency

Every feature that can be exercised without hardware should provide a local or simulated path first. Hardware-specific behavior should be isolated behind adapters.

## 4. Stable contracts over vendor lock-in

Do not expose vendor SDK types as core Siqoq APIs. Jetson, ROS 2, Isaac Sim, Gazebo, MQTT, NATS, and Kubernetes are integrations, not the domain model.

## 5. Observable by default

Inference, events, decisions, actions, errors, and device state should emit structured telemetry suitable for logs, metrics, and traces.

## 6. Safe actuation boundary

No reasoning component should directly drive physical hardware. Actions pass through explicit adapters and policy checks, and hardware examples must default to non-destructive mock behavior.

## 7. Reproducible development

Dependencies should be pinned or constrained, development commands documented, and CI should reproduce lint/test/build checks from a clean environment.

## 8. Security and dependency hygiene

Secrets never belong in the repository. Dependency updates, vulnerability reporting, and least-privilege examples follow OpenForge guidance.

## 9. Documentation is part of the feature

Public interfaces, adapters, schemas, deployment behavior, and hardware assumptions require documentation in the same change.

## 10. AI-assisted development remains reviewable

AI tools may be used for implementation and review, but generated changes must follow the same issue-first, test, documentation, licensing, and security requirements as human-authored changes.
