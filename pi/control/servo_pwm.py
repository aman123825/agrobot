"""Pan/tilt servo driver for the aimed-spray nozzle (FC-01).

Drives two SG90 servos (pan + tilt) from the Pi using hardware-PWM-capable
pins (GPIO13 and GPIO19, see config.GPIO). RPi.GPIO software PWM is used for
portability; the pins are hardware-PWM capable so a future swap to pigpio for
jitter-free pulses is straightforward.

All GPIO access is guarded: on a machine without RPi.GPIO (or off the Pi) the
driver imports and runs as a no-op, while still tracking the commanded angles
so the orchestrator logic and tests work everywhere.

Angle convention matches ``ai.spray_targeting``:
  * pan  > 0 -> right, < 0 -> left
  * tilt > 0 -> down,  < 0 -> up
The mechanical centre (0, 0) maps to the servo's 90-degree position.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config  # noqa: E402

logger = logging.getLogger(__name__)

SERVO_PWM_HZ = 50          # 20 ms frame for analog hobby servos
SERVO_MIN_DUTY = 2.5       # ~0.5 ms pulse -> 0 deg
SERVO_MAX_DUTY = 12.5      # ~2.5 ms pulse -> 180 deg
SERVO_RANGE_DEG = 180.0


def angle_to_duty(angle_deg: float) -> float:
    """Map a 0..180 servo angle to an RPi.GPIO PWM duty-cycle percentage."""
    angle_deg = max(0.0, min(SERVO_RANGE_DEG, angle_deg))
    return SERVO_MIN_DUTY + (angle_deg / SERVO_RANGE_DEG) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)


def aim_to_servo_angles(pan_deg: float, tilt_deg: float) -> tuple[float, float]:
    """Convert signed aim angles (centre 0) to 0..180 servo angles (centre 90)."""
    pan_servo = max(0.0, min(180.0, 90.0 + pan_deg))
    tilt_servo = max(0.0, min(180.0, 90.0 + tilt_deg))
    return (pan_servo, tilt_servo)


class PanTiltServo:
    def __init__(self, pan_pin: int | None = None, tilt_pin: int | None = None):
        self.pan_pin = pan_pin if pan_pin is not None else config.GPIO["servo_pan"]
        self.tilt_pin = tilt_pin if tilt_pin is not None else config.GPIO["servo_tilt"]
        self.pan_deg = 0.0
        self.tilt_deg = 0.0
        self._gpio = None
        self._pan_pwm = None
        self._tilt_pwm = None
        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pan_pin, GPIO.OUT)
            GPIO.setup(self.tilt_pin, GPIO.OUT)
            self._gpio = GPIO
            self._pan_pwm = GPIO.PWM(self.pan_pin, SERVO_PWM_HZ)
            self._tilt_pwm = GPIO.PWM(self.tilt_pin, SERVO_PWM_HZ)
            self._pan_pwm.start(angle_to_duty(90.0))
            self._tilt_pwm.start(angle_to_duty(90.0))
            logger.info("PanTiltServo ready (pan=GPIO%d tilt=GPIO%d)",
                        self.pan_pin, self.tilt_pin)
        except Exception as exc:
            logger.warning("RPi.GPIO unavailable (%s); servo calls are no-ops", exc)
            self._gpio = None

    def point(self, pan_deg: float, tilt_deg: float) -> tuple[float, float]:
        """Aim the nozzle at signed (pan, tilt) angles. Returns the servo angles."""
        self.pan_deg = pan_deg
        self.tilt_deg = tilt_deg
        pan_servo, tilt_servo = aim_to_servo_angles(pan_deg, tilt_deg)
        if self._pan_pwm is not None:
            self._pan_pwm.ChangeDutyCycle(angle_to_duty(pan_servo))
        if self._tilt_pwm is not None:
            self._tilt_pwm.ChangeDutyCycle(angle_to_duty(tilt_servo))
        return (pan_servo, tilt_servo)

    def center(self) -> None:
        """Return both servos to the mechanical centre."""
        self.point(0.0, 0.0)

    def close(self) -> None:
        """Stop PWM and release the GPIO channels (guarded)."""
        try:
            if self._pan_pwm is not None:
                self._pan_pwm.stop()
            if self._tilt_pwm is not None:
                self._tilt_pwm.stop()
            if self._gpio is not None:
                self._gpio.cleanup([self.pan_pin, self.tilt_pin])
        except Exception as exc:
            logger.debug("PanTiltServo close failed (%s)", exc)
