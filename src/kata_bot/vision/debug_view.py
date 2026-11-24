"""On-screen debug overlay (only used when show_debug is enabled)."""
from __future__ import annotations

import cv2

from kata_bot.vision.pipeline import VisionResult

FONT = cv2.FONT_HERSHEY_SIMPLEX


class DebugView:
    def __init__(self, window: str = "BeachBot Vision") -> None:
        self.window = window

    def show(self, frame, result: VisionResult) -> bool:
        """Draw and display. Returns False when the user presses Esc."""
        h, w = frame.shape[:2]
        if result.water.detected:
            cv2.rectangle(frame, (0, 0), (w, h), (255, 80, 0), 3)
            cv2.putText(frame, f"WATER:{result.water.side} ({result.water_reading.ratio * 100:.1f}%)",
                        (10, 28), FONT, 0.7, (255, 80, 0), 2)
        if result.can_box:
            x, y, bw, bh = result.can_box
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
            if result.target.kind.value == "CAN":
                cv2.putText(frame, f"e:{result.target.error:.2f}", (x, max(y - 5, 10)),
                            FONT, 0.4, (0, 255, 0), 1)
        if result.ring_box:
            x, y, rw, rh = result.ring_box
            cv2.rectangle(frame, (x, y), (x + rw, y + rh), (0, 0, 255), 2)
            cv2.putText(frame, f"w:{rw}", (x, max(y - 5, 10)), FONT, 0.4, (0, 0, 255), 1)
        cv2.imshow(self.window, frame)
        cv2.imshow("Mask Blue (water)", result.water_reading.mask)
        return (cv2.waitKey(1) & 0xFF) != 27

    def close(self) -> None:
        cv2.destroyAllWindows()
