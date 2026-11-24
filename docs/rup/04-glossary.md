# Glossary

| Term | Meaning |
|---|---|
| **4+1 view model** | Architecture described by logical, process, development and physical views, tied together by scenarios (Kruchten, 1995). The architectural representation used by RUP. |
| **ADR** | Architecture Decision Record: short document with context, decision and consequences (M. Nygard). |
| **Adapter** | Concrete implementation of a port for one technology (OpenCV camera, FIFO, pyserial, LEDC PWM). |
| **Composition root** | The single place where concrete objects are created and wired (`apps/*.py`, `kata_firmware.ino`). |
| **FIFO / named pipe** | Linux file used to stream text lines between the vision and master processes. |
| **FSM** | Finite state machine: the mission logic in `control/fsm.py`. |
| **Golden test** | Test comparing the new code with a trusted reference implementation on identical inputs. |
| **HSV** | Hue-Saturation-Value colour space; makes colour thresholds robust to brightness. |
| **Hysteresis** | Different on/off thresholds so a signal does not flicker near the limit. |
| **Kalman filter (1D)** | Recursive estimator used to smooth the lateral error. |
| **Lateral error** | Horizontal position of the target in [-1, 1]; 0 inside the central dead zone. |
| **LEDC** | ESP32 peripheral that generates PWM. |
| **PD controller** | Proportional-derivative steering correction. |
| **Port** | Interface the application depends on (`ports.py`, `interfaces.h`). |
| **S pattern** | Search manoeuvre: straight, curve, straight, curve to the other side. |
| **TMR** | Torneo Mexicano de Robótica (Mexican Robotics Tournament). |
