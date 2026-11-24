// KATA-bot ESP32 firmware (Arduino IDE, ESP32 core 3.x).
//
// Composition root: creates the Arduino adapters (PWM motors, Serial log,
// Wi-Fi AP, WebSocket server) and wires them to the pure logic in
// DriveTrain / CommandProcessor.
//
// Library: "WebSockets" by Markus Sattler (Library Manager).

#include <WiFi.h>
#include <WebSocketsServer.h>

#include <string>

#include "CommandProcessor.h"
#include "DriveTrain.h"
#include "config.h"

// ---------------------------------------------------------------- adapters
class LedcHBridge : public IMotor {
 public:
  LedcHBridge(uint8_t in1, uint8_t in2) : in1_(in1), in2_(in2) {}

  void begin() {
    ledcAttach(in1_, config::kPwmFrequencyHz, config::kPwmResolutionBits);
    ledcAttach(in2_, config::kPwmFrequencyHz, config::kPwmResolutionBits);
    setDuty(0);
  }

  void setDuty(int duty) override {
    duty = clampDuty(duty, -255, 255);
    ledcWrite(in1_, duty >= 0 ? duty : 0);
    ledcWrite(in2_, duty >= 0 ? 0 : -duty);
  }

 private:
  uint8_t in1_;
  uint8_t in2_;
};

class SerialLog : public ILog {
 public:
  void line(const char* text) override { Serial.println(text); }
};

// ------------------------------------------------------------ composition
LedcHBridge leftMotor(config::kLeftIn1, config::kLeftIn2);
LedcHBridge rightMotor(config::kRightIn1, config::kRightIn2);
LedcHBridge beltMotor(config::kBeltIn1, config::kBeltIn2);
SerialLog serialLog;
DriveTrain drive(leftMotor, rightMotor, serialLog);
Belt belt(beltMotor, serialLog);
CommandProcessor commands(drive, belt);
WebSocketsServer webSocket(config::kWebSocketPort);

void onWebSocketEvent(uint8_t client, WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      webSocket.sendTXT(client, "Bienvenido al servidor ESP32");
      break;
    case WStype_TEXT: {
      std::string cmd(reinterpret_cast<char*>(payload), length);
      String ack = "Recibí tu letra: ";
      ack += cmd.c_str();
      webSocket.sendTXT(client, ack);
      std::string reply = commands.handleManual(cmd);
      webSocket.sendTXT(client, reply.c_str());
      break;
    }
    default:
      break;
  }
}

void setup() {
  Serial.begin(config::kUartBaud);
  leftMotor.begin();
  rightMotor.begin();
  beltMotor.begin();

  WiFi.softAP(KATA_AP_SSID, KATA_AP_PASSWORD);
  webSocket.begin();
  webSocket.onEvent(onWebSocketEvent);
}

void loop() {
  webSocket.loop();

  if (!commands.manualMode() && Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    commands.handleAutonomous(line.c_str());
  }
}
