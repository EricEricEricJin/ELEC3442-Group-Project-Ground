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

    def identify(self)->bool:
        # assign joystick
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        
        self.sidestick = joysticks[0]

        self.sidestick_axes_num = self.sidestick.get_numaxes()
        self.sidestick_buttons_num = self.sidestick.get_numbuttons()
        
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

            
            # update sidestick interface
            self.sidestick_raw_axes = [round(self.sidestick.get_axis(i), 3) for i in range(self.sidestick_axes_num)]
            self.sidestick_raw_buttons = [self.sidestick.get_button(i) for i in range(self.sidestick_buttons_num)]

            self.clock.tick(100)
    
    def get_ss_xy(self):
        return self.sidestick_raw_axes[0], self.sidestick_raw_axes[1]
    
    

if __name__ == "__main__":
    j = Joysticks()
    j.identify()
    j.start()
    try:
        for i in range(100):
            # print(j.get_th_thrust_1(), j.get_th_thrust_2())
            print(j.get_ss_xy())
            time.sleep(0.1)
    except:
        pass
    finally:
        j.stop()