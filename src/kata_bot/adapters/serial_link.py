"""MotorLink over UART to the ESP32, with automatic reconnection."""
from __future__ import annotations

import logging
import threading
import time

import serial

from kata_bot.config import LinkConfig

log = logging.getLogger(__name__)


class SerialMotorLink:
    def __init__(self, cfg: LinkConfig) -> None:
        self.cfg = cfg
        self._lock = threading.Lock()
        self._running = True
        self._ser = self._open()
        threading.Thread(target=self._watchdog, daemon=True).start()

    def _open(self) -> serial.Serial:
        while True:
            try:
                s = serial.Serial(self.cfg.serial_port, self.cfg.baud_rate, timeout=1)
                log.info("ESP32 connected on %s", self.cfg.serial_port)
                return s
            except serial.SerialException:
                log.warning("ESP32 not available, retrying in 2 s")
                time.sleep(2)

    def _watchdog(self) -> None:
        while self._running:
            time.sleep(1.0)
            with self._lock:
                if self._ser is None or not self._ser.is_open:
                    log.warning("Serial link down, reconnecting")
                    self._ser = self._open()

    def send(self, command: str) -> None:
        with self._lock:
            if self._ser is None or not self._ser.is_open:
                return
            try:
                self._ser.write((command + "\n").encode())
            except serial.SerialException:
                log.error("Failed to send %r, watchdog will reconnect", command)
                try:
                    self._ser.close()
                except Exception:
                    pass

    def close(self) -> None:
        self._running = False
        with self._lock:
            if self._ser and self._ser.is_open:
                self._ser.close()
