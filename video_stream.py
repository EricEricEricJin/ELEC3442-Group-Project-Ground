import os
from socket import *
import threading

def start_video(IP, port):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("", port))
    sock.sendto(b"a", (IP, port))
    sock.close()
    cmd = f"ffplay.exe udp://{IP}:{port} -fflags nobuffer -flags low_delay -framedrop &"
    t = threading.Thread(target=lambda: os.system(cmd))
    t.start()

if __name__ == "__main__":
    start_video("154.221.20.43", 1237)
    print("Done")