"""Vision process (composition root): camera → pipeline → FIFOs."""
from __future__ import annotations

import argparse
import dataclasses
import logging

from kata_bot.config import CameraConfig, LinkConfig, VisionConfig
from kata_bot.ports import Camera, DetectionPublisher
from kata_bot.vision.calibration import calibrate, sample_hsv_frames
from kata_bot.vision.pipeline import VisionPipeline

log = logging.getLogger("vision")


def run(camera: Camera, publisher: DetectionPublisher, pipeline: VisionPipeline, view=None) -> None:
    while True:
        ok, frame = camera.read()
        if not ok:
            camera.reopen()
            continue
        result = pipeline.process(frame)
        publisher.publish_water(result.water)      # water first: highest priority
        publisher.publish_target(result.target)
        if view is not None and not view.show(frame, result):
            break


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="KATA-bot vision process")
    ap.add_argument("--headless", action="store_true", help="no debug windows (no display needed)")
    ap.add_argument("--camera", type=int, default=0, help="V4L2 camera index")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s: %(message)s",
                        datefmt="%H:%M:%S")

    from kata_bot.adapters.fifo import FifoPublisher
    from kata_bot.adapters.opencv_camera import OpenCvCamera

    vcfg = VisionConfig(show_debug=not args.headless)
    ccfg = dataclasses.replace(CameraConfig(), index=args.camera)

    publisher = FifoPublisher(LinkConfig())
    camera = OpenCvCamera(ccfg)
    for _ in range(ccfg.warmup_frames):
        camera.read()
    log.info("Calibrating black threshold...")
    threshold = calibrate(sample_hsv_frames(camera, ccfg.calibration_frames))
    log.info("Threshold: %s", threshold)

    view = None
    if vcfg.show_debug:
        from kata_bot.vision.debug_view import DebugView
        view = DebugView()
    try:
        run(camera, publisher, VisionPipeline(vcfg, threshold), view)
    finally:
        camera.release()
        if view:
            view.close()


if __name__ == "__main__":
    main()
