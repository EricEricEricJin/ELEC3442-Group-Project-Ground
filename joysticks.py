# Copyright Eric Jin 2024
# modified for SuperLink by Eric Jin in 2025

import pygame
import threading
import time

import platform

class Joysticks:
    SW_DOWN = -1
    SW_MID = 0
    SW_UP = 1

    BUTT_UP = 0
    BUTT_DOWN = 1

    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()

        self.throttle_raw_axes = []
        self.throttle_raw_buttons = []

    def identify(self)->bool:
        # assign joystick
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        self.joystick = None

        for js in joysticks:
            name = js.get_name()
            if "SL8" in name:
                self.joystick = js
                self.axes_num = js.get_numaxes()
                self.buttons_num = js.get_numbuttons()
                return True
        else:
            print("No SuperLink joystick detected.")
            return False
        

    def start(self)->None:
        self.t = threading.Thread(target=self._read_thread)
        self.running = True
        self.t.start()

    def stop(self)->None:
        self.running = False
        self.t.join()

    def _read_thread(self):
        while self.running:
            # quit if detect QUIT event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update sidestick interface
            self.raw_axes = [round(self.joystick.get_axis(i), 3) for i in range(self.axes_num)]
            self.raw_buttons = [self.joystick.get_button(i) for i in range(self.buttons_num)]

            self.clock.tick(100)
    
    
    def get_xyz(self):
        return self.raw_axes[0], self.raw_axes[1], self.raw_axes[3]
    
    def get_lever(self):
        return self.raw_axes[2]
    
    def get_sw_left(self): # (down, mid, up)
        sw_left_idx = 6
        if platform.system() == "Windows":
            sw_left_idx = 7
        if self.raw_axes[sw_left_idx] < -0.5:
            return self.SW_DOWN
        elif self.raw_axes[sw_left_idx] > 0.5:
            return self.SW_UP
        else:
            return self.SW_MID
        
    def get_sw_right(self):
        if self.raw_axes[4] < -0.5:
            return self.SW_DOWN
        elif self.raw_axes[4] > 0.5:
            return self.SW_UP
        else:
            return self.SW_MID
        
    def get_butt_mid(self):
        if (self.raw_buttons[1] == 1):
            return self.BUTT_DOWN
        else:
            return self.BUTT_UP

    def get_butt_left(self):
        if (self.raw_axes[5] >0):
            return self.BUTT_DOWN
        else:
            return self.BUTT_UP
    

if __name__ == "__main__":
    j = Joysticks()
    j.identify()
    j.start()
    try:
        for i in range(100):
            # print(j.get_th_thrust_1(), j.get_th_thrust_2())
            print(j.get_xyz())
            time.sleep(0.1)
    except:
        pass
    finally:
        j.stop()