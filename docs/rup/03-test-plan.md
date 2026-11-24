# Test Plan

## 1. Strategy

| Level | Scope | Tool | Runs on |
|---|---|---|---|
| Unit | Protocol, filters, behaviours, FSM transitions | pytest | PC |
| Golden (regression) | Refactored code vs the TMR 2026 reference code, same inputs | pytest + `tests/reference/` | PC |
| Vision (synthetic) | Detectors on generated images | pytest + OpenCV | PC |
| Firmware unit | `CommandProcessor`, `DriveTrain` with fake motors | g++ + ASan/UBSan | PC |
| Field | Whole robot in sand and water | Checklist §4 | Arena |

Run everything with `make test`.

## 2. Golden tests

`tests/test_golden_fsm.py` drives the original `maestro.py` (v8) and the new package with the **same
simulated clock and the same input timeline**, and requires the exact same list of
`(time, command)` pairs. Scenarios: can pick-up, full deposit cycle, water on the left then clear,
persistent water (rocking + timeout), 50 s of nothing (stuck escape), noisy can with dropouts.

`tests/test_golden_vision.py` compares `lateral_error`, the can shape filter (300 random contours)
and the threshold calibration with the original `vision.py` functions.

## 3. Test cases → requirements

| Test | Requirements |
|---|---|
| `test_messages.py` | Protocol for FR-01..04, NFR-03 |
| `test_control.py::test_water_interrupts_approach` | FR-10, NFR-01 |
| `test_control.py::test_reached_can_and_deposit_cycle` | FR-08, FR-09 |
| `test_control.py::test_missed_can_returns_to_search_and_stops_belt` | FR-08 |
| `test_control.py::test_stuck_detector_only_in_active_states` | FR-11 |
| `test_golden_fsm.py` (6 scenarios) | FR-06..11, NFR-07 |
| `test_golden_vision.py` | FR-01, FR-02, FR-04, FR-05, NFR-07 |
| `firmware/test` | FR-12..14 |

## 4. Field checklist

| # | Step | Expected |
|---|---|---|
| F-1 | Start `vision.py`, then `maestro.py` | Master logs "SEARCHING"; robot starts the S pattern |
| F-2 | Place a can 1 m ahead | Belt starts (`J`), robot centres and drives over it, pauses 2 s |
| F-3 | Put a blue tarp on one side | Robot stops and backs away from that side |
| F-4 | Block the wheels for 45 s while searching | Wiggle back/forward, then curve |
| F-5 | Unplug and replug the UART cable | "Serial link down, reconnecting", then resumes |
| F-6 | Connect a phone to the AP, open the control page, send `Z` then `F` | `F` answers `ERROR` in autonomous mode; after `Z` again it drives |
| F-7 | Ctrl+C on the master | Wheels and belt stop |
