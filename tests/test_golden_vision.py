"""Golden test: refactored vision helpers vs the TMR 2026 vision.py functions."""
import ast
import os

import cv2
import numpy as np
import pytest

from kata_bot.config import CanFilterConfig, VisionConfig
from kata_bot.domain.messages import TargetKind
from kata_bot.vision.calibration import calibrate
from kata_bot.vision.detectors import can_shape_check
from kata_bot.vision.geometry import lateral_error
from kata_bot.vision.pipeline import VisionPipeline

REF = os.path.join(os.path.dirname(__file__), "reference", "vision_tmr2026.py")


@pytest.fixture(scope="module")
def ref():
    """Load only imports, constants and pure functions: the script opens pipes at import time."""
    tree = ast.parse(open(REF).read())
    keep = {"calibrar_umbral", "es_lata_valida", "compute_error"}
    tree.body = [n for n in tree.body
                 if isinstance(n, (ast.Import, ast.ImportFrom))
                 or (isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper()
                                                       for t in n.targets))
                 or (isinstance(n, ast.FunctionDef) and n.name in keep)]
    ns = {}
    exec(compile(tree, REF, "exec"), ns)
    return ns


def test_lateral_error_matches(ref):
    for cx in range(0, 641):
        assert lateral_error(cx, 640) == ref["compute_error"](cx, 640)


def test_can_filter_matches(ref):
    rng = np.random.default_rng(0)
    for _ in range(300):
        img = np.zeros((480, 640), np.uint8)
        pts = rng.integers([0, 0], [640, 480], size=(rng.integers(3, 9), 2)).astype(np.int32)
        cv2.fillPoly(img, [cv2.convexHull(pts) if rng.random() < 0.5 else pts], 255)
        cnts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            bbox = cv2.boundingRect(c)
            # decisions must match; reason labels were translated to English
            assert can_shape_check(c, bbox, CanFilterConfig())[0] == ref["es_lata_valida"](c, bbox)[0]


class FrameCamera:
    def __init__(self, frames):
        self.frames = list(frames)

    def read(self):
        return (True, self.frames.pop(0)) if self.frames else (False, None)


def test_calibration_matches(ref, monkeypatch):
    rng = np.random.default_rng(1)
    frames = [rng.integers(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]
    monkeypatch.setattr(ref["time"], "sleep", lambda s: None)
    expected = ref["calibrar_umbral"](FrameCamera(frames), n_frames=5)
    got = calibrate(cv2.cvtColor(f, cv2.COLOR_BGR2HSV) for f in frames)
    assert (got.multiplier, got.min_thr, got.max_thr) == pytest.approx(expected)


# ------------------------------------------------- synthetic scenes
SAND = (150, 190, 215)   # BGR, light sand


def scene():
    return np.full((480, 640, 3), SAND, np.uint8)


def test_detects_black_can():
    img = scene()
    cv2.rectangle(img, (100, 300), (150, 380), (10, 10, 10), -1)
    r = VisionPipeline(VisionConfig()).process(img)
    assert r.target.kind is TargetKind.CAN
    assert r.target.error < 0


def test_detects_red_ring_with_width():
    img = scene()
    cv2.rectangle(img, (400, 200), (520, 260), (0, 0, 220), -1)
    r = VisionPipeline(VisionConfig()).process(img)
    assert r.target.kind is TargetKind.RED
    assert r.target.width == 121 and r.target.error > 0


def test_water_has_priority_and_side():
    img = scene()
    cv2.rectangle(img, (500, 250), (520, 330), (10, 10, 10), -1)
    cv2.rectangle(img, (0, 0), (250, 479), (200, 120, 0), -1)
    r = VisionPipeline(VisionConfig()).process(img)
    assert r.water.detected and r.water.side == "L"
    assert r.target.kind is TargetKind.NONE
