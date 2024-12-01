import socket
import re


class UdpHandler:
    def __init__(self, udp_ip: str, udp_port: int) -> None:
        self._ip = udp_ip
        self._port = udp_port

    def send(self, message: str) -> None:
        sock = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM,
        )  # UDP

        print(f"UDP target {self._ip}:{self._port}")
        print("message: %s" % message)

        sock.sendto(message, (self._ip, self._port))

    @staticmethod
    def validate_ipv4(ip: str):
        pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return bool(pattern.match(ip))

    @staticmethod
    def validate_ipv6(ip: str):
        pattern = re.compile(
            r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,7}:$|^::([0-9a-fA-F]{1,4}:){0,7}[0-9a-fA-F]{1,4}$"
        )
        return bool(pattern.match(ip))

    @staticmethod
    def validate_ip(ip: str):
        if UdpHandler.validate_ipv4(ip):
            return True
        elif UdpHandler.validate_ipv6(ip):
            return True
        else:
            return False
