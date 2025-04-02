import communication
import gui
import joysticks
import time
import threading
# import video_stream
import platform

class Main:
    def _update_pid(self):
        self.i_pid.pitch_kp, self.i_pid.pitch_ki, self.i_pid.pitch_kd, self.i_pid.pitch_me, self.i_pid.pitch_mo, self.i_pid.pitch_il, self.i_pid.roll_kp, self.i_pid.roll_ki, self.i_pid.roll_kd, self.i_pid.roll_me, self.i_pid.roll_mo, self.i_pid.roll_il = self.i_gui.get_pid_param()
        self.i_communication.pid_send = 1

    def __init__(self):
        print("Fixed Wing Plane Remote Control System")
        print("Copyright Eric Jin 2024")
        
        print("Initializing joysticks...")
        self.i_joysticks = joysticks.Joysticks()
        if (self.i_joysticks.identify()):
            self.i_joysticks.start()
            print("Done!")
        else:
            print("Failed!")
            print("Exiting...")
            # exit()

        print("Initializing communication...")        
        
        ports = communication.Communication.detect_ports()
        if (platform.system() == "Linux"):
            if "USB Serial" in ports:
                port = ports["USB Serial"]
            elif "CP2102 USB to UART Bridge Controller - CP2102 USB to UART Bridge Controller" in ports:
                port = ports["CP2102 USB to UART Bridge Controller - CP2102 USB to UART Bridge Controller"]
            else:
                print("No USB Serial found")
                exit()
        elif (platform.system() == "Windows"):
            for p in ports:
                if "CH340" in p:
                    port = ports[p]
                    break
                elif "CP210x" in p:
                    port = ports[p]
                    break
            else:
                print("No CH340 found")
                exit()
        else:
            print("Unknown platform")
            exit()
        
        print("Port:", port)

        self.i_data = communication.planeData()
        self.i_cmd = communication.stickCommand()
        self.i_mode = communication.modeCommand()
        self.i_pid = communication.pidCommand()
        self.i_communication = communication.Communication(port, self.i_cmd, self.i_data, self.i_mode, self.i_pid)
        self.i_communication.start(0.05)
        print("Done!")

        # Video
        # print("Initializing video...")
        # video_stream.start_video(self.SERVER_IP, self.video_port)

        print("Initializing GUI...")
        self.i_gui = gui.PFD(self._update_pid)
        self.gui_data_dict = {
            "pitch": 0, "roll": 0, 
            "air_speed": 0, "gnd_speed": 0, "accel": 0,
            "psr_alt": 0, "tof_alt": 0,"vs": 0,
            "hdg": 0,
            "FD_ON": True, 
            "tar_speed": 0, "tar_alt": 0, "tar_hdg": 0,
            "sta" : {
                "AIL MANUAL": True, "ELE MANUAL": True, "RUD MANUAL": True,
                "AIL STABLE": False, "ELE STABLE": False, "RUD STABLE": False,
                "AIL LCKATT": False, "ELE LCKATT": False, "RUD LCKATT": False,
            },
            "eng_1": True, "eng_2": True, "thrust_1": 12.3, "thrust_2": 23.4,
            "volt_main": 114514, 
            "volt_bus": 114514, "cpu_tmp": 1919, 
        }
        print("dict init done")

        self.mainloop_thread = threading.Thread(target=self.logic_mainloop)
        self.mainloop_thread.start()
        self.i_gui.run()
        print("Run!")
        self.mainloop_thread.join()


    def logic_mainloop(self):

        alt_queue = []
        ALT_QUEUE_LEN = 25


        while True:
            gui_state = self.i_gui.get_state()
            if gui_state == False:
                break
                
            # Update commands from joysticks to communication
            try:
                # control surface
                x, y, z = [x * 32767 for x in self.i_joysticks.get_xyz()] # so ugly way
                self.i_cmd.aileron = int(x)
                self.i_cmd.elevator = int(y)
                self.i_cmd.rudder = int(z)

                # mode setting
                mode_sw = self.i_joysticks.get_sw_left()
                if mode_sw == self.i_joysticks.SW_UP:
                    self.i_mode.mode = 1
                elif mode_sw == self.i_joysticks.SW_MID:
                    self.i_mode.mode = 2
                elif mode_sw == self.i_joysticks.SW_DOWN:
                    self.i_mode.mode = 3

            except:
                pass

            # Update QNH
            self.i_cmd.sea_level_pa = int(self.i_gui.get_qnh() * 100)

            # Attitude
            self.gui_data_dict["pitch"] = -communication.planeData.imu_r2r(self.i_data.pitch)
            self.gui_data_dict["roll"] = -communication.planeData.imu_r2r(self.i_data.roll)
            self.gui_data_dict["hdg"] = -communication.planeData.imu_r2r(self.i_data.yaw)
            # print(self.gui_data_dict["roll"], self.gui_data_dict["pitch"], self.gui_data_dict["pitch"])

            # Altitude and speed
            self.gui_data_dict["accel"] = communication.planeData.imu_r2r(self.i_data.accel_y) * 5
            
            altitude = self.psr2alt(communication.planeData.psr_r2r(self.i_data.pressure), self.i_cmd.sea_level_pa / 100)
            
            alt_queue.append(altitude)
            if len(alt_queue) > ALT_QUEUE_LEN:
                alt_queue.pop(0)
            altitude = sum(alt_queue) / len(alt_queue)
            
            self.gui_data_dict["vs"] = (altitude - self.gui_data_dict["psr_alt"]) / 0.02 / 0.00508 # m/s, require filtering!!0.00508
            self.gui_data_dict["psr_alt"] = altitude

            # temperatures
            self.gui_data_dict["temperature"] = communication.planeData.tmp_r2r(self.i_data.temperature)
            # self.gui_data_dict["cpu_tmp"] = communication.planeData.cputmp_r2r(self.i_data.cpu_temp)

            # Voltage
            self.gui_data_dict["volt_main"] = communication.planeData.vbat_r2r(self.i_data.volt_main)
            # self.gui_data_dict["volt_bus"] = communication.planeData.vbus_r2r(self.i_data.volt_bus)
            

            # Control surfaces
            self.gui_data_dict["elevator"] = self.i_data.elevator
            self.gui_data_dict["aileron_l"] = self.i_data.aileron
            self.gui_data_dict["aileron_r"] = -self.i_data.aileron
            self.gui_data_dict["rudder"] = self.i_data.rudder_l

            # print(self.gui_data_dict["pitch"])
            # print("state =", self.i_data.state)

            # Engine
            # # currently use set values
            # self.gui_data_dict["eng_1"] = self.i_data.eng_1 >= 0
            # self.gui_data_dict["thrust_1"] = self.i_data.eng_1
            # self.gui_data_dict["eng_2"] = self.i_data.eng_2 >= 0
            # self.gui_data_dict["thrust_2"] = self.i_data.eng_2
            # print(self.i_data.eng_1, self.i_data.eng_2)

            # print("pitch = ", self.gui_data_dict["pitch"])
            self.gui_data_dict["state"] = self.i_data.state
            self.i_gui.update(self.gui_data_dict)

            # print(to_float(i_data.angle_x), "\t", to_float(i_data.angle_y), "\t", to_float(i_data.angle_z))   
            # print(i_cmd.eng_1, i_cmd.eng_2)

            time.sleep(0.025)

        # Exit
        print("Stopping modules...")
        self.i_joysticks.stop()
        self.i_gui.stop()
        self.i_communication.stop()
        print("Done!")

        print("Exiting...")
        exit()

    @staticmethod
    def psr2alt(psr, qnh):
        return 44330 * (1-pow((psr / 100) / qnh, 0.1903))




if __name__ == "__main__":
    main = Main()
    while True:
        time.sleep(1)
