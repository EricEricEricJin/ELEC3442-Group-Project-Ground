# Copyright Eric Jin 2020
# Modified in 2024 by Eric Jin 

from threading import Thread
from socket import *
import struct
import time
import crc16


# KEEP SYNCHRONIZED WITH PLANE CODE!!!
class groundCommand:
    eng_1,eng_2 = 0, 0 
    opmode_elevator, opmode_aileron, opmode_rudder = 0,0,0
    elevator, aileron, rudder = 0,0,0
    thrust_1, thrust_2 = 0,0
    trim_elevator, trim_aileron, trim_rudder = 0,0,0

    sea_level_pa = 0

    update_time_ms = 0

    pack_format = "".join(["=","B", "hhh", "HH", "hhh", "I", "I"])

    def packed(self):
        state_byte = (self.eng_1<<7)|(self.eng_2<<6)|(self.opmode_elevator<<4)|(self.opmode_aileron<<2)|(self.opmode_rudder)
        # print("state byte =", state_byte)
        ret = struct.pack(self.pack_format, state_byte,
                          self.elevator, self.aileron, self.rudder,
                          self.thrust_1, self.thrust_2,
                          self.trim_elevator, self.trim_aileron, self.trim_rudder,
                          self.sea_level_pa,
                          self.update_time_ms)
        crc = crc16.crc16(0xffff, ret, len(ret))
        crc_packed = struct.pack("H", crc)
        return ret + crc_packed

# KEEP SYNCHRONIZED WITH PLANE CODE!!!
class planeData:
    accel_x, accel_y, accel_z = 0,0,0
    omega_x, omega_y, omega_z = 0,0,0
    mag_x, mag_y, mag_z = 0,0,0
    roll, pitch, yaw = 0,0,0

    tof = 0
    air_spd = 0

    volt_main, volt_bus, volt_aux = 0,0,0
    pressure, temperature = 0, 0

    elevator, aileron_l, aileron_r, rudder = 0, 0, 0, 0

    update_time_ms = 0
    crc_calc = 0

    pack_format = "".join(["=", "hhh"*4, "H"*2, "B"*3, "hh", "bbbb","I", "H"])

    def size(self):
        return struct.calcsize(self.pack_format)
    
    def unpack(self, packed):
        unpacked = struct.unpack(self.pack_format, packed)
        # print("len packed =", len(packed))
        crc_calc = crc16.crc16(0xffff, packed, len(packed)-2)
        if crc_calc == unpacked[-1]:
            # print("unpacked", unpacked)
            # checksum correct
            self.accel_x, self.accel_y, self.accel_z,   \
            self.omega_x, self.omega_y, self.omega_z,   \
            self.mag_x, self.mag_y, self.mag_z,         \
            self.roll, self.pitch, self.yaw,            \
            self.tof,   \
            self.air_spd,   \
            self.volt_main, self.volt_bus, self.volt_aux,   \
            self.pressure, self.temperature,                \
            self.elevator, self.aileron_l, self.aileron_r, self.rudder, \
            self.update_time_ms, self.crc_calc = unpacked
        else:
            # checksum wrong
            print("CRC error!", crc_calc, unpacked[-1])

    @staticmethod
    def imu_r2r(x):
        ret = x / 32768 * 180
        return ret - 2 if ret >= 1 else ret

    @staticmethod
    def tmp_r2r(x):
        return x / 100.0

    @staticmethod
    def psr_r2r(x):
        return x / 10.0 + 1e5

    @staticmethod
    def vbat_r2r(x):
        return x / 255.0 * 12.9 # todo

    @staticmethod
    def vbus_r2r(x):
        return x / 255.0 * 5.5
    
    def vaux_r2r(x):
        return x / 255.0 * 4.3

class Communication:
    def __init__(self, my_port, server_ip, server_port, cmd, data):
        self.server_addr = (server_ip, server_port)
        self.my_addr = ("", my_port)

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
            # print("send", packed)
            self.sock.sendto(packed, self.server_addr)
            time.sleep(self.send_period)

    def _recving(self):
        while self.running:
            try:
                # print("size =", self.data.size())
                packed = self.sock.recv(self.data.size())
                # print("packed =", packed)
                self.data.unpack(packed)
            except Exception as e:
                print(e)

    def stop(self):
        self.running = False
        self.sock.shutdown(SHUT_RDWR)
        self.t_sending.join()
        self.t_recving.join()




if __name__ == "__main__":
    SERVER_IP = "154.221.20.43"
    SERVER_PORT = 1235
    MY_PORT = 1233

    cmd = groundCommand()
    data = planeData()

    ComTest = Communication(MY_PORT, SERVER_IP, SERVER_PORT, cmd, data)
    cmd.thrust_1 = 123
    cmd.thrust_2 = 234
    ComTest.start(0.5)
    while True:
        # print(planeData.imu_r2r(data.roll), planeData.imu_r2r(data.pitch), planeData.imu_r2r(data.yaw))
        print(psr2alt(planeData.psr_r2r(data.pressure), 996), planeData.tmp_r2r(data.temperature))
        time.sleep(0.5)