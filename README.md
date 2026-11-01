# 🤖 KATA-bot: Autonomous Waste Collection Robot

> 🏆 **5th place nationally, Mexican Robotics Tournament (TMR) 2026, "Beach Can Collection" category**

<p align="center"><img src="assets/video1.gif" width="480"></p>

**What it does:** KATA-bot drives on sand by itself. It finds cans with a camera, collects them, carries them to the red deposit ring and unloads them, and it backs away from water.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C++-Solutions-orange.svg)](https://isocpp.org/)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20RPi%204-red.svg)]()

**KATA-bot** is an advanced autonomous robotics platform developed for the **Mexican Robotics Tournament (TMR)** in the "Beach Can Collection" category. This project integrates real-time computer vision, robust embedded systems architecture, and wireless telemetry to solve environmental cleanup challenges.

---

## 📸 Project Gallery

### Hardware & Development
 <img src="assets/foto1.jpg" width="400">  <img src="assets/foto2.jpg" width="400"> 
 <img src="assets/foto3.jpg" width="400">  <img src="assets/foto4.png" width="400"> 

### 📹 Technical Demos
Watch KATA-bot in action:

#### 1. Autonomous Navigation & Pathfinding
| <img src="assets/video1.gif" width="400"> | <img src="assets/video3.gif" width="400"> |

#### 2. Computer Vision Pipeline (OpenCV Detection)
<img src="assets/video2.gif" width="400">

#### 3. Remote Wifi WebSocket ESP-32 Server FULL CONTROL 
<img src="assets/video4.gif" width="400">

---

## 🛠️ Technical Specifications

* **Computer Vision:** Real-time processing on **Raspberry Pi 4** using OpenCV for target detection through HSV color filtering and contour analysis.
* **Embedded Architecture:** Robust dual-unit system using **ESP32 MCUs** with opto-isolators for driver protection and relay-based power management for high-torque motors.
* **Web-Based Control:** Custom **WebSocket-based HTML interface** hosted locally on the ESP32, enabling real-time manual override and telemetry.
* **Remote Monitoring:** Established wireless remote access via **VNC/SSH** for system debugging and live camera feed visualization.
* **Power Systems:** Managed high-current DC motor draws with a custom-engineered electronic safety layer.

## 🧭 System Architecture

```mermaid
flowchart LR
    CAM[Camera] --> V["Raspberry Pi 4<br/>vision.py<br/>OpenCV HSV detection"]
    V -- "/tmp/error_tracking<br/>CAN / RED / N" --> M["maestro.py<br/>State machine + Kalman 1D<br/>+ PD + stuck detector"]
    V -- "/tmp/water_alert<br/>W:L / W:R / W:C / C" --> M
    M -- "UART /dev/serial0<br/>115200 baud" --> E["ESP32<br/>motor control<br/>WebSocket server"]
    E --> D[Opto-isolated drivers] --> MOT[DC motors]
```

- **vision.py** auto-calibrates the black threshold. It detects cans (black, validated by area and shape), the red deposit ring and water (blue pixel ratio with hysteresis, plus the side it is on), and writes the results to two named pipes.
- **maestro.py** runs the FSM at about 12 Hz. It smooths the centering error with a 1D Kalman filter and steers with a PD controller (Kp = 24, Kd = 5). A watchdog reconnects the serial link if it drops. A stuck detector backs up and escapes after the same command has been sent for 40 s.

## 🔁 State Machine (`maquina_de_estados()`)

```mermaid
stateDiagram-v2
    [*] --> SEARCHING
    SEARCHING --> APPROACHING: can detected
    APPROACHING --> REACHED_CAN: can lost after >=4 centered frames
    APPROACHING --> SEARCHING: can lost (not centered)
    REACHED_CAN --> SEARCHING: pause 2 s, cans < 40
    REACHED_CAN --> SEARCHING_RED: pause 2 s, cans = 40
    SEARCHING_RED --> APPROACHING_RED: red ring detected
    APPROACHING_RED --> SEARCHING_RED: ring lost
    APPROACHING_RED --> TURNING_TO_DEPOSIT: ring width >= 100 px
    TURNING_TO_DEPOSIT --> DEPOSITING: turn 3 s + back 1 s
    DEPOSITING --> SEARCHING: door open 2 s, close
    SEARCHING --> AVOIDING_WATER: water
    APPROACHING --> AVOIDING_WATER: water
    SEARCHING_RED --> AVOIDING_WATER: water
    APPROACHING_RED --> AVOIDING_WATER: water
    TURNING_TO_DEPOSIT --> AVOIDING_WATER: water
    WATER_CLEAR_BACK --> AVOIDING_WATER: water
    AVOIDING_WATER --> WATER_CLEAR_BACK: water clear (>=1.5 s)
    AVOIDING_WATER --> SEARCHING: timeout 8 s
    WATER_CLEAR_BACK --> SEARCHING: back 2 s + turn 2.5 s
```

While searching, the robot follows an S pattern (1.8 s straight, 1.5 s curve). Water has the highest priority and interrupts every state except REACHED_CAN, DEPOSITING and AVOIDING_WATER itself.

## 🔌 ESP32 Firmware (`firmware/esp32/kata_marzo/kata_marzo.ino`, Arduino IDE, C++)

- Creates its own Wi-Fi access point and a **WebSocket server on port 81** for full manual control from a phone or laptop.
- **Manual mode:** single-letter commands: `F/B/L/R/S` (drive), `W/X` and `P/Ñ` (right/left speed), `K/k` (adjust Kp), `J/M` (conveyor belt on/off), `Q/A` (belt speed), `Y/T` (base speed).
- **Autonomous mode** (toggled with `Z`): reads the centering error from the Raspberry Pi over UART (115200) and applies **proportional differential steering** (`Kp = 4.5`, base PWM 155). `N` makes it turn to search and `S` stops it.
- Drives two DC motors and the conveyor belt with 5 kHz, 8-bit LEDC PWM.

> This is the March–April 2026 version of the firmware. It was recovered from the editor history.

## 🔩 Hardware

| Component | Role |
|---|---|
| Raspberry Pi 4 | Vision (OpenCV) and high-level control |
| Camera (640×480 @ 20 fps) | Detects cans, the deposit ring and water |
| ESP32 | Motor control, WebSocket manual-control server |
| Opto-isolated motor drivers + relays | Driver protection and power management |
| High-torque DC motors | Drive system |

## ▶️ How to Run

Requirements: Raspberry Pi with Python 3.9+, `opencv-python`, `numpy`, `pyserial`, and UART enabled (`/dev/serial0`) and wired to the ESP32.

```bash
pip install opencv-python numpy pyserial

# Terminal 1: vision (creates the pipes and calibrates the camera)
python3 scripts/vision.py

# Terminal 2: master control (waits for the pipes, then starts the FSM)
python3 scripts/maestro.py
```

## 👥 Leadership & Management
**Team:** 12 students, UDLAP. **Supervisor:** Dra. Alejandra Hernández Sánchez. **My role:** Project Lead & Embedded Systems Developer (Jan 2025 – Jun 2026).

As **Project Lead**, I managed a multidisciplinary team of 12 engineers. My role focused on technical roadmapping, cross-departmental integration (Mechanics, Electronics, and Software), and rapid prototyping for the 2025 and 2026 competition cycles.

---

## 👨‍💻 About the Author
**Francisco Viveros Mendoza**
*B.S. in Robotics and Telecommunications Engineering - UDLAP*
[LinkedIn](https://www.linkedin.com/in/francisco-viveros-mendoza-a20a06328/) | [GitHub](https://github.com/paco-vive) | 
