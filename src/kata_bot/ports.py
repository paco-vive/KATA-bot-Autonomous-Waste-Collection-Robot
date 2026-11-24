"""Ports: the interfaces the application depends on (Dependency Inversion).

Concrete implementations live in ``kata_bot.adapters``; tests use fakes.
"""
from __future__ import annotations

from typing import Protocol, Tuple

import numpy as np

from kata_bot.domain.messages import Detection, WaterStatus


class Camera(Protocol):
    def read(self) -> Tuple[bool, np.ndarray]: ...
    def reopen(self) -> None: ...
    def release(self) -> None: ...


class DetectionPublisher(Protocol):
    """Vision side: publishes what it sees."""
    def publish_water(self, status: WaterStatus) -> None: ...
    def publish_target(self, detection: Detection) -> None: ...


class DetectionSource(Protocol):
    """Master side: latest observations from vision."""
    def latest_target(self, now: float) -> Detection: ...
    def latest_water(self) -> WaterStatus: ...
    def has_data(self) -> bool: ...
    @property
    def alive(self) -> bool: ...


class MotorLink(Protocol):
    """Master side: sends one command line to the motor controller."""
    def send(self, command: str) -> None: ...
    def close(self) -> None: ...


class Clock(Protocol):
    def __call__(self) -> float: ...
