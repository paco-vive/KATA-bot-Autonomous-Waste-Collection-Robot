// Small abstractions so the control logic does not depend on Arduino APIs
// (Dependency Inversion). The Arduino implementations live in the .ino;
// firmware/test provides fakes and runs the logic on a PC.
#pragma once

class IMotor {
 public:
  virtual ~IMotor() = default;
  // Signed duty: -255 (full reverse) .. 255 (full forward).
  virtual void setDuty(int duty) = 0;
};

class ILog {
 public:
  virtual ~ILog() = default;
  virtual void line(const char* text) = 0;
};
