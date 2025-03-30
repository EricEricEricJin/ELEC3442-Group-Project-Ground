# Copyright Eric Jin 2020
# Modified in 2024 by Eric Jin 

# TRANS_BAUD = 115200
TRANS_BAUD = 57600

from threading import Thread
from socket import *
import struct
import time
from crc16 import crc16
from crc8 import crc8
import serial
import serial.tools.list_ports

import platform
import csv

# KEEP SYNCHRONIZED WITH PLANE CODE!!!

def pack_payload_to_buf(cmd_id, payload):
    SOF = 0xA5
    head_pack_format = "".join(["=", "B", "B", "H"])
    payload_len = len(payload)

    buf = struct.pack(head_pack_format, SOF, cmd_id, payload_len)
    crc8_val = crc8(0xff, buf, len(buf))
    buf += struct.pack("B", crc8_val)
    
    buf += payload
    crc16_val = crc16(0xffff, payload, payload_len)
    buf += struct.pack("H", crc16_val)

    return buf


class stickCommand:
    sea_level_pa = 1e5

    CMD_ID = 0x02

    elevator, aileron, rudder = 0,0,0
    # thrust = 0
    left_sw, right_sw = 0, 0
    mid_butt, left_butt = 0, 0

    payload_pack_format = "".join(["=", "hhh", "B"])

    def __bytes__(self):
        payload = struct.pack(self.payload_pack_format, 
                              self.rudder, self.elevator, self.aileron,
                              (self.left_sw << 6) | (self.right_sw << 4) | (self.mid_butt << 1) | (self.left_butt) )
        
        return pack_payload_to_buf(self.CMD_ID, payload)


class modeCommand:
    CMD_ID = 0xff
    mode = 0

    def __bytes__(self):
        payload = struct.pack("=B", self.mode)
        return pack_payload_to_buf(self.CMD_ID, payload)


class pidCommand:
    CMD_ID = 0xee
    pitch_kp, pitch_ki, pitch_kd, pitch_me, pitch_mo, pitch_il = 0, 0, 0, 0, 0, 0
    roll_kp, roll_ki, roll_kd, roll_me, roll_mo, roll_il = 0, 0, 0, 0, 0, 0

    def __bytes__(self):
        payload = struct.pack(12*'f', 
                              self.pitch_kp, self.pitch_ki, self.pitch_kd, self.pitch_me, self.pitch_mo, self.pitch_il,
                              self.roll_kp, self.roll_ki, self.roll_kd, self.roll_me, self.roll_mo, self.roll_il)
        return pack_payload_to_buf(self.CMD_ID, payload)


# KEEP SYNCHRONIZED WITH PLANE CODE!!!
class planeData:
    # SOF = 0xA5
    # DATA_ID = 0x03

    accel_x, accel_y, accel_z = 0,0,0
    omega_x, omega_y, omega_z = 0,0,0
    mag_x, mag_y, mag_z = 0,0,0
    roll, pitch, yaw = 0,0,0

    volt_main = 0
    pressure, temperature = 0, 0

    elevator, aileron, rudder_l, rudder_r = 0, 0, 0, 0

    state = 0

    pack_format = "".join(["=", "hhh"*4, "H", "hh", "b"*4, "B", "H"])

    LOG_FILE_NAME = "log.csv"

    def __init__(self):

        self.log_t0 = time.time()

        self.f = open(self.LOG_FILE_NAME, "w")
        self.cw = csv.writer(self.f)
        self.cw.writerow(["timestamp", "accel_x", "accel_y", "accel_z",
                          "omega_x", "omega_y", "omega_z",
                          "mag_x", "mag_y", "mag_z",
                          "roll", "pitch", "yaw",
                          "volt_main",
                          "pressure", "temperature",
                          "elevator", "aileron", "rudder_l", "rudder_r"])
        self.f.flush()

    def __del__(self):
        self.f.close()


    def size(self):
        return struct.calcsize(self.pack_format)

    def log_to_file(self):
        self.cw.writerow([int((time.time() - self.log_t0) * 1000),
                          self.accel_x, self.accel_y, self.accel_z, 
                          self.omega_x, self.omega_y, self.omega_z, 
                          self.mag_x, self.mag_y, self.mag_z, 
                          self.roll, self.pitch, self.yaw, 
                          self.volt_main, 
                          self.pressure, self.temperature, 
                          self.elevator, self.aileron, self.rudder_l, self.rudder_r])
        self.f.flush()

    def unpack(self, packed):
        unpacked = struct.unpack(self.pack_format, packed)
        print("len packed =", len(packed))
        crc_calc = crc16(0xffff, packed, len(packed)-2)

        if crc_calc == unpacked[-1]:
            # print("unpacked", unpacked)
            # checksum correct
            self.accel_x, self.accel_y, self.accel_z,                   \
            self.omega_x, self.omega_y, self.omega_z,                   \
            self.mag_x, self.mag_y, self.mag_z,                         \
            self.roll, self.pitch, self.yaw,                            \
            self.volt_main,                                             \
            self.pressure, self.temperature,                            \
            self.elevator, self.aileron, self.rudder_l, self.rudder_r,  \
            self.state, _  = unpacked
            
            try:
                self.log_to_file()
            except Exception as e:
                print("Log Error", e)

            # print("roll, yaw, pitch", self.roll, self.yaw, self.pitch)
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
        # return x / 255.0 * 12.9 # todo
        CAL_COEFF = 1.314
        return x * 4.3 / 1000.0 * CAL_COEFF

    @staticmethod
    def vbus_r2r(x):
        return x / 255.0 * 5.5
    
    @staticmethod
    def vaux_r2r(x):
        return x / 255.0 * 4.3
    
    @staticmethod
    def cputmp_r2r(x):
        return x / 100.0



