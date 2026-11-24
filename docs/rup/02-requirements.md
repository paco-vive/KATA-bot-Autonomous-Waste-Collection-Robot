# Software Requirements Specification

## 1. Functional requirements

| ID | Requirement | Use case | Implemented in |
|---|---|---|---|
| FR-01 | Detect black cans in the lower 60 % of the image, validated by area, aspect, solidity, circularity and convexity | UC-01 | `vision/detectors.py` `CanDetector`, `can_shape_check` |
| FR-02 | Keep tracking the same can between frames (nearest centroid within 80 px) | UC-01 | `CanDetector._pick` |
| FR-03 | Detect the red deposit ring and report its width in pixels | UC-02 | `RingDetector` |
| FR-04 | Detect water (blue pixel ratio with hysteresis 15 % / 1.5 %) and the side it is on | UC-03 | `WaterDetector` |
| FR-05 | Recalibrate the black threshold at start-up from the scene brightness | UC-01 | `vision/calibration.py` |
| FR-06 | Search with an S pattern (1.8 s straight, 1.5 s curve, alternating side) | UC-01, UC-02 | `control/behaviours.py` `SPattern` |
| FR-07 | Approach a target with Kalman-filtered error and PD steering (Kp 24, Kd 5) | UC-01, UC-02 | `control/filters.py`, `fsm.py` |
| FR-08 | Count a can as collected when it leaves the view after ≥ 4 centred frames | UC-01 | `fsm.py` `_on_approaching` |
| FR-09 | After N cans (40), find the ring, turn, back up, open the door 2 s, close it | UC-02 | `fsm.py` deposit states |
| FR-10 | Water interrupts every moving state; back off away from it, then turn away | UC-03 | `fsm.py` water states |
| FR-11 | Detect 40 s of identical commands and escape (wiggle, then curve) | UC-04 | `StuckDetector` |
| FR-12 | Manual driving and tuning from a phone/laptop over WebSocket | UC-05 | `CommandProcessor::handleManual` |
| FR-13 | Switch between manual and autonomous mode with `Z` | UC-05 | `CommandProcessor` |
| FR-14 | In autonomous mode, apply proportional differential steering from UART numbers | UC-01 | `CommandProcessor::handleAutonomous` |
| FR-15 | On Ctrl+C / SIGTERM, stop the wheels and belt | UC-06 | `master_app.stop_robot` |

## 2. Non-functional requirements

| ID | Category | Requirement | How it is met |
|---|---|---|---|
| NFR-01 | Safety | Water has the highest priority over every other behaviour | Checked first in every tick; separate FIFO so it is never queued behind targets |
| NFR-02 | Robustness | Recover automatically from serial, camera and pipe failures | Serial watchdog, camera re-open, pipe re-open |
| NFR-03 | Robustness | Stale vision data (> 0.5 s) must not keep the robot steering | `FifoSubscriber.latest_target` returns "nothing" |
| NFR-04 | Performance | Control loop ≈ 12 Hz; vision ≈ 20 fps at 640×480 on a Pi 4 | `tick_period_s = 0.08`; HSV masks only |
| NFR-05 | Maintainability | All tunable values in one file | `src/kata_bot/config.py`, `firmware/.../config.h` |
| NFR-06 | Testability | Mission logic and firmware logic testable on a PC without hardware | Pure FSM with injected clock; firmware logic without Arduino headers |
| NFR-07 | Regression safety | The refactor must behave exactly like the TMR 2026 code | Golden tests against `tests/reference/` |
| NFR-08 | Replicability | A new team can rebuild and run the robot from this repository | Physical view, README quick start |
| NFR-09 | Security | Wi-Fi credentials not hard-coded in git for new deployments | `secrets.h` (git-ignored) override |

## 3. Traceability

Requirement → use case: table above. Use case → sequence: [scenarios view](../architecture/01-scenarios-view.md).
Requirement → test: [test plan](03-test-plan.md).
