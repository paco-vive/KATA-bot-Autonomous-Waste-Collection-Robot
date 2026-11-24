"""One detector per object type (cans, red deposit ring, water).

Each detector builds its own mask and has a single reason to change.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from kata_bot.config import CanFilterConfig, VisionConfig
from kata_bot.vision.geometry import Hysteresis

BBox = tuple[int, int, int, int]


def _clean(mask: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, dst=mask)
    cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, dst=mask)
    return mask


def _contours(mask: np.ndarray):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cnts


# ---------------------------------------------------------------- cans
def can_shape_check(contour, bbox: BBox, cfg: CanFilterConfig) -> tuple[bool, str]:
    """Reject blobs that do not look like a standing or lying can."""
    _, _, bw, bh = bbox
    area = cv2.contourArea(contour)
    if area < cfg.min_area:
        return False, "area_small"
    if area > cfg.max_area:
        return False, "area_large"
    if bw < cfg.min_width:
        return False, "width_small"
    aspect = bh / max(1, bw)
    if aspect < cfg.min_aspect or aspect > cfg.max_aspect:
        return False, f"aspect={aspect:.2f}"
    solidity = area / max(1, bw * bh)
    if solidity < cfg.min_solidity:
        return False, f"solidity={solidity:.2f}"
    perimeter = cv2.arcLength(contour, True)
    if perimeter > 0:
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        if circularity < cfg.min_circularity:
            return False, f"circ={circularity:.2f}"
    convexity = area / max(1, cv2.contourArea(cv2.convexHull(contour)))
    if convexity < cfg.min_convexity:
        return False, f"conv={convexity:.2f}"
    return True, "ok"


class CanDetector:
    """Black cans in the lower part of the frame, with nearest-centroid tracking."""

    LOWER = np.array([0, 0, 0])

    def __init__(self, cfg: VisionConfig, kernel: np.ndarray) -> None:
        self.cfg = cfg
        self.kernel = kernel
        self.last_pos: tuple[int, int] | None = None

    def reset_tracking(self) -> None:
        self.last_pos = None

    def detect(self, hsv: np.ndarray, v_threshold: int) -> BBox | None:
        h = hsv.shape[0]
        mask = cv2.inRange(hsv, self.LOWER, np.array([180, 200, v_threshold]))
        _clean(mask, self.kernel)
        mask[: int(h * self.cfg.can_roi_top_ratio), :] = 0

        valid = [c for c in _contours(mask)
                 if can_shape_check(c, cv2.boundingRect(c), self.cfg.can)[0]]
        best = self._pick(valid)
        if best is None:
            return None
        x, y, bw, bh = cv2.boundingRect(best)
        self.last_pos = (x + bw // 2, y + bh // 2)
        return x, y, bw, bh

    def _pick(self, contours):
        if not contours:
            return None
        if self.last_pos is None:
            return max(contours, key=cv2.contourArea)
        best, best_dist = None, float("inf")
        for c in contours:
            m = cv2.moments(c)
            if m["m00"] == 0:
                continue
            cx, cy = int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])
            dist = np.hypot(cx - self.last_pos[0], cy - self.last_pos[1])
            if dist < self.cfg.max_centroid_jump_px and dist < best_dist:
                best, best_dist = c, dist
        if best is None:
            self.last_pos = None   # target jumped too far: re-acquire next frame
        return best


# ----------------------------------------------------------- red ring
class RingDetector:
    """The red deposit ring (red wraps around H=0, so two ranges)."""

    def __init__(self, cfg: VisionConfig, kernel: np.ndarray) -> None:
        self.cfg = cfg
        self.kernel = kernel

    def detect(self, hsv: np.ndarray) -> BBox | None:
        low = cv2.inRange(hsv, np.array([0, 150, 80]), np.array([10, 255, 255]))
        high = cv2.inRange(hsv, np.array([170, 150, 80]), np.array([180, 255, 255]))
        mask = _clean(cv2.bitwise_or(low, high), self.kernel)
        cnts = _contours(mask)
        if not cnts:
            return None
        c = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(c) < self.cfg.min_area_red:
            return None
        return cv2.boundingRect(c)


# -------------------------------------------------------------- water
@dataclass
class WaterReading:
    detected: bool
    side: str
    ratio: float
    mask: np.ndarray


class WaterDetector:
    """Blue-pixel ratio on the full frame, with hysteresis, plus the side."""

    def __init__(self, cfg: VisionConfig, kernel: np.ndarray) -> None:
        self.kernel = kernel
        self.switch = Hysteresis(cfg.water_on_ratio, cfg.water_off_ratio)

    def detect(self, hsv: np.ndarray) -> WaterReading:
        w = hsv.shape[1]
        mask = _clean(cv2.inRange(hsv, np.array([75, 40, 80]), np.array([135, 255, 255])), self.kernel)
        ratio = cv2.countNonZero(mask) / max(1, mask.size)
        detected = self.switch.update(ratio)
        side = "C"
        if detected:
            cnts = _contours(mask)
            if cnts:
                m = cv2.moments(max(cnts, key=cv2.contourArea))
                if m["m00"] > 0:
                    side = "L" if int(m["m10"] / m["m00"]) < w // 2 else "R"
        return WaterReading(detected, side, ratio, mask)
