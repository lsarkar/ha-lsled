
# if we are running a virtual rpi led test then we don't need to import the platform specific dependencies
try:
    from leds.neopixel import Neopixel
except ImportError:
    raise ValueError("Cannot find neopixel library")


class PicoLedStrip():

    def __init__(self, pin: int, num_leds: int, state_machine=0):
        self.pixels = Neopixel(num_leds, state_machine, pin, "GRB")

    def on(self):
        self.write_all(255, 255, 255)

    def off(self):
        self.write_all(0, 0, 0)

    def write_all(self, red: int, green: int, blue: int):
        self._write_to_strip(red, green, blue)

    def brightness(self, value: int):
        self.pixels.brightness(value)

    def _write_to_strip(self, red: int, green: int, blue: int):
        # low level library interaction with device
        self.pixels.fill((red, green, blue))
        self.pixels.show()
