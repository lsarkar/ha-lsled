from datapacket import DataPacket


class TestDataPacket:
    def test_correct_packet(self):
        payload = DataPacket(hex(0x00FF0012))
        assert payload.command == 1
