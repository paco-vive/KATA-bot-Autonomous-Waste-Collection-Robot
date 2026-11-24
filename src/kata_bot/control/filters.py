"""Signal processing for target tracking: 1D Kalman filter and PD controller."""
from __future__ import annotations


class KalmanFilter1D:
    """Constant-position Kalman filter that smooths the lateral error."""

    def __init__(self, q: float = 0.01, r: float = 0.10) -> None:
        self.q = q
        self.r = r
        self.reset()

    def reset(self) -> None:
        self.x = 0.0
        self.p = 1.0

    def update(self, z: float) -> float:
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (z - self.x)
        self.p *= 1.0 - k
        return self.x


class PDController:
    def __init__(self, kp: float, kd: float) -> None:
        self.kp = kp
        self.kd = kd
        self.reset()

    def reset(self) -> None:
        self.prev_error = 0.0

    def update(self, error: float, dt: float) -> float:
        d_error = (error - self.prev_error) / max(dt, 0.001)
        self.prev_error = error
        return self.kp * error + self.kd * d_error


class TargetTracker:
    """Kalman + PD for one kind of target (a can or the red ring)."""

    def __init__(self, kp: float, kd: float, q: float, r: float) -> None:
        self.kalman = KalmanFilter1D(q, r)
        self.pd = PDController(kp, kd)

    def reset(self) -> None:
        self.kalman.reset()
        self.pd.reset()

    def update(self, raw_error: float, dt: float) -> tuple[float, float]:
        """Return (filtered error, steering correction)."""
        filtered = self.kalman.update(raw_error)
        return filtered, self.pd.update(filtered, dt)
