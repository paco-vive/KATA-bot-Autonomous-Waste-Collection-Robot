"""All tunable parameters in one place.

The defaults are the exact values used at TMR 2026 (scripts v6 / v8).
Change them here, or build a modified copy with ``dataclasses.replace``.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LinkConfig:
    main_pipe: str = "/tmp/error_tracking"   # CAN / RED / N
    water_pipe: str = "/tmp/water_alert"     # W:L / W:R / W:C / C
    serial_port: str = "/dev/serial0"
    baud_rate: int = 115200
    detection_max_age_s: float = 0.5         # older data counts as "N"
    water_pipe_connect_timeout_s: float = 15.0


@dataclass(frozen=True)
class CameraConfig:
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 20
    warmup_frames: int = 20
    calibration_frames: int = 10
    reopen_delay_s: float = 2.0


@dataclass(frozen=True)
class CanFilterConfig:
    min_area: int = 800
    max_area: int = 60000
    min_width: int = 25
    min_aspect: float = 0.50
    max_aspect: float = 3.5
    min_solidity: float = 0.45
    min_circularity: float = 0.35
    min_convexity: float = 0.80


@dataclass(frozen=True)
class VisionConfig:
    kernel_size: int = 6
    can_roi_top_ratio: float = 0.40          # ignore the top 40 % of the frame for cans
    max_centroid_jump_px: int = 80           # tracker gate
    min_area_red: int = 1200
    water_on_ratio: float = 0.15             # > 15 % blue pixels: water
    water_off_ratio: float = 0.015           # < 1.5 % blue pixels: clear (hysteresis)
    show_debug: bool = True
    can: CanFilterConfig = field(default_factory=CanFilterConfig)


@dataclass(frozen=True)
class ControlConfig:
    # Mission
    cans_per_deposit: int = 40
    # S-shaped search pattern
    s_straight_s: float = 1.8
    s_curve_s: float = 1.5
    # Approach and pick-up
    min_centered_frames: int = 4
    max_lost_frames: int = 10
    reached_can_pause_s: float = 2.0
    error_threshold: float = 0.25
    kp: float = 24.0
    kd: float = 5.0
    # Deposit ("trailer" manoeuvre)
    red_close_width_px: int = 100
    turn_to_deposit_s: float = 3.0
    turn_backup_s: float = 1.0
    deposit_open_s: float = 2.0
    # Stuck detector
    stuck_time_s: float = 40.0
    stuck_wiggle_s: float = 1.2
    stuck_wiggle_period_s: float = 0.2
    stuck_escape_s: float = 1.0
    # Water avoidance
    water_stop_s: float = 0.4
    water_min_back_s: float = 1.5
    water_avoid_timeout_s: float = 8.0
    water_stuck_s: float = 3.0
    water_rock_period_s: float = 1.0
    water_extra_back_s: float = 2.0
    water_turn_s: float = 2.5
    # Loop timing
    tick_period_s: float = 0.08              # ~12 Hz
    water_tick_period_s: float = 0.05
    # Kalman
    kalman_q: float = 0.01
    kalman_r: float = 0.10
