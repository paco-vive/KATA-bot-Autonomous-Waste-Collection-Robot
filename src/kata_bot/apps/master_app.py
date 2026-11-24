"""Master process (composition root): FIFOs → state machine → ESP32."""
from __future__ import annotations

import argparse
import logging
import signal
import sys
import time

from kata_bot.config import ControlConfig, LinkConfig
from kata_bot.control.fsm import BeachBotFsm
from kata_bot.ports import DetectionSource, MotorLink

log = logging.getLogger("master")


def run(source: DetectionSource, motors: MotorLink, cfg: ControlConfig,
        clock=time.time, sleep=time.sleep, should_run=lambda: True) -> BeachBotFsm:
    fsm = BeachBotFsm(cfg, clock())
    for cmd in fsm.startup_commands():
        motors.send(cmd)
    log.info("SEARCHING - %d cans per deposit", cfg.cans_per_deposit)
    while should_run() and source.alive:
        now = clock()
        result = fsm.tick(now, source.latest_target(now), source.latest_water())
        for cmd in result.commands:
            motors.send(cmd)
        sleep(result.sleep_s)
    log.info("State machine stopped")
    return fsm


def stop_robot(motors: MotorLink, fsm_cls=BeachBotFsm) -> None:
    for _ in range(3):
        for cmd in fsm_cls.shutdown_commands():
            motors.send(cmd)
        time.sleep(0.05)
    motors.close()


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="KATA-bot master control")
    ap.add_argument("--port", default=LinkConfig.serial_port, help="ESP32 serial port")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s: %(message)s",
                        datefmt="%H:%M:%S")

    from kata_bot.adapters.fifo import FifoSubscriber
    from kata_bot.adapters.serial_link import SerialMotorLink

    link_cfg = LinkConfig(serial_port=args.port)
    motors = SerialMotorLink(link_cfg)
    source = FifoSubscriber(link_cfg)
    running = {"on": True}

    def shutdown(signum=None, frame=None):
        log.info("Clean shutdown, stopping ESP32")
        running["on"] = False
        source.stop()
        stop_robot(motors)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    source.start()
    log.info("Waiting for the camera to finish calibrating...")
    while not source.has_data() and running["on"]:
        time.sleep(0.1)
        source.touch()

    run(source, motors, ControlConfig(), should_run=lambda: running["on"])
    shutdown()


if __name__ == "__main__":
    main()