class Communication:
    def __init__(self, port, cmd, data, mode, pid):
        self.ser = serial.Serial(port, TRANS_BAUD, timeout=None)

        self.cmd = cmd
        self.data = data
        self.mode = mode
        self.pid = pid

        self.pid_send = 0

        self.prev_mode_val = None

    @staticmethod
    def detect_ports():
        ports = serial.tools.list_ports.comports()
        ret = dict()
        for p in ports:
            ret[p.description] = p.device
        return ret
    

    def start(self, send_period):

        self.send_period = send_period

        self.running = True

        self.t_sending = Thread(target = self._sending)
        self.t_recving = Thread(target = self._recving)
        self.t_recving.start()
        self.t_sending.start()


    def _sending(self):
        while self.running:
            if (self.mode.mode != self.prev_mode_val):
                self.prev_mode_val = self.mode.mode
                self.ser.write(bytes(self.mode))
                print("mode changed to", self.mode.mode)
            
            if self.pid_send:
                self.ser.write(bytes(self.pid))
                print("pid changed to", self.pid.pitch_kp, self.pid.pitch_ki, self.pid.roll_kp, self.pid.roll_ki)
                self.pid_send = 0

            b = bytes(self.cmd)
            # print("send", packed)
            self.ser.write(b)
            time.sleep(self.send_period)



    def _recving(self):
        while self.running:
            try:
                # print("size =", self.data.size())
                if self.ser.read(1) == b'\xa5':
                    head = b'\xa5' + self.ser.read(4)
                    sof, cmd_id, payload_len, crc8_val = struct.unpack("=BBHB", head)
                    if crc8(0xff, head, 4) != crc8_val:
                        print("CRC error!")
                        continue
                    
                    # print("head", head, sof, cmd_id, payload_len)
                    payload = self.ser.read(payload_len+2)
                    self.data.unpack(payload)
            except Exception as e:
                print(e)


    def stop(self):
        self.running = False
        self.ser.close()
        self.t_sending.join()
        self.t_recving.join()




if __name__ == "__main__":
    ports = Communication.detect_ports()
    
    port = ports["USB Serial"]
    print(port)

    cmd = stickCommand()
    data = planeData()
    mode = modeCommand()

    ComTest = Communication(port, cmd, data, mode)
    ComTest.start(0.5)

    while True:
        print(data.pitch)
        time.sleep(0.5)
    # while True:
    #     # print(planeData.imu_r2r(data.roll), planeData.imu_r2r(data.pitch), planeData.imu_r2r(data.yaw))
    #     print(psr2alt(planeData.psr_r2r(data.pressure), 996), planeData.tmp_r2r(data.temperature))
    #     time.sleep(0.5)