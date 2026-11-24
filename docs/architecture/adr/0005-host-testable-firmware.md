# ADR-0005: Firmware logic free of Arduino headers

**Status:** Accepted

## Context
The original sketch put command parsing, tuning, motor PWM and WebSocket handling in one file with
global variables. It could only be tested by flashing the ESP32.

## Decision
Split the sketch: `CommandProcessor` (command meaning, tuning) and `DriveTrain`/`Belt` (wheel and belt
duties) use only standard C++ and talk to hardware through `IMotor` and `ILog`. The `.ino` implements
those with LEDC PWM and `Serial`, and owns Wi-Fi and WebSocket.

## Consequences
- (+) `make -C firmware/test` checks the logic with ASan/UBSan on a PC.
- (+) Changing the motor driver or adding a servo means a new adapter class.
- (−) Small virtual-call overhead, negligible at these rates.
