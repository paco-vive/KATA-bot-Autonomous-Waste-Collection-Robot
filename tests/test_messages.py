from kata_bot.domain.commands import steering
from kata_bot.domain.messages import NO_DETECTION, Detection, TargetKind, WaterStatus


def test_detection_roundtrip():
    for d in (Detection(TargetKind.CAN, -0.25), Detection(TargetKind.RED, 0.5, 120), NO_DETECTION):
        assert Detection.decode(d.encode()) == d


def test_detection_wire_format():
    assert Detection(TargetKind.CAN, 0.1234).encode() == "CAN:0.123"
    assert Detection(TargetKind.RED, -1.0, 99).encode() == "RED:-1.000:99"


def test_garbage_decodes_to_nothing():
    for line in (None, "", "N", "CAN", "CAN:abc", "XYZ:1", "RED:1:wide"):
        assert Detection.decode(line) == NO_DETECTION


def test_water_keeps_last_side_when_clear():
    s = WaterStatus().next("W:L")
    assert s == WaterStatus(True, "L")
    s = s.next("C")
    assert s == WaterStatus(False, "L")
    assert WaterStatus(True, "R").encode() == "W:R"
    assert WaterStatus(False, "R").encode() == "C"


def test_steering_format():
    assert steering(3.14159) == "3.14"
    assert steering(-0.0) == "-0.0"
