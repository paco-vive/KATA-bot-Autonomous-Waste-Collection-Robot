# 🤖 KATA-bot: Autonomous Waste Collection Robot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C++-Solutions-orange.svg)](https://isocpp.org/)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20RPi%204-red.svg)]()

**KATA-bot** is an advanced autonomous robotics platform developed for the **Mexican Robotics Tournament (TMR)** in the "Beach Can Collection" category. This project integrates real-time computer vision, robust embedded systems architecture, and wireless telemetry to solve environmental cleanup challenges.

---

## 📸 Project Gallery

### Hardware & Development
| Photo 1: General Prototype | Photo 2: Electronics & Chassis |
|---|---|
| <img src="assets/foto1.jpg" width="400"> | <img src="assets/foto2.jpg" width="400"> |
| **Photo 3: Field Testing** | **Photo 4: Engineering Team** |
| <img src="assets/foto3.jpg" width="400"> | <img src="assets/foto4.jpg" width="400"> |

### 📹 Technical Demos
Watch KATA-bot in action:

#### 1. Autonomous Navigation & Pathfinding
assets/video1.mp4

#### 2. Computer Vision Pipeline (OpenCV Detection)
https://github.com/paco-vive/KATA-bot/assets/video2.mp4

#### 3. Low-Latency WebServer Control (ESP32/WebSockets)
https://github.com/paco-vive/KATA-bot/assets/video3.mp4

---

## 🛠️ Technical Specifications

* **Computer Vision:** Real-time processing on **Raspberry Pi 4** using OpenCV for target detection through HSV color filtering and contour analysis.
* **Embedded Architecture:** Robust dual-unit system using **ESP32 MCUs** with opto-isolators for driver protection and relay-based power management for high-torque motors.
* **Web-Based Control:** Custom **WebSocket-based HTML interface** hosted locally on the ESP32, enabling real-time manual override and telemetry.
* **Remote Monitoring:** Established wireless remote access via **VNC/SSH** for system debugging and live camera feed visualization.
* **Power Systems:** Managed high-current DC motor draws with a custom-engineered electronic safety layer.

## 👥 Leadership & Management
As **Project Lead**, I managed a multidisciplinary team of 12 engineers. My role focused on technical roadmapping, cross-departmental integration (Mechanics, Electronics, and Software), and rapid prototyping for the 2025 and 2026 competition cycles.

## 🚀 Quick Start
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/paco-vive/KATA-bot.git](https://github.com/paco-vive/KATA-bot.git)
    ```
2.  **Install dependencies (RPi):**
    ```bash
    pip install opencv-python numpy
    ```
3.  **Flash Firmware:**
    Open the `/firmware` folder in Arduino IDE and upload to the ESP32.

---

## 👨‍💻 About the Author
**Francisco Viveros Mendoza**
*B.S. in Robotics and Telecommunications Engineering - UDLAP*
[LinkedIn](https://www.linkedin.com/in/francisco-viveros-mendoza-a20a06328/) | [GitHub](https://github.com/paco-vive) | [Portfolio](https://urbanos.vercel.app/)
