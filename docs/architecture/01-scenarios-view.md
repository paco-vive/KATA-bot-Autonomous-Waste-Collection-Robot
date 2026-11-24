# Scenarios view (+1)

## Use-case diagram

```mermaid
flowchart LR
    OP((Operator))
    ARENA((Arena:<br/>cans, ring, water))
    subgraph K[KATA-bot]
        UC1([UC-01 Collect a can])
        UC2([UC-02 Deposit the load])
        UC3([UC-03 Avoid water])
        UC4([UC-04 Recover when stuck])
        UC5([UC-05 Drive manually])
        UC6([UC-06 Start and stop the mission])
    end
    OP --> UC6
    OP --> UC5
    ARENA --> UC1
    ARENA --> UC2
    ARENA --> UC3
    UC1 -. extends .-> UC4
    UC2 -. extends .-> UC4
```

## UC-01 Collect a can

| | |
|---|---|
| Precondition | Vision and master running; ESP32 in autonomous mode (`Z`) |
| Main flow | 1. S-pattern search. 2. Vision reports `CAN:<err>`. 3. Master starts the belt (`J`) and steers with PD. 4. The can leaves the view after ≥ 4 centred frames. 5. Stop, count +1, pause 2 s, stop the belt (`M`), search again. |
| Alternative | The can disappears before being centred: stop the belt, back to search. |
| Requirements | FR-01, 02, 05, 06, 07, 08, 14 |

```mermaid
sequenceDiagram
    autonumber
    participant CAM as Camera
    participant V as vision (VisionPipeline)
    participant P as FIFO error_tracking
    participant M as master (BeachBotFsm)
    participant E as ESP32 (CommandProcessor)
    CAM->>V: frame
    V->>P: CAN:-0.310
    M->>P: latest_target()
    M->>M: SEARCHING → APPROACHING
    M->>E: J (belt on)
    loop every 80 ms while the can is visible
        V->>P: CAN:<err>
        M->>M: Kalman + PD
        M->>E: <correction> e.g. -7.44
        E->>E: left = base − Kp·err, right = base + Kp·err
    end
    V->>P: N (can under the robot)
    M->>M: 10 lost frames, centred ≥ 4 → REACHED_CAN
    M->>E: S, … , M
```

## UC-02 Deposit the load

After `cans_per_deposit` cans: S-pattern search for the red ring → approach with PD until the ring is
≥ 100 px wide → curve right 3 s, back-left 1 s ("trailer" manoeuvre) → open the door (`DO`), back-left
2 s, close (`DC`) → search again. Requirements FR-03, FR-09.

## UC-03 Avoid water

```mermaid
stateDiagram-v2
    [*] --> AnyMovingState
    AnyMovingState --> AVOIDING_WATER: W:L / W:R / W:C
    AVOIDING_WATER --> AVOIDING_WATER: 0–0.4 s stop, then back away from the water side
    AVOIDING_WATER --> AVOIDING_WATER: after 3.4 s alternate BK/BA every 1 s (rocking)
    AVOIDING_WATER --> WATER_CLEAR_BACK: clear and ≥ 1.5 s
    AVOIDING_WATER --> SEARCHING: 8 s timeout
    WATER_CLEAR_BACK --> SEARCHING: back 2 s + turn away 2.5 s
```

Requirements FR-04, FR-10, NFR-01.

## UC-04 Recover when stuck

If the same command is sent for 40 s in a moving state: alternate back/forward every 0.2 s for 1.2 s,
then curve right for 1 s, then resume. Requirement FR-11.

## UC-05 Drive manually

The operator joins the ESP32 access point and sends one-letter commands over WebSocket (port 81).

| Key | Action | Key | Action |
|---|---|---|---|
| F / B / L / R / S | forward, back, spin left, spin right, stop | W / X | right speed ±10 |
| P / Ñ | left speed ±10 | K / k | Kp ±0.1 |
| J / M | belt on / off | Q / A | belt speed ±10 |
| Y / T | base speed ±10 | Z | toggle manual ↔ autonomous |

Driving keys and wheel tuning answer `ERROR` in autonomous mode. Requirements FR-12, FR-13.

## UC-06 Start and stop the mission

Start `vision.py` (creates the FIFOs and calibrates), then `maestro.py` (waits for the first vision data,
sends `S`, `M`, starts searching). Ctrl+C or SIGTERM sends `S`/`M` three times and closes the port. FR-15.
