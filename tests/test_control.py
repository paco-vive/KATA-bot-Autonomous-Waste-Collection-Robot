import pytest

from kata_bot.config import ControlConfig
from kata_bot.control.behaviours import SPattern, StuckDetector
from kata_bot.control.filters import KalmanFilter1D, PDController
from kata_bot.control.fsm import BeachBotFsm, State
from kata_bot.domain.commands import Cmd
from kata_bot.domain.messages import NO_DETECTION, NO_WATER, Detection, TargetKind, WaterStatus

CFG = ControlConfig()


def test_kalman_converges():
    k = KalmanFilter1D()
    for _ in range(50):
        x = k.update(1.0)
    assert x == pytest.approx(1.0, abs=1e-3)


def test_pd_derivative():
    pd = PDController(kp=2.0, kd=1.0)
    assert pd.update(1.0, dt=0.5) == pytest.approx(2.0 + 2.0)
    assert pd.update(1.0, dt=0.5) == pytest.approx(2.0)


def test_s_pattern_alternates_curves():
    p = SPattern(CFG)
    p.reset(0.0)
    cmds = [p.update(t / 10) for t in range(0, 80)]
    assert cmds[0] == Cmd.FORWARD
    assert Cmd.CURVE_RIGHT in cmds and Cmd.CURVE_LEFT in cmds
    assert cmds.index(Cmd.CURVE_RIGHT) < cmds.index(Cmd.CURVE_LEFT)


def test_stuck_detector_only_in_active_states():
    s = StuckDetector(CFG)
    assert not s.is_stuck("x", "DEPOSITING", 100.0)
    s.reset(0.0)
    assert not s.is_stuck("x", "SEARCHING", 0.0)
    assert s.is_stuck("x", "SEARCHING", CFG.stuck_time_s)


def drive(fsm, t, det=NO_DETECTION, water=NO_WATER):
    return fsm.tick(t, det, water)


def test_water_interrupts_approach():
    fsm = BeachBotFsm(CFG, 0.0)
    drive(fsm, 0.1, Detection(TargetKind.CAN, 0.0))
    assert fsm.state is State.APPROACHING
    r = drive(fsm, 0.2, water=WaterStatus(True, "L"))
    assert fsm.state is State.AVOIDING_WATER
    assert r.commands == [Cmd.STOP]
    assert r.sleep_s == CFG.water_tick_period_s


def test_reached_can_and_deposit_cycle():
    cfg = ControlConfig(cans_per_deposit=1)
    fsm = BeachBotFsm(cfg, 0.0)
    t = 0.0
    centered = Detection(TargetKind.CAN, 0.0)
    for _ in range(6):
        t += 0.08
        drive(fsm, t, centered)
    for _ in range(cfg.max_lost_frames):
        t += 0.08
        drive(fsm, t)
    assert fsm.state is State.REACHED_CAN and fsm.cans_total == 1
    t += cfg.reached_can_pause_s
    drive(fsm, t)
    assert fsm.state is State.SEARCHING_RED
    t += 0.08
    drive(fsm, t, Detection(TargetKind.RED, 0.0, 50))
    assert fsm.state is State.APPROACHING_RED
    t += 0.08
    drive(fsm, t, Detection(TargetKind.RED, 0.0, 150))
    assert fsm.state is State.TURNING_TO_DEPOSIT
    t += cfg.turn_to_deposit_s + cfg.turn_backup_s
    drive(fsm, t)
    assert fsm.state is State.DEPOSITING
    r = drive(fsm, t + 0.01)
    assert r.commands[0] == Cmd.DOOR_OPEN
    r = drive(fsm, t + cfg.deposit_open_s + 0.01)
    assert Cmd.DOOR_CLOSE in r.commands and fsm.state is State.SEARCHING


def test_missed_can_returns_to_search_and_stops_belt():
    fsm = BeachBotFsm(CFG, 0.0)
    drive(fsm, 0.1, Detection(TargetKind.CAN, 0.9))   # never centred
    t = 0.1
    out = []
    for _ in range(CFG.max_lost_frames):
        t += 0.08
        out += drive(fsm, t).commands
    assert fsm.state is State.SEARCHING
    assert out[-1] == Cmd.BELT_OFF
