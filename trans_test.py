import serial
import struct
from crc8 import crc8
from crc16 import crc16
import time
import communication

# from joysticks_hand import Joysticks
from joysticks import Joysticks

class stickValPacket:
    SOF = 0xA5
    CMD_ID = 0x02

    x, y, z = 0, 0, 0

    pack_format = "".join(["=", "B", "B", "H"])

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __bytes__(self):
        payload = struct.pack("=hhh", self.x, self.y, self.z)
        payload_len = len(payload)

        buf = struct.pack(self.pack_format, self.SOF, self.CMD_ID, payload_len)
        crc8_val = crc8(0xff, buf, len(buf))
        buf += struct.pack("B", crc8_val)        

        buf += payload
        crc16_val = crc16(0xffff, payload, payload_len)
        buf += struct.pack("H", crc16_val)

        return buf


class opModePacket:
    SOF = 0xA5
    CMD_ID = 0xff

    mode = 0

    pack_format = "".join(["=", "B", "B", "H"])

    def set_mode(self, mode):
        self.mode = mode

    def __bytes__(self):
        payload = struct.pack("=B", self.mode)
        payload_len = len(payload)

        buf = struct.pack(self.pack_format, self.SOF, self.CMD_ID, payload_len)
        crc8_val = crc8(0xff, buf, len(buf))
        buf += struct.pack("B", crc8_val)

        buf += payload
        crc16_val = crc16(0xffff, payload, payload_len)
        buf += struct.pack("H", crc16_val)
        
        return buf


if __name__ == "__main__":

    packet = stickValPacket()

    mp = opModePacket()

    ports = communication.Communication.detect_ports()
    port = ports["USB Serial"]
    ser = serial.Serial(port, 115200)

    js = Joysticks()
    js.identify()
    js.start()

    mode_sw = None

    while True:
        try:
            # x, y = js.get_ss_xy()
            x, y, z = js.get_xyz()
            sw = js.get_sw_left()
            
            if mode_sw != sw:
                mode_sw = sw
                if mode_sw == js.SW_UP:
                    mp.set_mode(2)
                elif mode_sw == js.SW_MID:
                    mp.set_mode(3)
                elif mode_sw == js.SW_DOWN:
                    mp.set_mode(4)
                b = bytes(mp)
                ser.write(b)                
                print("mode: ", mp.mode, b)

            x = int(x * 32768)
            x = -32768 if x < -32768 else 32767 if x > 32767 else x
            y = int(y * 16384)
            y = -32768 if y < -32768 else 32767 if y > 32767 else y
            z = int(z * 16384)
            z = -32768 if z < -32768 else 32767 if z > 32767 else z
            
            print(x, y, z)
            packet.set_xyz(x, y, z)
            ser.write(bytes(packet))
            time.sleep(0.05)
        except KeyboardInterrupt:
            break

    js.stop()
    ser.close()

