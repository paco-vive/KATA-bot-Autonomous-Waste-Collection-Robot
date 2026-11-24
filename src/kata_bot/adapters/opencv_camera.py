"""Camera port implemented with OpenCV + V4L2 (USB camera on the Raspberry Pi)."""
from __future__ import annotations

import logging
import time

import cv2

from kata_bot.config import CameraConfig

log = logging.getLogger(__name__)


class OpenCvCamera:
    def __init__(self, cfg: CameraConfig) -> None:
        self.cfg = cfg
        self.cap = self._open()

    def _open(self) -> cv2.VideoCapture:
        while True:
            cap = cv2.VideoCapture(self.cfg.index, cv2.CAP_V4L2)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.height)
            cap.set(cv2.CAP_PROP_FPS, self.cfg.fps)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            if cap.isOpened():
                return cap
            cap.release()
            log.warning("Camera %d not available, retrying", self.cfg.index)
            time.sleep(self.cfg.reopen_delay_s)

    def read(self):
        return self.cap.read()

    def reopen(self) -> None:
        self.cap.release()
        self.cap = self._open()

    def release(self) -> None:
        self.cap.release()
