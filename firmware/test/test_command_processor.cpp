// Host tests for the firmware logic: g++ on a PC, no ESP32 needed.
#include <cassert>
#include <cstdio>
#include <string>
#include <vector>

#include "../esp32/kata_firmware/CommandProcessor.h"

struct FakeMotor : IMotor {
  int duty = 0;
  void setDuty(int d) override { duty = d; }
};
struct FakeLog : ILog {
  std::vector<std::string> lines;
  void line(const char* t) override { lines.push_back(t); }
};

struct Rig {
  FakeMotor left, right, beltMotor;
  FakeLog log;
  DriveTrain drive{left, right, log};
  Belt belt{beltMotor, log};
  CommandProcessor cp{drive, belt};
};

static int failures = 0;
#define CHECK(c) do { if (!(c)) { std::printf("  FAIL %s:%d %s\n", __FILE__, __LINE__, #c); failures++; } } while (0)

static void manual_drive_and_replies() {
  Rig r;
  CHECK(r.cp.handleManual("F") == "32Forward: D155I155\n");
  CHECK(r.left.duty == 155 && r.right.duty == 155);
  CHECK(r.cp.handleManual("R") == "32Right: 155I155\n");
  CHECK(r.left.duty == 155 && r.right.duty == -155);
  CHECK(r.cp.handleManual("B") == "32Back: 155I155\n");
  CHECK(r.left.duty == -155 && r.right.duty == -155);
  CHECK(r.cp.handleManual("S") == "32STOP: 155I155\n");
  CHECK(r.left.duty == 0 && r.right.duty == 0);
  CHECK(r.log.lines.back() == "STOP");
}

static void speed_tuning_is_clamped() {
  Rig r;
  for (int i = 0; i < 20; i++) r.cp.handleManual("W");
  CHECK(r.cp.tuning().rightSpeed == 255);
  CHECK(r.cp.handleManual("\xC3\x91") == "Bajando_Velocidad  izq a: 145\n");
  CHECK(r.cp.handleManual("K") == "SUBIENDO_K a: 4.60\n");
  CHECK(r.cp.handleManual("?") == "ERROR \n");
}

static void belt_runs_reversed() {
  Rig r;
  CHECK(r.cp.handleManual("J") == "32activandoBANDAS:80\n");
  CHECK(r.beltMotor.duty == -80);
  CHECK(r.cp.handleManual("M") == "32StopBandas: 80\n");
  CHECK(r.beltMotor.duty == 0);
}

static void autonomous_mode() {
  Rig r;
  r.cp.handleAutonomous("10");             // ignored in manual mode
  CHECK(r.left.duty == 0);
  r.cp.handleManual("Z");
  CHECK(!r.cp.manualMode());
  CHECK(r.cp.handleManual("F") == "ERROR \n");   // driving disabled in autonomous mode
  r.cp.handleAutonomous("10");             // correction = int(10 * 4.5) = 45
  CHECK(r.right.duty == 200 && r.left.duty == 110);
  r.cp.handleAutonomous("-100");           // clamped
  CHECK(r.right.duty == 0 && r.left.duty == 255);
  r.cp.handleAutonomous("N");
  CHECK(r.left.duty == 155 && r.right.duty == -155);
  r.cp.handleAutonomous("CR");             // not implemented: no change
  CHECK(r.left.duty == 155 && r.right.duty == -155);
  r.cp.handleAutonomous("S");
  CHECK(r.left.duty == 0 && r.right.duty == 0);
}

int main() {
  manual_drive_and_replies();
  speed_tuning_is_clamped();
  belt_runs_reversed();
  autonomous_mode();
  std::printf(failures ? "FIRMWARE TESTS FAILED\n" : "All firmware tests passed\n");
  return failures ? 1 : 0;
}
