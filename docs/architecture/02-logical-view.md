# Logical view

## 1. Layers

```mermaid
flowchart TB
    subgraph Apps[Composition roots]
        VA[apps/vision_app.py]
        MA[apps/master_app.py]
        INO[kata_firmware.ino]
    end
    subgraph Adapters[Adapters: I/O technologies]
        CAMA[OpenCvCamera]
        FIFO[FifoPublisher / FifoSubscriber]
        SER[SerialMotorLink]
        DBG[DebugView]
        LEDC[LedcHBridge · SerialLog · WebSocketsServer]
    end
    subgraph Core[Core: no I/O]
        PORTS[[ports.py · interfaces.h]]
        VIS[vision: VisionPipeline, detectors, calibration, geometry]
        CTRL[control: BeachBotFsm, SPattern, StuckDetector, TargetTracker]
        DOM[domain: Detection, WaterStatus, Cmd]
        FW[firmware: CommandProcessor, DriveTrain, Belt]
    end
    VA --> CAMA & FIFO & DBG & VIS
    MA --> FIFO & SER & CTRL
    INO --> LEDC & FW
    CAMA & FIFO & SER -. implement .-> PORTS
    LEDC -. implements .-> PORTS
    VIS --> DOM
    CTRL --> DOM
```

Dependencies always point inward. `control/` and `domain/` import nothing from OpenCV, pyserial or the OS;
`CommandProcessor` and `DriveTrain` include no Arduino header.

## 2. Raspberry Pi classes

```mermaid
classDiagram
    direction LR
    class Camera {
        <<Protocol>>
        +read()
        +reopen()
        +release()
    }
    class DetectionPublisher {
        <<Protocol>>
        +publish_water(WaterStatus)
        +publish_target(Detection)
    }
    class DetectionSource {
        <<Protocol>>
        +latest_target(now) Detection
        +latest_water() WaterStatus
        +has_data()
        +alive
    }
    class MotorLink {
        <<Protocol>>
        +send(cmd)
        +close()
    }

    class VisionPipeline {
        +process(frame) VisionResult
    }
    class CanDetector {
        +detect(hsv, v_thr) BBox
    }
    class RingDetector {
        +detect(hsv) BBox
    }
    class WaterDetector {
        +detect(hsv) WaterReading
    }
    class BlackThreshold {
        +for_frame(hsv) int
    }
    class BeachBotFsm {
        +state: State
        +tick(now, Detection, WaterStatus) TickResult
    }
    class TargetTracker {
        +update(err, dt) tuple
    }
    class SPattern {
        +update(now) cmd
    }
    class StuckDetector {
        +is_stuck(cmd, state, now)
        +step(now)
    }
    class Detection {
        kind
        error
        width
        +encode() str
        +decode(line)$ Detection
    }
    class WaterStatus {
        detected
        side
        +encode() str
        +next(line) WaterStatus
    }

    VisionPipeline *-- CanDetector
    VisionPipeline *-- RingDetector
    VisionPipeline *-- WaterDetector
    VisionPipeline --> BlackThreshold
    VisionPipeline ..> Detection
    BeachBotFsm *-- "2" TargetTracker
    BeachBotFsm *-- SPattern
    BeachBotFsm *-- StuckDetector
    BeachBotFsm ..> Detection
    OpenCvCamera ..|> Camera
    FifoPublisher ..|> DetectionPublisher
    FifoSubscriber ..|> DetectionSource
    SerialMotorLink ..|> MotorLink
```

## 3. Firmware classes

```mermaid
classDiagram
    class IMotor {
        <<interface>>
        +setDuty(int)
    }
    class ILog {
        <<interface>>
        +line(text)
    }
    class DriveTrain {
        +forward()
        +back()
        +spinRight()
        +spinLeft()
        +stop()
        +differential(l, r)
    }
    class Belt {
        +run(speed)
        +stop()
    }
    class CommandProcessor {
        +handleManual(cmd) string
        +handleAutonomous(line)
        +manualMode()
    }
    class Tuning {
        kp
        baseSpeed
        rightSpeed
        leftSpeed
        beltSpeed
    }
    LedcHBridge ..|> IMotor
    FakeMotor ..|> IMotor
    SerialLog ..|> ILog
    DriveTrain --> "2" IMotor
    Belt --> IMotor
    CommandProcessor --> DriveTrain
    CommandProcessor --> Belt
    CommandProcessor *-- Tuning
```

## 4. Mission state machine

```mermaid
stateDiagram-v2
    [*] --> SEARCHING
    SEARCHING --> APPROACHING: can detected
    APPROACHING --> REACHED_CAN: lost after ≥ 4 centred frames
    APPROACHING --> SEARCHING: lost, not centred
    REACHED_CAN --> SEARCHING: 2 s, load not full
    REACHED_CAN --> SEARCHING_RED: 2 s, load full
    SEARCHING_RED --> APPROACHING_RED: ring detected
    APPROACHING_RED --> SEARCHING_RED: ring lost
    APPROACHING_RED --> TURNING_TO_DEPOSIT: width ≥ 100 px
    TURNING_TO_DEPOSIT --> DEPOSITING: 3 s curve + 1 s back
    DEPOSITING --> SEARCHING: door 2 s
    AVOIDING_WATER --> WATER_CLEAR_BACK: clear ≥ 1.5 s
    AVOIDING_WATER --> SEARCHING: 8 s timeout
    WATER_CLEAR_BACK --> SEARCHING: 4.5 s
    note right of AVOIDING_WATER: entered from any interruptible state when water is seen
```

## 5. Extension points

| To add… | Write | Untouched |
|---|---|---|
| A second camera (e.g. blue/water) | Another `Camera` adapter + detector | FSM |
| Ultrasonic obstacle sensor | A detector or a new field in the observation; one new FSM priority | Vision, firmware |
| Logging every message to a `.txt` | A `MotorLink` decorator that writes then forwards | FSM, serial adapter |
| ROS 2 instead of FIFOs | `DetectionPublisher` / `DetectionSource` over topics | Vision algorithms, FSM |
| Door servo / missing commands in firmware | Handlers in `CommandProcessor::handleAutonomous` + an `IServo` port | Pi software |
| Different motor driver | Another `IMotor` | `CommandProcessor` |
