
#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

# ---- Pin-Setup (BCM) ----
PINS = [17, 18, 27, 22]  # ULN2003 IN1..IN4
GPIO.setmode(GPIO.BCM)
for p in PINS:
    GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)

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

STEPS_PER_REV = 4096  # Half-Step

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

def rotate_degrees(deg, speed_hz=1000):
    """Dreht um deg Grad (positiv=vorwärts, negativ=rückwärts)."""
    direction = 1 if deg >= 0 else -1
    steps = int(abs(deg) * STEPS_PER_REV / 360.0)
    delay_s = 1.0 / float(speed_hz)
    step_sequence(steps, delay_s=delay_s, direction=direction)

def rotate_revolutions(revs, speed_hz=1000):
    """Dreht um revs Umdrehungen (positiv/negativ)."""
    direction = 1 if revs >= 0 else -1
    steps = int(abs(revs) * STEPS_PER_REV)
    delay_s = 1.0 / float(speed_hz)
    step_sequence(steps, delay_s=delay_s, direction=direction)

def release():
    """Spulen stromlos (weniger Wärme)."""
    for p in PINS:
        GPIO.output(p, GPIO.LOW)

if __name__ == "__main__":
    try:
        print("Vorwärts 1 Umdrehung @ 800 Hz")
        rotate_revolutions(1.0, speed_hz=800)

        print("Rückwärts 90° @ 800 Hz")
        rotate_degrees(-90, speed_hz=800)
    finally:
        release()
        GPIO.cleanup()
        print("Fertig & GPIO freigegeben.")
