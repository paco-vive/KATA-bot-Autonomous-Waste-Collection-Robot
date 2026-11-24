"""Automatic black-threshold calibration for changing sunlight on the beach."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class BlackThreshold:
    multiplier: float = 0.65
    min_thr: int = 40
    max_thr: int = 160

    def for_frame(self, hsv: np.ndarray) -> int:
        """Per-frame V threshold from the brightness of the lower half."""
        h = hsv.shape[0]
        brightness = float(np.mean(hsv[h // 2:, :, 2]))
        return int(np.clip(brightness * self.multiplier, self.min_thr, self.max_thr))


DEFAULT_THRESHOLD = BlackThreshold()


def calibrate(hsv_frames: Iterable[np.ndarray]) -> BlackThreshold:
    """Derive the threshold from the V channel of the lower half of a few frames."""
    values: list[np.ndarray] = []
    for hsv in hsv_frames:
        h = hsv.shape[0]
        v = hsv[h // 2:, :, 2].ravel()
        values.append(v[(v > 30) & (v < 250)])
    arr = np.concatenate(values) if values else np.empty(0)
    if arr.size < 100:
        return DEFAULT_THRESHOLD

    background = np.percentile(arr, 50)
    objects = np.percentile(arr, 20)
    return BlackThreshold(
        multiplier=float(np.clip(objects / max(1.0, background), 0.35, 0.80)),
        min_thr=int(np.clip(objects * 0.70, 20, 60)),
        max_thr=int(np.clip(objects * 1.30, 80, 200)),
    )


def sample_hsv_frames(camera, n: int, pause_s: float = 0.05):
    """Yield up to ``n`` HSV frames from a Camera port (skips failed reads)."""
    import cv2

    for _ in range(n):
        ok, frame = camera.read()
        if ok:
            yield cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        time.sleep(pause_s)
