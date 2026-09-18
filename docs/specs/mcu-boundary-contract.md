# MCU/Motor-Controller Boundary Contract v0

Status: v0, **contract only — no MCU adapter is implemented in this
repository, and no MCU hardware exists to test against.** This document
defines the boundary that a future MCU/motor-controller adapter must
implement; it does not implement or exercise that adapter.

This contract sits downstream of the ActuatorAdapter contract (issue #51,
prospectively `siqoq.actuation` if/when it lands) and is a sibling to the
GPIO adapter contract (issue #52). See `docs/architecture.md`, "Action
adapters", for where actuation fits in the input -> inference -> semantic
event -> decision -> action pipeline.

## Why this boundary exists

AGENTS.md treats any new physical side effect or actuator authority as a
high-risk design change and requires actuation to stay behind an explicit
adapter/policy boundary rather than branching application logic throughout
the codebase. The MCU boundary is the specific point where Siqoq's software
stops and MCU-resident firmware (motor controller, driver board, etc.)
begins. This document is that boundary's contract.

## What crosses the boundary

Only plain, typed data crosses the MCU boundary — never raw serial bytes,
never protocol-specific framing (no CRC bytes, packet headers, register
addresses, or vendor wire formats) in core Siqoq code.

- Commands are typed values such as velocity setpoints, position setpoints,
  or the mandatory stop command (see below) — plain Python data (e.g.
  dataclasses/enums), analogous to how `MockAction` is the typed boundary
  between `siqoq.policy` and action adapters in
  `docs/specs/action-contract.md`.
- Translating a typed command into the wire protocol a specific MCU expects
  (serial framing, checksums, register maps, baud rate handling, etc.) is
  the responsibility of the future MCU adapter implementation, kept behind
  this boundary — not something core policy/decision code, the
  ActuatorAdapter contract, or the GPIO adapter contract should ever need
  to know about.
- No vendor- or protocol-specific type (e.g. a specific serial library
  object, a specific MCU SDK class) may appear in a type signature outside
  the MCU adapter itself, mirroring the existing "no vendor/actuator type"
  check applied to `sensors.py`/`events.py` and the action contract.

## Relationship to the ActuatorAdapter and GPIO adapter contracts

- **ActuatorAdapter/ActionResult contract (issue #51):** the ActuatorAdapter
  contract is the general actuation boundary — it defines how a decided
  action becomes an `ActionResult` regardless of which physical mechanism
  executes it. The MCU boundary defined here is one possible adapter
  *behind* that boundary: an MCU/motor-controller implementation of
  whatever adapter interface the ActuatorAdapter contract specifies. This
  document does not redefine `ActionResult` or the adapter interface itself;
  it only constrains what an MCU-backed adapter implementation may send
  across the wire once the ActuatorAdapter contract lands.
- **GPIO adapter contract (issue #52):** the GPIO adapter is a sibling
  actuator adapter, not a dependency of this boundary. GPIO (digital
  pins/relays) and MCU (a semi-autonomous microcontroller running its own
  firmware loop) are different physical mechanisms behind the same
  ActuatorAdapter boundary. A system may implement one, both, or neither;
  this document does not assume the GPIO adapter exists, only that both
  adapters, if implemented, sit behind the same actuator/policy boundary
  and follow the same "plain typed data in, no hardware types leaking out"
  rule.

## Safety requirements (explicit)

These are safety-sensitive requirements per AGENTS.md's actuator-authority
rule, stated now so that any future MCU adapter implementation is measured
against them from day one:

- **Command rate limits.** The MCU boundary must enforce a maximum command
  rate (e.g. a minimum interval between successive velocity/position
  setpoints). A future adapter that cannot demonstrate a rate limit is not
  conformant with this contract. The exact numeric limit is deployment-
  specific and is deferred to the adapter's own design review — this
  contract only mandates that a limit exists and is enforced at the
  boundary, not assumed by callers.
- **Mandatory stop command.** The command vocabulary crossing this boundary
  must always include a stop / zero-velocity command, and that command must
  always be honorable — it must never be rejected, queued behind other
  commands, or subject to the same rate limit as normal setpoints. Any
  future adapter must treat stop as the highest-priority command in its
  implementation.
- **Fail-safe-to-stopped default.** If communication between Siqoq and the
  MCU is lost (timeout, disconnect, malformed response), the *MCU-side
  firmware* — not Siqoq — is responsible for stopping the actuator (e.g. a
  watchdog timeout on the firmware side that zeroes output in the absence
  of fresh commands). Siqoq's obligation under this contract is narrower
  and entirely within its own control: it must never send a command that
  implies continued motion is safe when it cannot confirm the MCU is
  receiving fresh commands (e.g. no "cruise indefinitely" command exists in
  the vocabulary; every non-stop command is a single setpoint, not a
  standing instruction). Siqoq does not, and cannot, guarantee the MCU
  firmware behavior itself — that guarantee is a hardware/firmware property
  outside this repository's scope, which is exactly why no MCU adapter is
  implemented here.

## Compatibility rules

- **Breaking:** removing the stop command from the vocabulary, allowing
  stop to be rate-limited or queued, or allowing a non-stop command that
  implies open-ended/standing motion (no bounded setpoint).
- **Compatible / additive:** adding new typed setpoint kinds, tightening
  (lowering) a rate limit, adding new adapter-side telemetry that does not
  change what commands cross the boundary.

## Conformance

There is nothing to conformance-test in this repository today: no MCU
adapter exists, and no MCU hardware is available to exercise fail-safe
behavior against. Conformance for a future adapter must include, at
minimum: a rate-limit test (command rejected/held below the minimum
interval), a stop-command test (stop always accepted regardless of rate
limit state), and a documented statement of which physical MCU/firmware was
used to validate the fail-safe-to-stopped behavior, since that behavior
cannot be verified in simulation alone.
