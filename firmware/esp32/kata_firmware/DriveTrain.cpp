#include "DriveTrain.h"

int clampDuty(int value, int lo, int hi) {
  return value < lo ? lo : (value > hi ? hi : value);
}

void DriveTrain::forward(int right, int left) {
  left_.setDuty(left);
  right_.setDuty(right);
  log_.line("FORWARD");
}

void DriveTrain::back(int right, int left) {
  left_.setDuty(-left);
  right_.setDuty(-right);
  log_.line("BACK");
}

void DriveTrain::spinRight(int right, int left) {
  left_.setDuty(left);
  right_.setDuty(-right);
  log_.line("RIGHT");
}

void DriveTrain::spinLeft(int right, int left) {
  left_.setDuty(-left);
  right_.setDuty(right);
  log_.line("LEFT");
}

void DriveTrain::stop() {
  left_.setDuty(0);
  right_.setDuty(0);
  log_.line("STOP");
}

void DriveTrain::differential(int left, int right) {
  left_.setDuty(left);
  right_.setDuty(right);
}

void Belt::run(int speed) {
  motor_.setDuty(-speed);
  log_.line("BANDAS");
}

void Belt::stop() {
  motor_.setDuty(0);
  log_.line("STOP_BANDAS");
}
