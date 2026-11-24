# Vision

| Field | Value |
|---|---|
| Product | KATA-bot, autonomous waste-collection robot |
| Context | Mexican Robotics Tournament (TMR), "Beach Can Collection" category |
| Result | 5th place nationally, TMR 2026 |
| Version | 2.0 (architecture refactor of the TMR 2026 code, same behaviour) |

## 1. Problem statement

| | |
|---|---|
| **The problem of** | collecting cans scattered on a beach without human control |
| **affects** | competition teams, and in the long run beach-cleaning efforts |
| **whose impact is** | a robot must see small dark objects on bright sand, avoid water and return its load to a deposit |
| **a successful solution** | finds, collects and deposits cans autonomously, never drives into water, and can be understood, rebuilt and improved by the next team |

## 2. Stakeholders

| Stakeholder | Interest |
|---|---|
| Competition team (12 students, UDLAP) | A reliable robot on competition day |
| Next generation of the team | Understand, replicate and improve the robot |
| Judges / reviewers / recruiters | Engineering quality, traceability |
| Supervisor | Academic rigour and documentation |

## 3. Product overview

A Raspberry Pi 4 runs two Python processes: **vision** (OpenCV) and **master** (mission state machine).
An ESP32 drives the wheels and the conveyor belt, and also offers **manual control** over Wi-Fi from a phone.

## 4. Scope

**In scope:** can, deposit-ring and water detection; mission state machine; PD steering; stuck recovery;
water avoidance; manual WebSocket control; tests that run without the robot.

**Out of scope (v2):** mapping/SLAM, obstacle sensors (ultrasonic), a second camera, telemetry logging
to file. The firmware header listed these as future ideas; the architecture leaves extension points for them
(see the logical view §5).

## 5. Constraints

- Raspberry Pi 4, Python ≥ 3.9, OpenCV ≥ 4.5; ESP32 with Arduino core 3.x.
- One USB camera at 640×480 / 20 fps.
- UART at 115200 baud between Pi and ESP32.
- Sand, direct sunlight and water in the arena.
