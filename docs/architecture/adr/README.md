# Architecture Decision Records

Format by Michael Nygard: context, decision, consequences. Accepted records are not edited; a new
record supersedes an old one.

| # | Decision | Status |
|---|---|---|
| [0001](0001-two-processes-and-fifos.md) | Two processes (vision, master) linked by named pipes | Accepted (from TMR 2026) |
| [0002](0002-ports-and-adapters.md) | Ports and adapters with `typing.Protocol` | Accepted |
| [0003](0003-pure-state-machine.md) | State machine as a pure function of time and inputs | Accepted |
| [0004](0004-golden-tests.md) | Golden tests against the TMR 2026 code | Accepted |
| [0005](0005-host-testable-firmware.md) | Firmware logic free of Arduino headers | Accepted |
| [0006](0006-keep-wire-protocol.md) | Keep the pipe and UART protocols unchanged | Accepted |
