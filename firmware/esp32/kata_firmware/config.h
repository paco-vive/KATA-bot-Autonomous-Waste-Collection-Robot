// KATA-bot ESP32 firmware: pins and default tuning.
#pragma once

#include <stdint.h>

namespace config {

// H-bridge inputs (PWM on both inputs of each channel)
constexpr uint8_t kLeftIn1 = 18;
constexpr uint8_t kLeftIn2 = 19;
constexpr uint8_t kRightIn1 = 21;
constexpr uint8_t kRightIn2 = 22;
constexpr uint8_t kBeltIn1 = 16;
constexpr uint8_t kBeltIn2 = 17;

// LEDC PWM
constexpr uint32_t kPwmFrequencyHz = 5000;
constexpr uint8_t kPwmResolutionBits = 8;   // duty 0..255

// Serial link to the Raspberry Pi (shared with the USB console)
constexpr uint32_t kUartBaud = 115200;

// WebSocket manual control
constexpr uint16_t kWebSocketPort = 81;

// Default tuning (TMR 2026 values)
constexpr float kDefaultKp = 4.5f;
constexpr int kDefaultBaseSpeed = 155;
constexpr int kDefaultBeltSpeed = 80;
constexpr int kSpeedStep = 10;
constexpr float kKpStep = 0.1f;

}  // namespace config

// Wi-Fi access point credentials. Override them without touching git:
// copy secrets.example.h to secrets.h (ignored by git) and edit it.
#if __has_include("secrets.h")
#include "secrets.h"
#else
#define KATA_AP_SSID "ESP32_CHAT"
#define KATA_AP_PASSWORD "12345678"
#endif
