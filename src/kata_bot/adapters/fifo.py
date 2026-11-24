"""Named-pipe (FIFO) transport between vision.py and maestro.py.

Two FIFOs keep water alerts independent of target messages, so a water
alert is never delayed behind target traffic.
"""
from __future__ import annotations

import errno
import logging
import os
import threading
import time

from kata_bot.config import LinkConfig
from kata_bot.domain.messages import NO_DETECTION, NO_WATER, Detection, WaterStatus

log = logging.getLogger(__name__)


def ensure_fifo(path: str) -> None:
    try:
        os.mkfifo(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class FifoPublisher:
    """Writer side (vision). Opening a FIFO for writing blocks until a reader opens it."""

    def __init__(self, cfg: LinkConfig) -> None:
        self.cfg = cfg
        for path in (cfg.main_pipe, cfg.water_pipe):
            ensure_fifo(path)
        log.info("Waiting for the master to open %s", cfg.main_pipe)
        self._main = open(cfg.main_pipe, "w", buffering=1)
        self._water = None
        self._water_lock = threading.Lock()
        t = threading.Thread(target=self._connect_water, daemon=True)
        t.start()
        t.join(timeout=cfg.water_pipe_connect_timeout_s)

    def _connect_water(self) -> None:
        fd = open(self.cfg.water_pipe, "w", buffering=1)
        with self._water_lock:
            self._water = fd
        log.info("Water pipe connected")

    def publish_water(self, status: WaterStatus) -> None:
        with self._water_lock:
            if self._water is None:
                return
            try:
                self._water.write(status.encode() + "\n")
                self._water.flush()
            except OSError:
                pass   # master gone; the main pipe handles reconnection

    def publish_target(self, detection: Detection) -> None:
        try:
            self._main.write(detection.encode() + "\n")
        except BrokenPipeError:
            log.warning("Master disconnected, reopening main pipe")
            self._main.close()
            self._main = open(self.cfg.main_pipe, "w", buffering=1)
            log.info("Main pipe reconnected")


class FifoSubscriber:
    """Reader side (master). One thread per FIFO keeps the latest value."""

    def __init__(self, cfg: LinkConfig, clock=time.time) -> None:
        self.cfg = cfg
        self.clock = clock
        self._lock = threading.Lock()
        self._last_line: str | None = None
        self._last_time = clock()
        self._water = NO_WATER
        self._alive = True

    def start(self) -> None:
        threading.Thread(target=self._read_main, daemon=True).start()
        threading.Thread(target=self._read_water, daemon=True).start()

    def _wait_for(self, path: str) -> None:
        log.info("Waiting for %s", path)
        while not os.path.exists(path):
            time.sleep(0.5)

    def _read_main(self) -> None:
        self._wait_for(self.cfg.main_pipe)
        with open(self.cfg.main_pipe) as pipe:
            while self._alive:
                line = pipe.readline()
                if not line:
                    log.warning("Main pipe closed")
                    self._alive = False
                    return
                line = line.strip()
                if line:
                    with self._lock:
                        self._last_line = line
                        self._last_time = self.clock()

    def _read_water(self) -> None:
        self._wait_for(self.cfg.water_pipe)
        with open(self.cfg.water_pipe) as pipe:
            while self._alive:
                line = pipe.readline()
                if not line:
                    log.warning("Water pipe closed")
                    return
                line = line.strip()
                if line:
                    with self._lock:
                        self._water = self._water.next(line)

    # --- DetectionSource port
    def latest_target(self, now: float) -> Detection:
        with self._lock:
            if now - self._last_time > self.cfg.detection_max_age_s:
                return NO_DETECTION
            return Detection.decode(self._last_line)

    def latest_water(self) -> WaterStatus:
        with self._lock:
            return self._water

    def has_data(self) -> bool:
        with self._lock:
            return self._last_line is not None

    def touch(self) -> None:
        """Keep data fresh while waiting for the first message (camera calibrating)."""
        with self._lock:
            self._last_time = self.clock()

    @property
    def alive(self) -> bool:
        return self._alive

    def stop(self) -> None:
        self._alive = False
