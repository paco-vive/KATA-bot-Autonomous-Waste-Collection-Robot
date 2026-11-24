"""Turns a BGR frame into the two protocol messages (target + water)."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from kata_bot.config import VisionConfig
from kata_bot.domain.messages import NO_DETECTION, Detection, TargetKind, WaterStatus
from kata_bot.vision.calibration import DEFAULT_THRESHOLD, BlackThreshold
from kata_bot.vision.detectors import BBox, CanDetector, RingDetector, WaterDetector, WaterReading
from kata_bot.vision.geometry import lateral_error


@dataclass
class VisionResult:
    target: Detection
    water: WaterStatus
    water_reading: WaterReading
    can_box: BBox | None = None
    ring_box: BBox | None = None


class VisionPipeline:
    """Priority: water > can > red ring > nothing."""

    def __init__(self, cfg: VisionConfig, threshold: BlackThreshold = DEFAULT_THRESHOLD) -> None:
        kernel = np.ones((cfg.kernel_size, cfg.kernel_size), np.uint8)
        self.threshold = threshold
        self.cans = CanDetector(cfg, kernel)
        self.ring = RingDetector(cfg, kernel)
        self.water = WaterDetector(cfg, kernel)

    def process(self, frame_bgr: np.ndarray) -> VisionResult:
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        w = hsv.shape[1]
        water = self.water.detect(hsv)
        status = WaterStatus(water.detected, water.side)

        if water.detected:
            self.cans.reset_tracking()
            return VisionResult(NO_DETECTION, status, water)

        can_box = self.cans.detect(hsv, self.threshold.for_frame(hsv))
        ring_box = self.ring.detect(hsv)

        if can_box is not None:
            x, _, bw, _ = can_box
            target = Detection(TargetKind.CAN, lateral_error(x + bw // 2, w))
        elif ring_box is not None:
            x, _, rw, _ = ring_box
            target = Detection(TargetKind.RED, lateral_error(x + rw // 2, w), rw)
        else:
            target = NO_DETECTION
        return VisionResult(target, status, water, can_box, ring_box)
