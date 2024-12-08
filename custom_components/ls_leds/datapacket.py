class ReadCommand:
    def __init__(self):
        pass

    def execute(self, strip_ip) -> None:
        payload = [0, 0, 0, 0, 1, 0]
        return f"00ff0012"


class DataPacket:
    """payload:
    packet:
            8 bits red
            8 bits green
            8 bits blue
            4 bits command id
                0x0 WRITE Command
                0x1 READ Command
                0x2 ID Command - TBD
            4 bits strip id
                0x0 strip id 0
                0x1 strip id 1
                0xF strip id 2 (ALL) (deprecated).
    """  # noqa: D205

    def __init__(self, raw_input):
        self.raw_input = raw_input
        self._r = self.raw_input[0] & 0xFF
        self._g = self.raw_input[1] & 0xFF
        self._b = self.raw_input[2] & 0xFF
        self._command = (self.raw_input[3] >> 4) & 0xF
        self._led_strip_id = self.raw_input[3] & 0xF

    def strip_id(self):
        return self._led_strip_id

    def red(self):
        return self._r

    def green(self):
        return self._g

    def blue(self):
        return self._b

    def command(self):
        return self._command

    def color(self):
        return (self._r, self._g, self._b)

    def invert_color(self):
        return (255 - self._r, 255 - self._g, 255 - self._b)
    
    @staticmethod
    def construct_rgb(red: int, green: int, blue: int, strip_index: int) -> str:
        """Construct an rgb byte array."""
        rgb_packet = []
        rgb_packet.append(red)
        rgb_packet.append(green)
        rgb_packet.append(blue)
        rgb_packet.append(strip_index)

        return bytearray(rgb_packet)
