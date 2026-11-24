"""Golden test: the refactored state machine must send exactly the same
commands, at exactly the same simulated times, as the TMR 2026 maestro.py.
"""
import importlib.util
import os
import time as real_time

import pytest

from kata_bot.apps.master_app import run
from kata_bot.config import ControlConfig
from kata_bot.domain.messages import NO_WATER, Detection

REF = os.path.join(os.path.dirname(__file__), "reference", "maestro_tmr2026.py")


def load_reference():
    spec = importlib.util.spec_from_file_location("maestro_ref", REF)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeTime:
    def __init__(self, on_advance):
        self.t = 1000.0
        self.on_advance = on_advance

    def time(self):
        return self.t

    def sleep(self, d):
        self.t += d
        self.on_advance(self.t)

    def strftime(self, fmt):
        return real_time.strftime(fmt)


def run_reference(scenario, duration, cans_per_deposit):
    mod = load_reference()
    sent = []
    clock = FakeTime(None)
    start = clock.t

    def feed(t):
        target, water = scenario(t - start)
        mod.ultimo_dato = target
        mod.tiempo_ultimo_dato = t
        if water is not None:   # same parsing as the reference reader thread
            if water.startswith("W"):
                mod.water_detected = True
                parts = water.split(":")
                mod.water_side = parts[1] if len(parts) > 1 else "C"
            else:
                mod.water_detected = False
        if t - start > duration:
            mod.running = False

    clock.on_advance = feed
    mod.time = clock
    mod.log = lambda msg: None
    mod.enviar = lambda cmd: sent.append((round(clock.t - start, 4), str(cmd)))
    mod.CANS_PER_DEPOSIT = cans_per_deposit
    mod.running = True
    feed(clock.t)
    mod.maquina_de_estados()
    return sent


class FakeSource:
    def __init__(self, scenario, start):
        self.scenario = scenario
        self.start = start
        self.water = NO_WATER

    def latest_target(self, now):
        target, water = self.scenario(now - self.start)
        if water is not None:
            self.water = self.water.next(water)
        return Detection.decode(target)

    def latest_water(self):
        return self.water

    def has_data(self):
        return True

    @property
    def alive(self):
        return True


class Recorder:
    def __init__(self, clock):
        self.clock = clock
        self.sent = []

    def send(self, cmd):
        self.sent.append((round(self.clock.t - 1000.0, 4), cmd))

    def close(self):
        pass


def run_refactor(scenario, duration, cans_per_deposit):
    clock = FakeTime(lambda t: None)
    source = FakeSource(scenario, clock.t)
    rec = Recorder(clock)
    run(source, rec, ControlConfig(cans_per_deposit=cans_per_deposit),
        clock=clock.time, sleep=clock.sleep,
        should_run=lambda: clock.t - 1000.0 <= duration)
    return rec.sent


# ---------------------------------------------------------------- scenarios
def can_pickup(t):
    if 1.0 <= t < 3.0:
        return f"CAN:{0.4 - t * 0.15:.3f}", "C"
    return "N", "C"


def full_cycle(t):
    if 0.5 <= t < 2.0:
        return "CAN:0.000", "C"
    if 5.0 <= t < 7.0:
        return f"RED:{0.3 - (t - 5) * 0.2:.3f}:{int(40 + (t - 5) * 40)}", "C"
    return "N", "C"


def water_left_then_clear(t):
    if 2.0 <= t < 4.0:
        return "N", "W:L"
    return "N", "C"


def water_right_persistent(t):
    if t >= 1.0:
        return "N", "W:R"
    return "N", "C"


def nothing(t):
    return "N", "C"


def noisy_can_with_dropouts(t):
    if 0.5 <= t < 6.0 and int(t * 10) % 7 != 0:
        return f"CAN:{((t * 7) % 2) - 1:.3f}", None
    return "N", None


@pytest.mark.parametrize("scenario,duration,cans", [
    (can_pickup, 8.0, 40),
    (full_cycle, 20.0, 1),
    (water_left_then_clear, 12.0, 40),
    (water_right_persistent, 15.0, 40),
    (nothing, 50.0, 40),          # 40 s of identical commands -> stuck escape
    (noisy_can_with_dropouts, 10.0, 40),
])
def test_same_commands_as_tmr2026(scenario, duration, cans):
    expected = run_reference(scenario, duration, cans)
    actual = run_refactor(scenario, duration, cans)
    assert len(expected) > 20
    assert actual == expected
