from threading import Thread
from socket import *

class videoReceiver:
    def __init__(self, my_port, server_ip, server_port) -> None:
        self.server_addr = (server_ip, server_port)
        self.my_addr = ("", my_port)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind()