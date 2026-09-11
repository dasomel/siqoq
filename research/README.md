# Research Evidence

Siqoq follows the OpenForge Research Evidence Collection Standard:
https://github.com/dasomel/openforge/blob/main/docs/research-evidence.md

Collect sanitized machine-readable evidence during normal development when practical. Useful evidence includes simulation/edge/inference test duration and results, latency/resource measurements where relevant, failures/recovery/retries, normalized hardware/environment profiles, and agent-assisted attempts, elapsed time, human interventions, review corrections, CI retries, and final verification.

Preserve negative/partial results and distinguish simulation/recorded-input evidence from physical-device evidence.

## Public-data rule

Only sanitized records may be committed publicly. Never publish credentials/tokens, private URLs/IPs/hostnames, personal/customer/employer data, raw sensitive media, confidential prompts/source, arbitrary environment dumps, or security-sensitive device/infrastructure details. Raw camera/sensor data, traces, CI logs, screenshots, prompts, and security output are sensitive-by-default.

Before public storage: validate against the OpenForge schema, run secret/pattern checks, normalize device/environment labels, review free-form fields, and publish aggregate/categorized measurements when raw artifacts cannot be proven safe.
