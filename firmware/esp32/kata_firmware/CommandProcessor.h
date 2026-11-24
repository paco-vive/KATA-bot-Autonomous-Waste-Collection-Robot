// Interprets both command channels:
//   * WebSocket (manual mode): one-letter commands from the phone / laptop.
//   * UART (autonomous mode): steering corrections from the Raspberry Pi.
// Pure C++ (no Arduino headers), unit-tested in firmware/test.
#pragma once

#include <string>

#include "DriveTrain.h"
#include "config.h"

struct Tuning {
  float kp = config::kDefaultKp;
  int baseSpeed = config::kDefaultBaseSpeed;
  int rightSpeed = config::kDefaultBaseSpeed;   // manual mode, right wheel
  int leftSpeed = config::kDefaultBaseSpeed;    // manual mode, left wheel
  int beltSpeed = config::kDefaultBeltSpeed;
};

class CommandProcessor {
 public:
  CommandProcessor(DriveTrain& drive, Belt& belt) : drive_(drive), belt_(belt) {}

  // Manual channel. Returns the text reply for the client ("ERROR \n" if
  // the command is unknown or not allowed in the current mode).
  std::string handleManual(const std::string& cmd);

  // Autonomous channel: a number (steering error), "N" (spin to search) or "S" (stop).
  // Other lines are ignored. Does nothing while in manual mode.
  void handleAutonomous(const std::string& line);

  bool manualMode() const { return manual_; }
  const Tuning& tuning() const { return tuning_; }

 private:
  std::string adjust(int& value, int delta, const char* label);
  std::string adjustKp(float delta, const char* label);
  std::string driveReply(const char* label, const char* sep);

  DriveTrain& drive_;
  Belt& belt_;
  Tuning tuning_;
  bool manual_ = true;   // true: WebSocket drives; false: Raspberry Pi drives
};
