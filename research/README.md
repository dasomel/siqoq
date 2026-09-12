# Research Evidence

Siqoq follows the OpenForge Research Evidence Collection Standard:
https://github.com/dasomel/openforge/blob/main/docs/research-evidence.md

Collect machine-readable evidence during normal development when practical. Useful evidence includes simulation/edge/inference test duration/results, latency/resource measurements, failures/recovery/retries, hardware/environment profiles, and agent-assisted attempts/interventions/review corrections/CI retries/final verification. Preserve negative/partial results and distinguish simulation/recorded-input evidence from physical-device evidence.

## Legacy evidence on discovery

During implementation, fixes, verification, simulation/device experiments, releases, or documentation, catalog historical simulation results, recorded-input/device tests, inference/latency/resource measurements, CI results, failure/recovery records, and dated experiment evidence encountered from earlier work. Preserve the original evidence and its simulation/physical distinction.

Use `dasomel/openforge#89` as the portfolio-level legacy catalog source of truth. Record source/path, known date, evidence class/strength, environment scope, metrics/facts, limitations, and likely paper use. Never infer measurements that were not recorded. Keep negative, partial, and superseded experiment results when useful longitudinally.

## Public-data rule

This is a personal OSS/test project. Synthetic/recorded test identifiers, device/model specifications, local endpoints, RFC1918 addresses, and reproducibility-relevant environment/runtime details may remain when intentionally part of public experiments.

Never publish credentials/tokens/private keys, genuinely sensitive media, real personal data, or accidental personal information. Review future third-party/non-public artifacts separately. Validate structured evidence against the OpenForge schema and run secret/pattern checks before publication.