// Differential drive (two wheels) and conveyor belt.
#pragma once

#include "interfaces.h"

int clampDuty(int value, int lo, int hi);

class DriveTrain {
 public:
  DriveTrain(IMotor& left, IMotor& right, ILog& log) : left_(left), right_(right), log_(log) {}

  void forward(int right, int left);
  void back(int right, int left);
  void spinRight(int right, int left);
  void spinLeft(int right, int left);
  void stop();
  // Independent wheel duties, already in range.
  void differential(int left, int right);

 private:
  IMotor& left_;
  IMotor& right_;
  ILog& log_;
};

class Belt {
 public:
  Belt(IMotor& motor, ILog& log) : motor_(motor), log_(log) {}
  void run(int speed);   // the belt is mounted reversed: runs at -speed
  void stop();

 private:
  IMotor& motor_;
  ILog& log_;
};
