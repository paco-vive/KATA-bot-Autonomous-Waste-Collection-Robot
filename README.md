# 🤖 KATA-bot: Autonomous Waste Collection Robot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C++-Solutions-orange.svg)](https://isocpp.org/)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20RPi%204-red.svg)]()

**KATA-bot** es un robot autónomo desarrollado para el **Torneo Mexicano de Robótica (TMR)** en la categoría de "Limpieza de Playa". Este proyecto integra visión artificial, sistemas embebidos de alta potencia y telemetría en tiempo real.

---

## 📸 Galería del Proyecto

### Desarrollo y Hardware
| Foto 1: Prototipo General | Foto 2: Electrónica/Chasis |
|---|---|
| <img src="assets/foto1.jpg" width="400"> | <img src="assets/foto2.jpg" width="400"> |
| Foto 3: Pruebas en Campo | Foto 4: Equipo de Trabajo |
| <img src="assets/foto3.jpg" width="400"> | <img src="assets/foto4.jpg" width="400"> |

### Demos en Video
Aquí puedes ver al KATA-bot en acción:

#### 1. Prueba de Navegación Autónoma
https://github.com/paco-vive/KATA-bot/assets/video1.mp4

#### 2. Detección de Objetos (OpenCV)
https://github.com/paco-vive/KATA-bot/assets/video2.mp4

#### 3. Control vía WebServer (ESP32)
https://github.com/paco-vive/KATA-bot/assets/video3.mp4

---

## 🛠️ Especificaciones Técnicas

* **Visión Artificial:** Pipeline en **Raspberry Pi 4** con OpenCV para detección de latas mediante filtrado HSV.
* **Arquitectura Embebida:** Sistema robusto basado en **ESP32**, utilizando optoacopladores para protección de drivers y relevadores para gestión de potencia.
* **Control de Motores:** Algoritmos de control de velocidad y dirección mediante PWM.
* **Interfaz de Usuario:** Servidor local HTML/WebSocket integrado en el ESP32 para telemetría y control remoto de baja latencia.
* **Monitoreo:** Acceso remoto vía VNC/SSH para debugging en tiempo real.

## 👥 Liderazgo y Gestión
Como **Project Lead**, coordiné a un equipo multidisciplinario de 12 personas, gestionando desde el diseño mecánico en CAD hasta la integración de software y electrónica durante los ciclos 2025-2026.

## 🚀 Instalación rápida
1. Clona el repositorio: `git clone https://github.com/paco-vive/KATA-bot.git`
2. Instala dependencias en tu RPi: `pip install opencv-python numpy`
3. Carga el firmware en el ESP32 usando Arduino IDE (carpeta `/firmware`).

---

## 👨‍💻 Contacto
**Francisco Viveros Mendoza** *Ingeniería en Robótica y Telecomunicaciones - UDLAP* [LinkedIn](https://www.linkedin.com/in/francisco-viveros-mendoza-a20a06328/) | [GitHub](https://github.com/paco-vive) | [Portfolio](https://urbanos.vercel.app/)
