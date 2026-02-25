#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

# ---- Pin-Setup (BCM) ----
PINS = [17, 18, 27, 22]  # ULN2003 IN1..IN4
GPIO.setmode(GPIO.BCM)
for p in PINS:
    GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    

STEPS_PER_REV = 4096  # Half-Step


# Half-Step Sequenz (8 Muster)
HALF_STEP_SEQ = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1],
]

def step_sequence(n_steps, delay_s=0.001, direction=1):
    """Führt n_steps Musterwechsel aus (direction: 1=vorwärts, -1=rückwärts)."""
    seq = HALF_STEP_SEQ if direction == 1 else HALF_STEP_SEQ[::-1]
    idx = 0
    for _ in range(n_steps):
        pattern = seq[idx]
        for pin, val in zip(PINS, pattern):
            GPIO.output(pin, GPIO.HIGH if val else GPIO.LOW)
        time.sleep(delay_s)
        idx = (idx + 1) % len(seq)


def rotate_degrees(deg, speed_hz=300):
    """Dreht um deg Grad (positiv=vorwärts, negativ=rückwärts)."""
    direction = 1 if deg >= 0 else -1
    steps = int(abs(deg) * STEPS_PER_REV / 360.0)
    delay_s = 1.0 / float(speed_hz)
    step_sequence(steps, delay_s=delay_s, direction=direction)
    
def release():
    """Spulen stromlos (weniger Wärme)."""
    for p in PINS:
        GPIO.output(p, GPIO.LOW)
