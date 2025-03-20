import serial
import struct
from crc8 import crc8
from crc16 import crc16
import time

from joysticks_hand import Joysticks

class Packet:
    SOF = 0xA5
    CMD_ID = 0x02

    x, y = 0, 0

    pack_format = "".join(["=", "B", "B", "H"])

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def __bytes__(self):
        payload = struct.pack("=hh", self.x, self.y)
        payload_len = len(payload)

        buf = struct.pack(self.pack_format, self.SOF, self.CMD_ID, payload_len)
        crc8_val = crc8(0xff, buf, len(buf))
        buf += struct.pack("B", crc8_val)
        

        buf += payload
        crc16_val = crc16(0xffff, payload, payload_len)
        buf += struct.pack("H", crc16_val)

        return buf


if __name__ == "__main__":

    packet = Packet()
    ser = serial.Serial('/dev/ttyUSB0', 115200)

    js = Joysticks()
    js.identify()
    js.start()

    while True:
        try:
            x, y = js.get_ss_xy()
            x = int(x * 32768)
            x = -32768 if x < -32768 else 32767 if x > 32767 else x
            y = int(y * 16384)
            y = -32768 if y < -32768 else 32767 if y > 32767 else y
            print(x, y)
            packet.set_xy(x, y)
            ser.write(bytes(packet))
            time.sleep(0.03)
        except KeyboardInterrupt:
            break

    js.stop()
    ser.close()

