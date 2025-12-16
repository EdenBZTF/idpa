class MockCompass:
    def get_magnet(self):
        return (12.3, -4.8, 0.5)

class MockGPS:
    def read(self):
        return {"latitude":47.51629566199016, "longitude": 9.438055388669438, "altitude": 500, "satellites": 7} #fpt arbon
class MockOLED:
    def display_text(self, text):
        print(f"[OLED MOCK] {text}")

class MockStepper:
    def step(self, steps=1, direction=1):
        print(f"[STEPPER MOCK] Steps: {steps}, Direction: {direction}")

