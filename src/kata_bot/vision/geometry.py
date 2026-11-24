"""Frame-geometry helpers that do not depend on OpenCV."""
from __future__ import annotations


def lateral_error(cx: int, width: int) -> float:
    """Normalised lateral error in [-1, 1] with a dead zone in the central quarter.

    The dead zone spans 3/8 to 5/8 of the width: inside it the error is 0.
    """
    zone_l = 3 * (width // 8)
    zone_r = 5 * (width // 8)
    if cx < zone_l:
        raw = (cx - zone_l) / zone_l
    elif cx > zone_r:
        raw = (cx - zone_r) / (width - zone_r)
    else:
        raw = 0.0
    return float(min(1.0, max(-1.0, raw)))


class Hysteresis:
    """Boolean switch with separate on/off thresholds (avoids flicker)."""

    def __init__(self, on: float, off: float) -> None:
        if off >= on:
            raise ValueError("off threshold must be below on threshold")
        self.on = on
        self.off = off
        self.active = False

    def update(self, value: float) -> bool:
        if self.active and value < self.off:
            self.active = False
        elif not self.active and value > self.on:
            self.active = True
        return self.active
