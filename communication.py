# Copyright Eric Jin 2020
# Modified in 2024 by Eric Jin 

from threading import Thread
from socket import *
import struct
import time
import crc16


# KEEP SYNCHRONIZED WITH PLANE CODE!!!
class groundCommand:
    elevator, aileron, rudder = 0,0,0
    eng_1,eng_2, thrust_1, thrust_2 = 0,0,0,0
    op_mode, trim_elevator, trim_aileron = 0,0,0
    update_time_ms = 0

    pack_format = "".join(["hhh", "BBHH", "Bhh", "I"])

    def packed(self):
        ret = struct.pack(self.pack_format, self.elevator, self.aileron, self.rudder,
                          self.eng_1, self.eng_2, self.thrust_1, self.thrust_2,
                          self.op_mode, self.trim_elevator, self.trim_aileron,
                          self.update_time_ms)
        crc = crc16.crc16(0xffff, ret, len(ret))
        crc_packed = struct.pack("H", crc)
        return ret + crc_packed

# KEEP SYNCHRONIZED WITH PLANE CODE!!!
class planeData:
    accel_x, accel_y, accel_z = 0,0,0
    omega_x, omega_y, omega_z = 0,0,0
    mag_x, mag_y, mag_z = 0,0,0
    angle_x, angle_y, angle_z = 0,0,0

    tof = 0
    air_spd = 0

    volt_main, volt_bus, volt_aux = 0,0,0
    altitude = 0
    crc_calc = 0

    pack_format = "".join(["hhh"*4, "H"*2, "B"*3, "H", "H"])

    def size(self):
        return 0
    
    def unpack(self, packed):
        unpacked = struct.unpack(self.pack_format, packed)
        if crc16.crc16(0xffff, packed, len(packed)-2) == unpacked[-1]:
            # checksum correct
            self.accel_x, self.accel_y, self.accel_z,     \
            self.omega_x, self.omega_y, self.omega_z,     \
            self.mag_x, self.mag_y, self.mag_z,           \
            self.angle_x, self.angle_y, self.angle_z,     \
            self.tof,                                     \
            self.air_spd,                                 \
            self.volt_main, self.volt_bus, self.volt_aux, \
            self.altitude, self.crc_calc = unpacked
        else:
            # checksum wrong
            pass

class Communication:
    def __init__(self, ip, port, cmd, data):
        self.server_addr = (ip, port)
        self.my_addr = ("", port)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(self.my_addr)

        self.cmd = cmd
        self.data = data

    def start(self, send_period):

        self.send_period = send_period

        self.running = True

        self.t_sending = Thread(target = self._sending)
        self.t_recving = Thread(target = self._recving)
        self.t_recving.start()
        self.t_sending.start()


    def _sending(self):
        while self.running:
            packed = self.cmd.packed()
            self.sock.sendto(packed, self.server_addr)
            time.sleep(self.send_period)

    def _recving(self):
        while self.running:
            packed = self.sock.recv(self.data.size())
            self.data.unpack(packed)

    def stop(self):
        self.running = False
        self.sock.shutdown(SHUT_RDWR)
        self.t_sending.join()
        self.t_recving.join()

if __name__ == "__main__":
    ComTest = Communication()
    ComTest.run()