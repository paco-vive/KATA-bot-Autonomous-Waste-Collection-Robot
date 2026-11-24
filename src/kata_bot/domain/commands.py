"""Master → ESP32 serial commands (one text line each).

A line is either a steering correction (a number, e.g. ``-12.5``) or one of
the codes below. See docs/architecture/03-process-view.md §4 for which codes
the current firmware actually executes.
"""
from __future__ import annotations


class Cmd:
    STOP = "S"
    FORWARD = "F"
    BACK = "B"
    CURVE_RIGHT = "CR"
    CURVE_LEFT = "CL"
    BACK_LEFT = "BL"
    BACK_CURVE_K = "BK"     # backward curve used when water is on the left
    BACK_CURVE_A = "BA"     # backward curve used when water is on the right
    DOOR_OPEN = "DO"
    DOOR_CLOSE = "DC"
    BELT_ON = "J"
    BELT_OFF = "M"


def steering(correction: float) -> str:
    """Encode a PD correction exactly as the TMR 2026 code did."""
    return str(round(correction, 2))
