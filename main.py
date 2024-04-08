import communication
import gui
import joysticks
import time

if __name__ == "__main__":
    print("Fixed Wing Plane Remote Control System")
    print("Copyright Eric Jin 2024")
    
    # print("Special thanks to Percy Liu and Dryden Zhou for cooperation in 2020-2021")
    # print("Thanks to Uky Fan for helping building the plane model")



    print("Initializing joysticks...")
    i_joysticks = joysticks.Joysticks()
    if (i_joysticks.identify()):
        print("Done!")
    else:
        print("Failed!")
        print("Exiting...")
        exit()


    print("Initializing communication...")
    IP, port = "127.0.0.1", 1234
    print("IP:", "Port:", port)
    i_data = communication.planeData()
    i_cmd = communication.groundCommand()
    i_communication = communication.Communication(IP, port, i_cmd, i_data)
    i_communication.start(0.04)
    print("Done!")


    print("Initializing GUI...")
    i_gui = gui.PFD()
    gui_data_dict = {
        "pitch": 0, "roll": 0, 
        "air_speed": 0, "gnd_speed": 0, "accel": 0,
        "psr_alt": 0, "tof_alt": 0,"vs": 0,
        "hdg": 0,
        "long": 0, "lat": 0,
        "FD_ON": True, 
        "tar_speed": 10, "tar_alt": -10, "tar_hdg": 0, "tar_long": 0, "tar_lat": 0,
        "sta" : {
            "CRUISE": True, "MANU": True, "FAC": True, "AP_HDG": True,
            "TO/LD": True, "AUTO": True, "MCAS": True, "AP_ALT": True,
            "AP_SPD": True
        }
    }
    i_gui.run()
    print("Done!")

    while True:
        gui_state = i_gui.get_state()
        if gui_state == 0:
            break
            
        # Update commands from joysticks to communication
        
        # control surface
        ss_x, ss_y, ss_z = i_joysticks.get_ss_xyz()
        i_cmd.aileron = ss_x
        i_cmd.elevator = ss_y
        i_cmd.rudder = ss_z

        # throttles
        th_t1, th_t2 = i_joysticks.get_th_thrust
        i_cmd.eng_1 = th_t1
        i_cmd.eng_2 = th_t2

        # Update data from communication to GUI
        gui_data_dict["pitch"] = i_data.angle_x
        gui_data_dict["roll"] = i_data.angle_y
        gui_data_dict["hdg"] = i_data.mag_z
        i_gui.update(gui_data_dict)

        time.sleep(0.01)

    # Exit
    print("Stopping modules...")
    i_joysticks.stop()
    i_gui.stop()
    i_communication.stop()
    print("Done!")

    print("Exiting...")
    exit()
