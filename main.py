import communication
import gui
import joysticks
import time

def to_float(x):
    ret = x / 32768
    return ret - 2 if ret >= 1 else ret


if __name__ == "__main__":
    print("Fixed Wing Plane Remote Control System")
    print("Copyright Eric Jin 2024")
    
    # print("Special thanks to Percy Liu and Dryden Zhou for cooperation in 2020-2021")
    # print("Thanks to Uky Fan for helping building the plane model")



    print("Initializing joysticks...")
    i_joysticks = joysticks.Joysticks()
    if (i_joysticks.identify()):
        i_joysticks.start()
        print("Done!")
    else:
        print("Failed!")
        print("Exiting...")
        # exit()


    print("Initializing communication...")
    
    SERVER_IP = "154.221.20.43"
    SERVER_PORT = 1235
    MY_PORT = 1233
    
    print("Server IP:", SERVER_IP, "Server Port:", SERVER_PORT, "My Port:", MY_PORT)
    i_data = communication.planeData()
    i_cmd = communication.groundCommand()
    i_communication = communication.Communication(MY_PORT, SERVER_IP, SERVER_PORT, i_cmd, i_data)
    i_communication.start(0.1)
    print("Done!")

    # print("Initializing GUI...")
    # i_gui = gui.PFD()
    # gui_data_dict = {
    #     "pitch": 0, "roll": 0, 
    #     "air_speed": 0, "gnd_speed": 0, "accel": 0,
    #     "psr_alt": 0, "tof_alt": 0,"vs": 0,
    #     "hdg": 0,
    #     "long": 0, "lat": 0,
    #     "FD_ON": True, 
    #     "tar_speed": 10, "tar_alt": -10, "tar_hdg": 0, "tar_long": 0, "tar_lat": 0,
    #     "sta" : {
    #         "CRUISE": True, "MANU": True, "FAC": True, "AP_HDG": True,
    #         "TO/LD": True, "AUTO": True, "MCAS": True, "AP_ALT": True,
    #         "AP_SPD": True
    #     }
    # }
    # i_gui.run()
    # print("Done!")

    while True:
        # gui_state = i_gui.get_state()
        # if gui_state == 0:
        #     break
            
        # Update commands from joysticks to communication
        
        # control surface
        ss_x, ss_y, ss_z = [x * 32767 for x in i_joysticks.get_ss_xyz()] # so ugly way
        i_cmd.aileron = int(ss_x)
        i_cmd.elevator = int(ss_y)
        i_cmd.rudder = int(ss_z)

        # throttles
        th_t1, th_t2 = [int(x * 65535) for x in i_joysticks.get_th_thrust()]
        th_eng1, th_eng2 = i_joysticks.get_th_engon()
        i_cmd.eng_1 = int(th_eng1)
        i_cmd.eng_2 = int(th_eng2)
        i_cmd.thrust_1 = th_t1
        i_cmd.thrust_2 = th_t2

        # Update data from communication to GUI
        # gui_data_dict["pitch"] = to_float(i_data.angle_x)
        # gui_data_dict["roll"] = to_float(i_data.angle_y)
        # gui_data_dict["hdg"] = to_float(i_data.angle_z)
        # i_gui.update(gui_data_dict)

        # print(to_float(i_data.angle_x), "\t", to_float(i_data.angle_y), "\t", to_float(i_data.angle_z))   
        # print(i_cmd.eng_1, i_cmd.eng_2)

        time.sleep(0.02)

    # Exit
    print("Stopping modules...")
    i_joysticks.stop()
    i_gui.stop()
    i_communication.stop()
    print("Done!")

    print("Exiting...")
    exit()
