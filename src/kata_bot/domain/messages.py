"""Vision → master protocol (text lines over two named pipes).

Main pipe:  ``CAN:<err>``  |  ``RED:<err>:<width_px>``  |  ``N``
Water pipe: ``W:<L|R|C>``  |  ``C``

``err`` is the lateral error in [-1, 1] (negative = target on the left).
Encoding and decoding live together so both sides can never drift apart.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetKind(str, Enum):
    NONE = "N"
    CAN = "CAN"
    RED = "RED"


@dataclass(frozen=True)
class Detection:
    kind: TargetKind = TargetKind.NONE
    error: float = 0.0
    width: int = 0

    def encode(self) -> str:
        if self.kind is TargetKind.CAN:
            return f"CAN:{self.error:.3f}"
        if self.kind is TargetKind.RED:
            return f"RED:{self.error:.3f}:{self.width}"
        return "N"

    @staticmethod
    def decode(line: str | None) -> "Detection":
        if not line or line == "N":
            return NO_DETECTION
        parts = line.split(":")
        if len(parts) >= 2 and parts[0] in ("CAN", "RED"):
            try:
                width = int(parts[2]) if len(parts) >= 3 else 0
                return Detection(TargetKind(parts[0]), float(parts[1]), width)
            except ValueError:
                pass
        return NO_DETECTION


NO_DETECTION = Detection()


@dataclass(frozen=True)
class WaterStatus:
    detected: bool = False
    side: str = "C"   # L, R or C (centre / unknown)

    def encode(self) -> str:
        return f"W:{self.side}" if self.detected else "C"

    def next(self, line: str) -> "WaterStatus":
        """Apply a water-pipe line to this status.

        On ``C`` (clear) the last known side is kept on purpose: after the
        water disappears the robot still needs to know which way to back off.
        """
        if line.startswith("W"):
            parts = line.split(":")
            return WaterStatus(True, parts[1] if len(parts) > 1 else "C")
        return WaterStatus(False, self.side)


NO_WATER = WaterStatus()
