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

        print("UDP target IP: %s" % self._ip)
        print("UDP target port: %s" % self._port)
        print("message: %s" % message)

        sock.sendto(message, (self._ip, self._port))