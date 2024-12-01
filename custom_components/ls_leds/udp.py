import socket


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
