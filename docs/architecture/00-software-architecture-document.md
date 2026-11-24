# Software Architecture Document (SAD)

Structure follows the RUP *Software Architecture Document* template, with the 4+1 view model as the
architectural representation.

## 1. Introduction

**Purpose.** Give a complete architectural overview of KATA-bot's software and justify its significant
decisions, so that a new team can understand, rebuild and improve it.
**Scope.** The Raspberry Pi software (vision + master) and the ESP32 firmware.
**References.** [Vision](../rup/01-vision.md) · [Requirements](../rup/02-requirements.md) · [ADRs](adr/README.md)

## 2. Architectural representation

| View | Question | Audience | Document |
|---|---|---|---|
| Scenarios (+1) | What does the robot do, for whom? | Everyone | [01](01-scenarios-view.md) |
| Logical | Which abstractions exist and how do they relate? | Developers | [02](02-logical-view.md) |
| Process | Which processes and threads run, and how do they talk? | Integrators | [03](03-process-view.md) |
| Development | How is the code organised, built and tested? | Developers | [04](04-development-view.md) |
| Physical | On which hardware is it deployed and how is it wired? | Builders | [05](05-physical-view.md) |

**Style: ports and adapters (hexagonal architecture).** The mission logic and the vision algorithms
depend on small interfaces (`ports.py`, `interfaces.h`). OpenCV capture, named pipes, pyserial, LEDC PWM
and WebSockets are adapters plugged in by a composition root. This is the approach used in professional
robotics and embedded code (e.g. ROS 2 nodes separate algorithms from I/O; Grenning, *TDD for Embedded C*;
Martin, *Clean Architecture*) because it lets the logic be tested without the robot.
See [ADR-0002](adr/0002-ports-and-adapters.md).

## 3. Goals and constraints

| Goal / constraint | Consequence |
|---|---|
| Behaviour must not change (it placed 5th at TMR 2026) | Golden tests against the original code ([ADR-0004](adr/0004-golden-tests.md)); wire protocol unchanged ([ADR-0006](adr/0006-keep-wire-protocol.md)) |
| Test without the robot | Pure FSM with injected clock ([ADR-0003](adr/0003-pure-state-machine.md)); firmware logic without Arduino headers ([ADR-0005](adr/0005-host-testable-firmware.md)) |
| Water is a hazard | Dedicated pipe and top priority in the FSM |
| Raspberry Pi 4 CPU | Simple HSV masks, no neural networks |
| Two processes already proven in competition | Kept: vision and master communicate through FIFOs ([ADR-0001](adr/0001-two-processes-and-fifos.md)) |

## 4. Architectural mechanisms

| Mechanism | Solution |
|---|---|
| Configuration | Frozen dataclasses in `config.py`; `config.h` in the firmware |
| Dependency injection | Constructor injection in `apps/vision_app.py`, `apps/master_app.py`, `kata_firmware.ino` |
| Inter-process communication | Two FIFOs with a text protocol defined in one module (`domain/messages.py`) |
| Pi ↔ ESP32 communication | UART text lines (`domain/commands.py` ↔ `CommandProcessor`) |
| Time | Passed in as `now`; only the composition root reads the clock |
| Logging | Python `logging`; `ILog` in the firmware |
| Fault recovery | Serial watchdog, camera re-open, pipe re-open, stale-data timeout, stuck escape |

## 5. Size and performance

| Item | Value |
|---|---|
| Vision | 640×480 @ 20 fps, 3 HSV masks per frame |
| Control loop | 12.5 Hz (80 ms), 20 Hz while reacting to water |
| Python package | ~1,300 lines; firmware ~360 lines |

## 6. Quality

| Attribute | Tactic | Evidence |
|---|---|---|
| Correctness of refactor | Golden tests | `tests/test_golden_*.py` |
| Testability | Ports, fakes, injected clock | 24 Python tests + firmware tests, no hardware |
| Modifiability | One detector / behaviour / adapter per module | [06-solid-principles.md](06-solid-principles.md) |
| Safety | Water priority, stale-data timeout, clean shutdown | NFR-01..03 |
