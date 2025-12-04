class MockCompass:
    def get_magnet(self):
        return (12.3, -4.8, 0.5)

class MockGPS:
    def read(self):
        return {"latitude": 47.55702056936907, "longitude": 8.891574232825205, "altitude": 500, "satellites": 7}
class MockOLED:
    def display_text(self, text):
        print(f"[OLED MOCK] {text}")

class MockStepper:
    def step(self, steps=1, direction=1):
        print(f"[STEPPER MOCK] Steps: {steps}, Direction: {direction}")
