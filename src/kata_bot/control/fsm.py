"""BeachBot mission state machine.

Pure logic: it receives the time, the latest detection and the water status,
and returns the commands to send. It never touches pipes, serial ports or the
clock, so every transition can be unit-tested (tests/test_fsm.py).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from kata_bot.config import ControlConfig
from kata_bot.control.behaviours import SPattern, StuckDetector
from kata_bot.control.filters import TargetTracker
from kata_bot.domain.commands import Cmd, steering
from kata_bot.domain.messages import Detection, TargetKind, WaterStatus

log = logging.getLogger(__name__)


class State(str, Enum):
    SEARCHING = "SEARCHING"
    APPROACHING = "APPROACHING"
    REACHED_CAN = "REACHED_CAN"
    SEARCHING_RED = "SEARCHING_RED"
    APPROACHING_RED = "APPROACHING_RED"
    TURNING_TO_DEPOSIT = "TURNING_TO_DEPOSIT"
    DEPOSITING = "DEPOSITING"
    AVOIDING_WATER = "AVOIDING_WATER"
    WATER_CLEAR_BACK = "WATER_CLEAR_BACK"


#: States that water detection may interrupt (water has top priority).
WATER_INTERRUPTIBLE = frozenset({
    State.SEARCHING,
    State.APPROACHING,
    State.SEARCHING_RED,
    State.APPROACHING_RED,
    State.TURNING_TO_DEPOSIT,
    State.WATER_CLEAR_BACK,
})


@dataclass
class TickResult:
    commands: list[str] = field(default_factory=list)
    sleep_s: float = 0.08


class BeachBotFsm:
    def __init__(self, cfg: ControlConfig, now: float) -> None:
        self.cfg = cfg
        self.state = State.SEARCHING
        self.state_start = now
        self.last_tick = now
        self.cans_collected = 0
        self.cans_total = 0
        self._centered = 0
        self._lost = 0
        self._last_cmd: object = 0.0
        self._door_open = False
        self._saved_water_side = "C"
        self._can = TargetTracker(cfg.kp, cfg.kd, cfg.kalman_q, cfg.kalman_r)
        self._red = TargetTracker(cfg.kp, cfg.kd, cfg.kalman_q, cfg.kalman_r)
        self._pattern = SPattern(cfg)
        self._stuck = StuckDetector(cfg)
        self._pattern.reset(now)
        self._stuck.reset(now)

    # ------------------------------------------------------------------ API
    @staticmethod
    def startup_commands() -> list[str]:
        return [Cmd.STOP, Cmd.BELT_OFF]

    @staticmethod
    def shutdown_commands() -> list[str]:
        return [Cmd.STOP, Cmd.BELT_OFF]

    def tick(self, now: float, det: Detection, water: WaterStatus) -> TickResult:
        dt = now - self.last_tick
        self.last_tick = now
        out: list[str] = []

        # Priority 1: water
        if water.detected and self.state in WATER_INTERRUPTIBLE:
            out.append(Cmd.STOP)
            log.info("[WATER] on %s during %s, avoiding", water.side, self.state.value)
            self._change(State.AVOIDING_WATER, now, f"water on {water.side}")
            return TickResult(out, self.cfg.water_tick_period_s)

        # Priority 2: stuck
        if self._stuck.is_stuck(self._last_cmd, self.state.value, now):
            cmd, escaping = self._stuck.step(now)
            out.append(cmd)
            if not escaping:
                log.info("Escape finished, resuming")
                self._stuck.reset(now)
                self._pattern.reset(now)
            return TickResult(out, self.cfg.tick_period_s)

        handler = getattr(self, f"_on_{self.state.value.lower()}")
        handler(now, dt, det, water, out)
        return TickResult(out, self.cfg.tick_period_s)

    # ------------------------------------------------------------- helpers
    def _elapsed(self, now: float) -> float:
        return now - self.state_start

    def _change(self, new: State, now: float, reason: str = "") -> None:
        log.info("%s -> %s  (%s)", self.state.value, new.value, reason)
        self.state = new
        self.state_start = now
        self._centered = 0
        self._lost = 0
        self._last_cmd = 0.0
        self._door_open = False
        self._can.reset()
        self._red.reset()
        self._pattern.reset(now)
        self._stuck.reset(now)

    def _track(self, tracker: TargetTracker, det: Detection, dt: float, out: list[str]) -> float:
        self._lost = 0
        filtered, correction = tracker.update(det.error, dt)
        self._last_cmd = correction
        out.append(steering(correction))
        return filtered

    def _coast(self, out: list[str]) -> bool:
        """Target lost: keep the last correction for a few frames. True while coasting."""
        self._lost += 1
        if self._lost < self.cfg.max_lost_frames:
            out.append(steering(float(self._last_cmd)))
            return True
        return False

    # -------------------------------------------------------------- states
    def _on_searching(self, now, dt, det, water, out):
        out.append(self._pattern.update(now))
        self._last_cmd = "S_PATTERN"
        if det.kind is TargetKind.CAN:
            out.append(Cmd.BELT_ON)
            self._change(State.APPROACHING, now, "can detected")

    def _on_approaching(self, now, dt, det, water, out):
        if det.kind is TargetKind.CAN:
            filtered = self._track(self._can, det, dt, out)
            if abs(filtered) < self.cfg.error_threshold:
                self._centered += 1
            else:
                self._centered = max(0, self._centered - 1)
            return
        if self._coast(out):
            return
        if self._centered >= self.cfg.min_centered_frames:
            self.cans_collected += 1
            self.cans_total += 1
            out.append(Cmd.STOP)
            self._change(State.REACHED_CAN, now,
                         f"can {self.cans_collected}/{self.cfg.cans_per_deposit}")
        else:
            out.append(Cmd.BELT_OFF)
            self._change(State.SEARCHING, now, "can missed")

    def _on_reached_can(self, now, dt, det, water, out):
        out.append(Cmd.STOP)
        if self._elapsed(now) >= self.cfg.reached_can_pause_s:
            out.append(Cmd.BELT_OFF)
            if self.cans_collected >= self.cfg.cans_per_deposit:
                self.cans_collected = 0
                self._change(State.SEARCHING_RED, now, "load full, looking for deposit")
            else:
                self._change(State.SEARCHING, now, "next can")

    def _on_searching_red(self, now, dt, det, water, out):
        out.append(self._pattern.update(now))
        self._last_cmd = "S_PATTERN"
        if det.kind is TargetKind.RED:
            self._change(State.APPROACHING_RED, now, "red ring detected")

    def _on_approaching_red(self, now, dt, det, water, out):
        if det.kind is TargetKind.RED:
            self._track(self._red, det, dt, out)
            if det.width >= self.cfg.red_close_width_px:
                out.append(Cmd.STOP)
                self._change(State.TURNING_TO_DEPOSIT, now, f"ring at {det.width}px")
            return
        if not self._coast(out):
            out.append(Cmd.BELT_OFF)
            self._change(State.SEARCHING_RED, now, "ring lost")

    def _on_turning_to_deposit(self, now, dt, det, water, out):
        t = self._elapsed(now)
        if t < self.cfg.turn_to_deposit_s:
            out.append(Cmd.CURVE_RIGHT)
        elif t < self.cfg.turn_to_deposit_s + self.cfg.turn_backup_s:
            out.append(Cmd.BACK_LEFT)
        else:
            out.append(Cmd.STOP)
            self._change(State.DEPOSITING, now, "in position")

    def _on_depositing(self, now, dt, det, water, out):
        if not self._door_open:
            out.append(Cmd.DOOR_OPEN)
            self._door_open = True
        out.append(Cmd.BACK_LEFT)
        if self._elapsed(now) >= self.cfg.deposit_open_s:
            out += [Cmd.DOOR_CLOSE, Cmd.STOP]
            log.info("Deposit done, total=%d", self.cans_total)
            self._change(State.SEARCHING, now, "deposit done")

    def _on_avoiding_water(self, now, dt, det, water, out):
        t = self._elapsed(now)
        c = self.cfg
        if t >= c.water_avoid_timeout_s:
            out.append(Cmd.STOP)
            self._change(State.SEARCHING, now, "water timeout")
        elif not water.detected and t >= c.water_min_back_s:
            out.append(Cmd.STOP)
            self._saved_water_side = water.side
            self._change(State.WATER_CLEAR_BACK, now, f"side={water.side}")
        elif t < c.water_stop_s:
            out.append(Cmd.STOP)
        elif t > c.water_stop_s + c.water_stuck_s:
            cycle = int((t - c.water_stop_s) / c.water_rock_period_s) % 2
            out.append(Cmd.BACK_CURVE_K if cycle == 0 else Cmd.BACK_CURVE_A)
        else:
            out.append(Cmd.BACK_CURVE_A if water.side == "R" else Cmd.BACK_CURVE_K)

    def _on_water_clear_back(self, now, dt, det, water, out):
        t = self._elapsed(now)
        right = self._saved_water_side == "R"
        if t < self.cfg.water_extra_back_s:
            out.append(Cmd.BACK_CURVE_A if right else Cmd.BACK_CURVE_K)
        elif t < self.cfg.water_extra_back_s + self.cfg.water_turn_s:
            out.append(Cmd.CURVE_LEFT if right else Cmd.CURVE_RIGHT)
        else:
            out.append(Cmd.STOP)
            self._change(State.SEARCHING, now, "water avoided")
