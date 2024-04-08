# Copyright Eric Jin 2024


import pygame
import threading
import time

# Capatible with Thrustmaster TCA Officer Pack Airbus Edition
# Joystick + throttle lever
class Joysticks:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()

        self.throttle_raw_axes = []
        self.throttle_raw_buttons = []

    def identify(self)->bool:
        # assign joystick
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        
        self.throttle = None
        self.sidestick = None

        for joystick in joysticks:
            name = joystick.get_name()
            if name == "TCA Q-Eng 1&2":
                self.throttle = joystick
                self.throttle_axes_num = joystick.get_numaxes()
                self.throttle_buttons_num = self.throttle.get_numbuttons()
            elif name == "T.A320 Pilot":
                self.sidestick = joystick
                self.sidestick_axes_num = joystick.get_numaxes()
                self.sidestick_buttons_num = joystick.get_numbuttons()
                self.sidestick_hats_num = joystick.get_numhats()

        if (not self.sidestick) or (not self.throttle):
            return False
        
        return True

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

            # update throttle interface
            self.throttle_raw_axes = [round(self.throttle.get_axis(i), 3) for i in range(self.throttle_axes_num)]
            self.throttle_raw_buttons = [self.throttle.get_button(i) for i in range(self.throttle_buttons_num)]
            
            # update sidestick interface
            self.sidestick_raw_axes = [round(self.sidestick.get_axis(i), 3) for i in range(self.sidestick_axes_num)]
            self.sidestick_raw_buttons = [self.sidestick.get_button(i) for i in range(self.sidestick_buttons_num)]
            self.sidestick_raw_hat = self.sidestick.get_hat(0)

            self.clock.tick(100)
    
    def get_th_thrust(self):
        return (1-self.throttle_raw_axes[0]) / 2, (1-self.throttle_raw_axes[1]) / 2
    def get_th_redbut(self):
        return self.throttle_raw_buttons[0], self.throttle_raw_buttons[1]
    def get_th_engon(self):
        return self.throttle_raw_buttons[2], self.throttle_raw_buttons[3]
    def get_th_blackbut(self):
        return self.throttle_raw_buttons[4], self.throttle_raw_buttons[5]
    def get_th_crank(self):
        return self.throttle_raw_buttons[6]
    def get_th_start(self):
        return self.throttle_raw_buttons[7]
    
    def get_ss_xyz(self):
        return self.sidestick_raw_axes[0], self.sidestick_raw_axes[1], self.sidestick_raw_axes[2]
    def get_ss_lever(self):
        return self.sidestick_raw_axes[3]
    def get_ss_trigger(self): # (down, up)
        return self.sidestick_raw_buttons[0], self.sidestick_raw_buttons[1]
    def get_ss_blackbut(self):
        return self.sidestick_raw_buttons[2]
    def get_ss_redbut(self):
        return self.sidestick_raw_buttons[3]
    def get_ss_leftkey(self):
        return self.sidestick[10], self.sidestick[11], self.sidestick[12], self.sidestick[15], self.sidestick[14], self.sidestick[13]
    def get_ss_rightkey(self):
        return self.sidestick[6], self.sidestick[5], self.sidestick[4], self.sidestick[7], self.sidestick[8], self.sidestick[9]
    def get_ss_hat(self):
        return self.sidestick_raw_hat


if __name__ == "__main__":
    j = Joysticks()
    j.identify()
    j.start()
    try:
        for i in range(100):
            # print(j.get_th_thrust_1(), j.get_th_thrust_2())
            print(j.get_ss_xyz())
            time.sleep(0.1)
    except:
        pass
    finally:
        j.stop()