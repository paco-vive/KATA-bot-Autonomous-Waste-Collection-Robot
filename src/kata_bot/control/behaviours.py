"""Reusable open-loop behaviours. Each one returns the command for this tick."""
from __future__ import annotations

import logging

from kata_bot.config import ControlConfig
from kata_bot.domain.commands import Cmd

log = logging.getLogger(__name__)


class SPattern:
    """Search by driving straight, then curving, alternating the curve side."""

    def __init__(self, cfg: ControlConfig) -> None:
        self.cfg = cfg
        self.reset(0.0)

    def reset(self, now: float) -> None:
        self.phase = "STRAIGHT"
        self.turn_right = True
        self.phase_start = now

    def update(self, now: float) -> str:
        elapsed = now - self.phase_start
        if self.phase == "STRAIGHT":
            if elapsed >= self.cfg.s_straight_s:
                self.phase = "CURVE"
                self.phase_start = now
            return Cmd.FORWARD
        cmd = Cmd.CURVE_RIGHT if self.turn_right else Cmd.CURVE_LEFT
        if elapsed >= self.cfg.s_curve_s:
            self.turn_right = not self.turn_right
            self.phase = "STRAIGHT"
            self.phase_start = now
        return cmd


class StuckDetector:
    """Detects that the same command has been sent for too long and escapes.

    Escape: wiggle back/forward, then curve right.
    """

    ACTIVE_STATES = ("SEARCHING", "APPROACHING", "SEARCHING_RED", "APPROACHING_RED")

    def __init__(self, cfg: ControlConfig) -> None:
        self.cfg = cfg
        self.reset(0.0)

    def reset(self, now: float) -> None:
        self.last_cmd: object = None
        self.same_cmd_since = now
        self.unsticking = False
        self.unstick_start = now
        self.phase = ""

    def is_stuck(self, current_cmd: object, state: str, now: float) -> bool:
        if state not in self.ACTIVE_STATES:
            self.reset(now)
            return False
        if current_cmd != self.last_cmd:
            self.last_cmd = current_cmd
            self.same_cmd_since = now
        if now - self.same_cmd_since >= self.cfg.stuck_time_s:
            if not self.unsticking:
                self.unsticking = True
                self.unstick_start = now
                self.phase = "WIGGLE"
                log.warning("Stuck detected, starting escape")
            return True
        return False

    def step(self, now: float) -> tuple[str, bool]:
        """Return (command, still_escaping)."""
        t = now - self.unstick_start
        if self.phase == "WIGGLE":
            cycle = int(t / self.cfg.stuck_wiggle_period_s) % 2
            if t >= self.cfg.stuck_wiggle_s:
                self.phase = "ESCAPE"
                self.unstick_start = now
            return (Cmd.BACK if cycle == 0 else Cmd.FORWARD), True
        if t >= self.cfg.stuck_escape_s:
            self.reset(now)
            return Cmd.CURVE_RIGHT, False
        return Cmd.CURVE_RIGHT, True
