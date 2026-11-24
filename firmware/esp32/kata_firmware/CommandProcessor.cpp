#include "CommandProcessor.h"

#include <cctype>
#include <cstdio>
#include <cstdlib>

namespace {
std::string fmt(const char* pattern, int a) {
  char buf[64];
  std::snprintf(buf, sizeof(buf), pattern, a);
  return buf;
}
}  // namespace

std::string CommandProcessor::driveReply(const char* label, const char* sep) {
  char buf[64];
  std::snprintf(buf, sizeof(buf), "32%s:%s%dI%d\n", label, sep, tuning_.rightSpeed, tuning_.leftSpeed);
  return buf;
}

std::string CommandProcessor::adjust(int& value, int delta, const char* label) {
  value = clampDuty(value + delta, 0, 255);
  return std::string(label) + fmt("%d\n", value);
}

std::string CommandProcessor::adjustKp(float delta, const char* label) {
  tuning_.kp += delta;
  char buf[32];
  std::snprintf(buf, sizeof(buf), "%.2f\n", tuning_.kp);
  return std::string(label) + buf;
}

std::string CommandProcessor::handleManual(const std::string& c) {
  Tuning& t = tuning_;
  const int step = config::kSpeedStep;

  // Driving and wheel tuning: manual mode only.
  if (manual_) {
    if (c == "R") { drive_.spinRight(t.rightSpeed, t.leftSpeed); return driveReply("Right", " "); }
    if (c == "L") { drive_.spinLeft(t.rightSpeed, t.leftSpeed); return driveReply("Left", " "); }
    if (c == "F") { drive_.forward(t.rightSpeed, t.leftSpeed); return driveReply("Forward", " D"); }
    if (c == "B") { drive_.back(t.rightSpeed, t.leftSpeed); return driveReply("Back", " "); }
    if (c == "S") { drive_.stop(); return driveReply("STOP", " "); }
    if (c == "W") return adjust(t.rightSpeed, step, "SUBIENDO_Velocidad a: ");
    if (c == "X") return adjust(t.rightSpeed, -step, "Bajando_Velocidad a: ");
    if (c == "P") return adjust(t.leftSpeed, step, "SUBIENDO_Velocidad izq a: ");
    if (c == "\xC3\x91") return adjust(t.leftSpeed, -step, "Bajando_Velocidad  izq a: ");   // "Ñ"
    if (c == "K") return adjustKp(config::kKpStep, "SUBIENDO_K a: ");
    if (c == "k") return adjustKp(-config::kKpStep, "BAJANDO_K a: ");
  }

  // Belt, base speed and mode switch: always available.
  if (c == "J") { belt_.run(t.beltSpeed); return fmt("32activandoBANDAS:%d\n", t.beltSpeed); }
  if (c == "M") { belt_.stop(); return fmt("32StopBandas: %d\n", t.beltSpeed); }
  if (c == "Q") return adjust(t.beltSpeed, step, "SUBIENDO_Velocidad BANDA a: ");
  if (c == "A") return adjust(t.beltSpeed, -step, "Bajando_Velocidad BANDA a: ");
  if (c == "Y") return adjust(t.baseSpeed, step, "SUBIENDO_Velocidad BASE a: ");
  if (c == "T") return adjust(t.baseSpeed, -step, "Bajando_Velocidad BASE a: ");
  if (c == "Z") {
    manual_ = !manual_;
    drive_.stop();
    return driveReply("STOP", " ");
  }
  return "ERROR \n";
}

void CommandProcessor::handleAutonomous(const std::string& line) {
  if (manual_ || line.empty()) return;

  if (std::isdigit(static_cast<unsigned char>(line[0])) || line[0] == '-') {
    const float error = std::strtof(line.c_str(), nullptr);
    const int correction = static_cast<int>(error * tuning_.kp);
    const int right = clampDuty(tuning_.baseSpeed + correction, 0, 255);
    const int left = clampDuty(tuning_.baseSpeed - correction, 0, 255);
    drive_.differential(left, right);
  } else if (line == "N") {
    drive_.spinRight(tuning_.baseSpeed, tuning_.baseSpeed);
  } else if (line == "S") {
    drive_.stop();
  }
  // Other master commands (F, CR, CL, BL, BK, BA, DO, DC, J, M) are not
  // implemented in this firmware version: see docs/architecture/03-process-view.md.
}
