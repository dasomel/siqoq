# Project Name — Siqoq

**English** | [한국어](project-name.ko.md)

## Pronunciation

For this project, **Siqoq** is pronounced **“see-kok”** (Korean: **시콕**).

## Meaning and inspiration

The name is inspired by Arctic snow-and-wind imagery, especially the idea of **drifting snow**: snow particles moving with the surrounding environment rather than remaining fixed in one place.

Siqoq uses that image as a metaphor for an AI workload moving across environments:

```text
Simulation
   ↓
Laptop
   ↓
Edge
   ↓
Physical World
```

The workload may move, but the core contracts for sensing, semantic events, inference, policy, observability, and action should remain as stable as practical.

## What the naming research clarified

The project was not named Siqoq immediately. Early exploration covered whale names, Arctic terms, ocean concepts, and ideas around boundaries, movement, sensing, and feedback.

Candidates included names such as Beluga, Orca, Minke, Bowhead, Baleen, Fluke, Tusk, Coda, Triton, Tidal, Spiral, Helix, Qajaq, Polynya, and Boreal. Many were already strongly occupied across GitHub, AI products, robotics research, or established brands.

The more important result was not eliminating names; it was clarifying the project's identity.

### It does not need to be another whale name

Siqoq should fit alongside projects such as Narwhal and Beluga without mechanically repeating another animal name. Otherwise the mascot relationship can become more visible than the technical role.

### Direct technical names age poorly

Names built directly from words such as `edge`, `physical`, `robot`, `agent`, `sense`, `field`, or `loop` were heavily saturated and risk tying the identity to a narrow technology moment.

### The concepts that survived

The strongest conceptual anchors were:

- Digital ↔ Physical boundary
- Simulation ↔ Reality
- movement across environments
- Sense → Think → Act → Feedback
- edge as a bridge
- Arctic ecosystem identity

Siqoq was selected because it preserves the **movement + Arctic** identity without binding the project to one device, framework, or AI model.

## Relationship to the wider OSS ecosystem

The names share a world rather than a strict naming template:

```text
Narwhal
  Cloud Native / Platform Infrastructure

Beluga
  Data Platform

Siqoq
  Simulation → Edge → Physical AI
```

The common thread is an Arctic/ocean-inspired OSS ecosystem in which each project owns a different engineering problem.

## Linguistic note

Arctic Indigenous languages are diverse, and there is no single language that should simply be called “the Inuit language.” Spellings and meanings can vary by language, region, and dialect.

For that reason, Siqoq does **not** use the name as a claim that one spelling has one universal linguistic definition across Inuit languages. The repository uses **Siqoq** primarily as its project identity and as an Arctic-inspired metaphor for portability and movement across environments.

When describing the name publicly, prefer wording such as:

> **Siqoq (pronounced “see-kok”) is an Arctic-inspired name associated with the image of drifting snow. In this project, it represents AI workloads moving from simulation to edge and into the physical world.**

Avoid presenting an unsupported universal translation or claiming authority over Indigenous terminology.

## Brand statement

> **Build in simulation. Run at the edge. Move into the physical world.**

## Why the name fits the architecture

Siqoq is intentionally not named after a specific hardware vendor, robotics framework, AI model family, or cloud platform. This supports the long-term architecture:

- laptop before dedicated hardware
- simulation before risky physical testing
- CPU baseline before accelerator-specific optimization
- adapters instead of vendor lock-in
- edge execution without mandatory cloud
- optional Kubernetes/fleet operation only when scale requires it
- perception-action-feedback loop rather than one-way inference
- stable contracts instead of device-specific APIs

The name should remain stable even if the project adds new simulators, model runtimes, accelerators, robots, or orchestration systems.

See [Siqoq Vision](vision.md) for the broader project direction that emerged from this research.
