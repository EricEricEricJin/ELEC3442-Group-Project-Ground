################################################################################
# Copyright Eric Jin 2020
# originally two files: pfd.py and ewd.py,
# now merged and modified in 2024 by Eric Jin
################################################################################

from tkinter import *
from socket import *
from struct import unpack
from threading import Thread
import math
from time import sleep

class updateTest:
    def __init__(self):
        self.data_list = {
            "pitch": 0, "roll": 0, 
            "air_speed": 0, "gnd_speed": 0, "accel": 0,
            "psr_alt": 0, "tof_alt": 0,"vs": 0, "temperature": 0,
            "hdg": 0,
            "FD_ON": True, 
            "tar_speed": 0, "tar_alt": 0, "tar_hdg": 0,
            "sta" : {
                "AIL MANUAL": True, "ELE MANUAL": True, "RUD MANUAL": True,
                "AIL STABLE": False, "ELE STABLE": False, "RUD STABLE": False,
                "AIL LCKATT": False, "ELE LCKATT": False, "RUD LCKATT": False,
            },
            "eng_1": True, "eng_2": True, "thrust_1": 12.3, "thrust_2": 23.4,
            "volt_main": 11.6, "volt_bus": 5.0, "cpu_tmp": 0
        }
        self.P = PFD()


    def run(self):
        t = Thread(target = self._service)
        t.start()
        self.P.run()

    def _service(self):
        while True:
            self.data_list["pitch"] -= 1
            self.data_list["roll"] += 1
            self.P.update(self.data_list)
            sleep(1)


class infoBox:
    def __init__(self, cvs, title, x0, y0, w, h, c, fontsize=12) -> None:
        self.cvs = cvs
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.title = title
        self.color = c

        # self.box = self.cvs.create_rectangle(x0, y0, x0 + w, y0 + h, outline=self.color)
        self.text_title = self.cvs.create_text(x0 + w / 2, y0, text=self.title, fill=self.color, font=("consolas", int(fontsize)))
        self.text_content = self.cvs.create_text(x0 + w / 2, y0 + h/2, text="", fill=self.color, font=("consolas", int(fontsize)))
        title_bounds = self.cvs.bbox(self.text_title)
        side_length = (self.w - (title_bounds[2] - title_bounds[0])) / 2
        self.box = self.cvs.create_line(x0 + side_length, y0,
                             x0, y0, 
                             x0, y0 + h,
                             x0 + w, y0 + h,
                             x0 + w, y0,
                             x0 + w - side_length, y0, fill=self.color, width=2)

    def set_content(self, txt):
        self.cvs.itemconfigure(self.text_content, text=txt, fill=self.color)

    def set_color(self, color):
        self.color = color
        self.cvs.itemconfigure(self.box, fill = self.color)
        self.cvs.itemconfigure(self.text_title, fill = self.color)
        self.cvs.itemconfigure(self.text_content, fill = self.color)


class arcDial:
    """ 
    Create arc dial chart with minimum = 0 and maximum = 100
    cvs:        the canvas object
    x0, y0:     position
    w:          width and height
    red_line:   if value is larger than red_line, will be displayed in red color
    """
    def __init__(self, cvs, x0, y0, w, red_line):
        # x0, y0: coordinate of center
        self.cvs = cvs

        self.w = w
        self.x0 = x0
        self.y0 = y0
        self.red_line = red_line
        self.arc_rad = self.w / 2 * 0.95

        div_line_len_index = 0.05
        self.cvs.create_arc(x0 + self.w / 2 - self.arc_rad, y0 + self.w / 2 - self.arc_rad, x0 + self.w / 2 + self.arc_rad,
                            y0 + self.w / 2 + self.arc_rad, outline="white", start=0, extent=225, style=ARC, width=2)

        if self.red_line <= 0:
            color = "red"
        else:
            color = "white"

        self.cvs.create_line(x0 + self.w / 2 - self.arc_rad / 1.4142, y0 + self.w / 2 + self.arc_rad / 1.4142, x0 + self.w / 2 -
                             self.arc_rad / 1.4142 + self.w * div_line_len_index, y0 + self.w / 2 + self.arc_rad / 1.4142 - self.w * 0.05, fill=color, width=2)
        self.cvs.create_text(x0 + self.w / 2 - self.arc_rad / 1.4142  + self.w * div_line_len_index * 2, y0 + self.w / 2 + self.arc_rad /
                             1.4142 - self.w * div_line_len_index * 2, text="0", fill=color, font=("consolas", int(self.w / 15)))

        if self.red_line <= 50:
            color = "red"
        else:
            color = "white"

        self.cvs.create_line(x0 + self.w / 2 - self.arc_rad / 1.4142, y0 + self.w / 2 - self.arc_rad / 1.4142, x0 + self.w / 2 - self.arc_rad / 1.4142 +
                             self.w * div_line_len_index, y0 + self.w / 2 - self.arc_rad / 1.4142 + self.w * div_line_len_index, fill=color, width=2)
        self.cvs.create_text(x0 + self.w / 2 - self.arc_rad / 1.4142 + self.w * div_line_len_index * 2, y0 + self.w / 2 - self.arc_rad /
                             1.4142 + self.w * div_line_len_index * 2, text="50", fill=color, font=("consolas", int(self.w / 15)))

        if self.red_line <= 100:
            color = "red"
        else:
            color = "white"

        self.cvs.create_line(x0 + self.w / 2 + self.arc_rad / 1.4142, y0 + self.w / 2 - self.arc_rad / 1.4142, x0 + self.w / 2 + self.arc_rad / 1.4142 -
                             self.w * div_line_len_index, y0 + self.w / 2 - self.arc_rad / 1.4142 + self.w * div_line_len_index, fill=color, width=2)
        self.cvs.create_text(x0 + self.w / 2 + self.arc_rad / 1.4142 - self.w * div_line_len_index * 2, y0 + self.w / 2 -
                             self.arc_rad / 1.4142 + self.w * div_line_len_index * 2, text="100", fill=color, font=("consolas", int(self.w / 15)))

        if self.red_line <= 125:
            self.cvs.create_arc(x0 + self.w / 2 - self.arc_rad, y0 + self.w / 2 - self.arc_rad, x0 + self.w / 2 + self.arc_rad, y0 + self.w / 2 +
                                self.arc_rad, outline="red", start=0, extent=(125 - red_line) / 125 * 225, style=ARC, width=2)

        self.text = self.cvs.create_text(
            x0 + self.w / 2, y0 + self.w * 0.75, text="---", fill="green", font=("consolas", int(self.w / 10)))
        self.line = self.cvs.create_line(x0 - 10, y0 - 
                                         10, x0 - 10, y0 - 10, fill="green", width=3)

    def set_val(self, val, on=True):
        """
        val: between 0 t0 125
        on: if set to False, will display "---" and will not display bar
        """
        if val < 0:
            val = 0
        elif val > 125:
            val = 125

        if val < self.red_line:
            color = "green"
        else:
            color = "red"

        if on:
            self.cvs.itemconfigure(self.text, text=str(round(val)), fill=color)
            angle = (125 - val) / 125 * 225
            self.cvs.coords(self.line, self.x0 + self.w / 2, self.y0 + self.w / 2, self.x0 + math.cos(
                math.radians(angle)) * self.w / 2 + self.w / 2, self.y0 + self.w / 2 - math.sin(math.radians(angle)) * self.w / 2)
        else:
            self.cvs.itemconfigure(self.text, text="---", fill="green")
            self.cvs.coords(self.line, self.x0 - 10, self.y0 - 10, self.x0 - 10, self.y0 - 10)




class scaleChart:
    """
    Create a scale chart
    cvs: the master canvas object
    x0, y0: position of left-up conner
    w, h: width and height
    c: color
    title: title text
    vmax, vmin: maximum and minimum value
    dir: direction of the bar, "V" vertical or "H" horizontal
    """
    def __init__(self, cvs, x0, y0, w, h, c, title, vmax, vmin, dir="V", fontsize = 12):
        self.cvs = cvs
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.length = w if dir == 'H' else h
        self.dir = dir
        self.title = title
        self.color = c
        self.vmax, self.vmin = vmax, vmin

        if self.dir == "H":
            title_xy = x0 + w / 2, y0 + fontsize
            value_xy = x0 + w / 2, y0 + h - fontsize
            box_bb = x0, y0 + 0.45 * h, x0 + w, y0 + 0.55 * h
        elif self.dir == "V":
            title_xy = x0 + w / 4, y0 + h / 4
            value_xy = x0 + w / 4, y0 + h / 4 * 3
            box_bb = x0 + w / 2 + w / 2 * 0.4, y0, x0 + w / 2 + w / 2 * 0.6, y0 + h

        self.text_title = self.cvs.create_text(*title_xy, text=self.title, fill=self.color, font=("consolas", int(fontsize)))
        self.text_value = self.cvs.create_text(*value_xy, text="", fill=self.color, font=("consolas", int(fontsize)))
        self.box = self.cvs.create_rectangle(*box_bb, outline=self.color)
        self.bar = None

    def set_val(self, value):
        """
        value: between vmin and vmax
        """
        self.cvs.itemconfigure(self.text_value, text=round(value, 1))

        if self.dir == "V":
            bar_x0y0x1y1 = self.x0 + self.w / 2 + self.w / 2 * 0.35,                 \
                           self.y0 + self.h - (value-self.vmin)/(self.vmax-self.vmin)*self.h, \
                           self.x0 + self.w / 2 + self.w / 2 * 0.65,                 \
                           self.y0 + self.h - (value-self.vmin)/(self.vmax-self.vmin)*self.h
        elif self.dir == "H":
            bar_x0y0x1y1 = self.x0 + (value-self.vmin)/(self.vmax-self.vmin)*self.w, \
                            self.y0 + 0.35 * self.h,                                  \
                            self.x0 + (value-self.vmin)/(self.vmax-self.vmin)*self.w, \
                            self.y0 + 0.65 * self.h
        if self.bar:
            self.cvs.coords(self.bar, *bar_x0y0x1y1)
        else:
            self.bar = self.cvs.create_line(*bar_x0y0x1y1, fill=self.color)
                
"""
Abbr:
STA:    status
ATT:    attitude
ALT:    altitude
VS:     vertical speed
HDG:    heading
"""

class PFD:
    WIN_H = int(900)
    WIN_W = int(1200)

    STA_IND_H = int(WIN_H / 16)
    STA_IND_W = WIN_W / 2
    STA_IND_X = 0
    STA_IND_Y = 0
    
    SPEED_H = int(WIN_H / 2 - STA_IND_H)
    SPEED_W = WIN_W / 2 * 0.15
    SPEED_X = 0
    SPEED_Y = STA_IND_H

    ATT_A = WIN_W / 2 * 0.6
    ATT_X, ATT_Y = WIN_W/2 * 0.15, SPEED_Y

    ALT_H = SPEED_H
    ALT_W = SPEED_W
    ALT_X = WIN_W/2 * 0.75
    ALT_Y = SPEED_Y

    VS_H = SPEED_H
    VS_W = WIN_W/2 * 0.1
    VS_X = WIN_W/2 * 0.9
    VS_Y = SPEED_Y

    HDG_A = WIN_W / 2 * 0.75
    HDG_X = 0
    HDG_Y = WIN_H - HDG_A

    # mechanical display
    MD_W = WIN_W / 2
    MD_H = WIN_H / 4
    MD_X, MD_Y = WIN_W / 2, 0

    # Engine monitor display
    EWD_W = WIN_W / 2
    EWD_H = WIN_H / 2
    EWD_X, EWD_Y = WIN_W/2, WIN_H / 4

    # Entry field
    ETFD_X, ETFD_Y = WIN_W / 2, WIN_H / 4 * 3

    def __init__(self):
        self.data_list = {
            "pitch": 0, "roll": 0, 
            "air_speed": 0, "gnd_speed": 0, "accel": 0,
            "psr_alt": 0, "tof_alt": 0,"vs": 0, "temperature": 0,
            "hdg": 0,
            "FD_ON": True, 
            "tar_speed": 0, "tar_alt": 0, "tar_hdg": 0,
            "sta" : {
                "AIL MANUAL": False, "ELE MANUAL": False, "RUD MANUAL": False,
                "AIL STABLE": False, "ELE STABLE": False, "RUD STABLE": False,
                "AIL LCKATT": False, "ELE LCKATT": False, "RUD LCKATT": False,
            },
            "eng_1": False, "eng_2": False, "thrust_1": 0, "thrust_2": 0,
            "volt_main": 0.0, "volt_bus": 0.0, "cpu_tmp": 0,
            "elevator": 0, "aileron_l": 0, "aileron_r": 0, "rudder": 0
        }
        
        # self.COM = Communicate()
        # self.COM.send(b"pfd")

        self.root = Tk()
        self.root.geometry(str(self.WIN_W) + "x" + str(self.WIN_H))
        self.root.configure(bg = "black")
        # self.root.overrideredirect(True)

        self.sta_ind_cvs = Canvas(master = self.root, height = self.STA_IND_H, width = self.STA_IND_W, bg = "black", highlightthickness = 0)
        self.sta_ind_cvs.place(x = self.STA_IND_X, y = self.STA_IND_Y)
        
        self.speed_cvs = Canvas(master = self.root, height = self.SPEED_H, width = self.SPEED_W, bg = "black", highlightthickness = 0)
        self.speed_cvs.place(x = self.SPEED_X, y = self.SPEED_Y)

        self.att_cvs = Canvas(master = self.root, height = self.ATT_A, width = self.ATT_A, bg = "black", highlightthickness = 0)
        self.att_cvs.place(x = self.ATT_X, y = self.ATT_Y)

        self.alt_cvs = Canvas(master = self.root, height = self.ALT_H, width = self.ALT_W, bg = "black", highlightthickness = 0)
        self.alt_cvs.place(x = self.ALT_X, y = self.ALT_Y)

        self.vs_cvs = Canvas(master = self.root, height = self.VS_H, width = self.VS_W, bg = "black", highlightthickness = 0)
        self.vs_cvs.place(x = self.VS_X, y = self.VS_Y)

        self.hdg_cvs = Canvas(master = self.root, height = self.HDG_A, width = self.HDG_A, bg = "black", highlightthickness = 0)
        self.hdg_cvs.place(x = self.HDG_X, y = self.HDG_Y)
        # NOTE: buyao yongman h
        # ??? WTF is the comment 

        self.ewd_cvs = Canvas(master = self.root, height = self.EWD_H, width = self.EWD_W, bg= "black", highlightthickness = 0)
        self.ewd_cvs.place(x = self.EWD_X, y = self.EWD_Y)

        self.md_cvs = Canvas(master = self.root, height = self.MD_H, width = self.MD_W, bg= "black", highlightthickness = 0)
        self.md_cvs.place(x = self.MD_X, y = self.MD_Y)

        self._init_sta_ind()
        self._init_speed()
        self._init_att()
        self._init_alt()
        self._init_vs()
        self._init_hdg()
        self._init_ewd()
        self._init_md()
        self._init_entryfield()

    def _init_sta_ind(self):
        for i in range(3):
            coord = (
                self.STA_IND_W / 4 * (i + 1), 0, 
                self.STA_IND_W / 4 * (i + 1), self.STA_IND_H / 5 * 4
            )
            self.sta_ind_cvs.create_line(coord, fill = "white")

        self.sta_ind_disp_text = [
            ["AIL MANUAL", "ELE MANUAL", "RUD MANUAL"],
            ["AIL STABLE", "ELE STABLE", "RUD STABLE"],
            ["AIL LCKATT", "ELE LCKATT", "RUD LCKATT"],
        ]

        self.sta_ind_disp_mat = []

        for i in range(len(self.sta_ind_disp_text)):
            self.sta_ind_disp_mat.append([])
            for j in range(len(self.sta_ind_disp_text[0])):
                coord = ((1 + 2 * j) / 8 * self.STA_IND_W, (1 + 2 * i) / 8 * self.STA_IND_H)
                self.sta_ind_disp_mat[i].append(self.sta_ind_cvs.create_text(coord, text = self.sta_ind_disp_text[i][j], fill = "black"))

    def _init_speed(self):
        self.speed_lines = []
        self.speed_texts = []

        self.speed_cvs.create_rectangle(1 / 4 * self.SPEED_W, 0, 3 / 4 * self.SPEED_W, self.SPEED_H, fill = "grey")

        for i in range(16):
            self.speed_lines.append(self.speed_cvs.create_line(-114, -114, -114, -114, fill = "white"))
            self.speed_texts.append(self.speed_cvs.create_text(-114, -114, text = "0", fill = "white"))
        
        self.speed_cvs.create_polygon((1 / 8 * self.SPEED_W, 9 / 20 * self.SPEED_H, 5 / 8 * self.SPEED_W, 9 / 20 * self.SPEED_H, 3 / 4 * self.SPEED_W, 1 / 2 * self.SPEED_H, 5 / 8 * self.SPEED_W, 11 / 20 * self.SPEED_H, 1 / 8 * self.SPEED_W, 11 / 20 * self.SPEED_H), fill = "#202020")
        self.speed_val_text = self.speed_cvs.create_text(3 / 8 * self.SPEED_W, 1 / 2 * self.SPEED_H, text = "", fill = "white")

        self.accel_indi = self.speed_cvs.create_rectangle(3 / 4 * self.SPEED_W, 1 / 2 * self.SPEED_H, 4 / 5 * self.SPEED_W, 1 / 2 * self.SPEED_H, fill = "white")
        self.speed_fd = self.speed_cvs.create_polygon(-114, -114, -114, -114, outline = "pink")

    def _init_att(self):        
        self.blue_poly = self.att_cvs.create_rectangle((0, 0, self.ATT_A, self.ATT_A), fill = "blue", width = 0)
        self.brown_poly = self.att_cvs.create_polygon((-114, -114, -114, -114), fill = "red")

        self.att_lines = []
        self.att_texts = []

        for i in range(25):
            self.att_lines.append(self.att_cvs.create_line(-114, -114, -114, -114, fill = "white"))

        for i in range(13):
            self.att_texts.append(self.att_cvs.create_text(-114, -114, text = str(abs(60 - 10 * i)) ))
            self.att_texts.append(self.att_cvs.create_text(-114, -114, text = str(abs(60 - 10 * i)) ))

        self.att_cvs.create_line(3 / 10 * self.ATT_A, 1 / 2 * self.ATT_A, 9 / 20 * self.ATT_A, 1 / 2 * self.ATT_A, width = 5, fill = "black")
        self.att_cvs.create_line(11 / 20 * self.ATT_A, 1 / 2 * self.ATT_A, 7 / 10 * self.ATT_A, 1 / 2 * self.ATT_A, width = 5, fill = "black")
        self.att_cvs.create_rectangle(49 / 100 * self.ATT_A, 49 / 100 * self.ATT_A, 51 / 100 * self.ATT_A, 51 / 100 * self.ATT_A, fill = "black")

    def _init_alt(self):
        self.alt_lines = []
        self.alt_texts = []

        self.alt_cvs.create_rectangle(1 / 4 * self.ALT_W, 0, 3 / 4 * self.ALT_W, self.ALT_H, fill = "grey")

        for i in range(16):
            self.alt_lines.append(self.alt_cvs.create_line(-114, -114, -114, -114, fill = "white"))
            self.alt_texts.append(self.alt_cvs.create_text(-114, -114, text = "0", fill = "white"))

        self.alt_cvs.create_polygon((1 / 4 * self.ALT_W, 1 / 2 * self.ALT_H, 3 / 8 * self.ALT_W, 11 / 20 * self.ALT_H, 7 / 8 * self.ALT_W, 11 / 20 * self.ALT_H, 7 / 8 * self.ALT_W, 9 / 20 * self.ALT_H, 3 / 8 * self.ALT_W, 9 / 20 * self.ALT_H), fill = "#202020")
        self.alt_val_text = self.alt_cvs.create_text(5 / 8 * self.ALT_W, 1 / 2 * self.ALT_H, text = "", fill = "white")

        self.alt_fd = self.alt_cvs.create_polygon(-114, -114, -114, -114, outline = "pink")

    def _init_vs(self):
        self.vs_cvs.create_polygon((1 / 4 * self.VS_W, 0, 1 / 4 * self.VS_W, self.VS_H, 3 / 4 * self.VS_W, 39 / 40 * self.VS_H, 3 / 4 * self.VS_W, 1 / 40 * self.VS_H), fill = "grey")
        # (40, 200-780tan(0.04083v)) # Fuck magic numbers
        for i in range(-5, 6):
            # self.vs_cvs.create_text(40, 200-780 * math.tan(0.04083 * i), text = str(abs(i)), fill = "white")
            l_cd = self._vs_line_coord(i * 100)
            self.vs_cvs.create_text((l_cd[0] + l_cd[2]) / 2, (l_cd[1] + l_cd[3]) / 2, text = str(abs(i)))
        self.vs_line = self.vs_cvs.create_line(-114, -114, -114, -114, width = self.VS_H / 100)

    def _init_hdg(self):

        self.hdg_real_dis_betw_circ = 100 # ft
        self.hdg_delta_r_of_circ = self.HDG_A / 10

        # Plane sign
        self.hdg_cvs.create_polygon(
            self._hdg_planesign_coord(self.HDG_A / 2, self.HDG_A / 2, self.HDG_A / 100),
            outline = "white"
        )

        # Heading ray
        self.hdg_cvs.create_line(
            self.HDG_A / 2, self.HDG_A / 2 - 4 * self.hdg_delta_r_of_circ, 
            self.HDG_A / 2, self.HDG_A / 2 - self.HDG_A / 200,
            fill = "white"
        )

        # radar panel
        for i in range(1, 5):
            self.hdg_cvs.create_arc(self.HDG_A / 2 - i * self.hdg_delta_r_of_circ, self.HDG_A / 2 - i * self.hdg_delta_r_of_circ, self.HDG_A / 2 + i * self.hdg_delta_r_of_circ, self.HDG_A / 2 + i * self.hdg_delta_r_of_circ, start = 270, extent = 359, outline = "white", style = ARC)
            if i < 4:
                self.hdg_cvs.create_text(self.HDG_A / 2 - i * self.hdg_delta_r_of_circ - 10, self.HDG_A / 2, text = str(i), fill = "white")

        self.hdg_line_num = 72
        self.hdg_line_list = []
        self.hdg_text_list = []

        # lines KEDU
        for i in range(self.hdg_line_num):
            self.hdg_line_list.append(self.hdg_cvs.create_line(-114, -114, -114, -114, fill = "white"))
            if i % 2 == 0:
                self.hdg_text_list.append(self.hdg_cvs.create_text(-114, -114, text = str(int(i * 360 / self.hdg_line_num)), fill = "white"))

        self.hdg_cvs.create_polygon(
            self._hdg_numbox_coord(self.HDG_A / 2, self.HDG_A / 2 - 4 * self.hdg_delta_r_of_circ, self.HDG_A / 16),
            outline = "white"
        )

        self.hdg_val_text = self.hdg_cvs.create_text(self.HDG_A / 2, self.HDG_A / 2 - 4 * self.hdg_delta_r_of_circ - self.HDG_A / 32, text = "", fill = "white")

        # self.hdg_fd = 
    
    def _init_ewd(self):
        # engine and warning display
        block_w = 200
        self.eng_ind_1 = arcDial(self.ewd_cvs, self.EWD_W / 2 - block_w, (self.EWD_H - block_w) / 2, block_w, 100)
        self.eng_ind_2 = arcDial(self.ewd_cvs, self.EWD_W / 2, (self.EWD_H - block_w) / 2, block_w, 100)
        
        # voltage display
        self.vbat_disp = infoBox(self.ewd_cvs, "MAIN BAT", 10, self.EWD_H - 70, 100, 60, 'green')
        self.vbat_disp.set_content("---")
        self.vbus_disp = infoBox(self.ewd_cvs, "BUS VOLT", 130, self.EWD_H - 70, 100, 60, "green")
        self.vbat_disp.set_content("---")

        # temperature
        self.exttmp_disp = infoBox(self.ewd_cvs, "EXT TEMP", 250, self.EWD_H - 70, 100, 60, "green")
        self.exttmp_disp.set_content("---")

        self.cputmp_disp = infoBox(self.ewd_cvs, "CPU TEMP", 370, self.EWD_H - 70, 100, 60, "green")
        self.cputmp_disp.set_content("---")


    def _init_md(self): # mechanical display
        self.elevator_disp = scaleChart(self.md_cvs, 200, 100, 100, 100, "blue", "ELEVATOR", 1, -1, dir="V")
        self.elevator_disp.set_val(0)

        self.aileron_l_disp = scaleChart(self.md_cvs, 80, 100, 100, 100, "blue", "AILERON L", 1, -1, dir="V")
        self.aileron_l_disp.set_val(0)

        self.aileron_r_disp = scaleChart(self.md_cvs, 320, 100, 100, 100, "blue", "AILERON R", 1, -1, dir="V")
        self.aileron_r_disp.set_val(0)

        self.rudder_disp = scaleChart(self.md_cvs, 440, 100, 100, 100, "blue", "RUDDER", 1, -1, dir="H")
        self.rudder_disp.set_val(0)

    def _init_entryfield(self):
        qnh_label = Label(text="QNH")
        qnh_label.place(x=self.ETFD_X + 10, y=self.ETFD_Y + 10, width=60)
        qnh_label.config(bg="black", fg="green")
        self.qnh_entry = Spinbox(from_=990, to=1100, increment=0.1)
        self.qnh_entry.place(x = self.ETFD_X + 80, y = self.ETFD_Y + 10, width=60)
        self.qnh_entry.config(bg="black", fg="green")

    def run(self):
        # t = Thread(target = self._service)
        # t.start()
        self.root.after(50, self._service)
        self.root.mainloop()

    def update(self, data_list):
        self.data_list = data_list

    def stop(self):
        pass
    
    def get_state(self):
        return True
    
    def get_qnh(self):
        try:
            return float(self.qnh_entry.get())
        except:
            return 0

    def _service(self):
        try:
            self._update_sta_ind(self.data_list["sta"])
            self._update_speed(self.data_list["air_speed"], self.data_list["accel"], self.data_list["FD_ON"], self.data_list["tar_speed"])
            self._update_att(self.data_list["pitch"], self.data_list["roll"])
            self._update_alt(self.data_list["psr_alt"], self.data_list["FD_ON"], self.data_list["tar_alt"])
            self._update_vs(self.data_list["vs"])
            self._update_hdg(self.data_list["hdg"])
            self._update_ewd(self.data_list["eng_1"], self.data_list["thrust_1"], 0, 
                             self.data_list["eng_2"], self.data_list["thrust_2"], 0,
                             self.data_list["volt_main"], self.data_list["volt_bus"], 
                             self.data_list["temperature"], self.data_list["cpu_tmp"])
            self._update_md(self.data_list["elevator"], self.data_list["aileron_l"], self.data_list["aileron_r"], self.data_list["rudder"])
            
            self.root.after(100, self._service)

        except Exception as e:
            print(e)
            pass

    def _update_sta_ind(self, sta_dict):
        # print(sta_dict)
        for i in range(len(self.sta_ind_disp_mat)):
            for j in range(len(self.sta_ind_disp_mat[i])):
                if self.sta_ind_disp_text[i][j] != "":
                    color = "green" if sta_dict[self.sta_ind_disp_text[i][j]] else "black"
                    self.sta_ind_cvs.itemconfigure(self.sta_ind_disp_mat[i][j], fill = color)

    def _update_speed(self, speed, accel, fd_on, tar_speed):
        self.speed_cvs.itemconfigure(self.speed_val_text, text = str(speed))

        for i in range(16):
            if i % 2:
                is_short = (speed % 10 < 5)
            else:
                is_short = not(speed % 10 < 5)
            self.speed_cvs.coords(self.speed_lines[i], self._rollbar_line_coord(self.SPEED_W / 2, self.SPEED_H, self.SPEED_H / 16, 1 / 4 * self.SPEED_W - 1 / 8 * self.SPEED_W * is_short, 1 / 4 * self.SPEED_W, 0, i - 8, 5, speed))
            if is_short == 0:
                self.speed_cvs.coords(self.speed_texts[int(i / 2)], (3 / 8 * self.SPEED_W, self._rollbar_line_coord(1 / 2 * self.SPEED_W, self.SPEED_H, 1 / 16 * self.SPEED_H, 1 / 4 * self.SPEED_W, 1 / 4 * self.SPEED_W, 0, i - 8, 5, speed)[1]))
                self.speed_cvs.itemconfigure(self.speed_texts[int(i / 2)], text = str(self._rollbar_num_val(speed, 5, i - 8)))
        
        self.speed_cvs.coords(self.accel_indi, (3 / 4 * self.SPEED_W, 1 / 2 * self.SPEED_H, 4 / 5 * self.SPEED_W, 1 / 2 * self.SPEED_H - accel * (self.SPEED_H / 40)))

        if fd_on:
            self.speed_cvs.coords(
                self.speed_fd, self._rollbar_fd_coord(
                    (3 / 4 * self.SPEED_W, self.SPEED_H / 2 - (tar_speed - speed) * self.SPEED_H / 80),
                    self.SPEED_W / 10
                )
            )
        else:
            self.speed_cvs.coords(self.speed_fd, (-114, -114, -114, -114))

    def _update_att(self, pitch, roll):
        long_center_line_coord = self._att_line_coord(self.ATT_A, roll, pitch, 2 * 1.42 * 13 / 8 * self.ATT_A, 1 / 8 * self.ATT_A, 0, 5)
        # print("LCLC: ", long_center_line_coord)

        if 45 < roll <= 135:
            # left
            brown_coord = (
                long_center_line_coord[0], long_center_line_coord[1], 
                long_center_line_coord[2], long_center_line_coord[3],
                0, self.ATT_A,
                0, 0
            )
            
        elif 135 < roll <= 180 or -180 < roll <= -135:
            # up
            brown_coord = (
                long_center_line_coord[0], long_center_line_coord[1], 
                long_center_line_coord[2], long_center_line_coord[3],
                0, 0,
                self.ATT_A, 0
            )
            pass
        elif -135 < roll <= -45:
            # right
            brown_coord = (
                long_center_line_coord[0], long_center_line_coord[1], 
                long_center_line_coord[2], long_center_line_coord[3],
                self.ATT_A, 0,
                self.ATT_A, self.ATT_A
            )

            pass
        elif -45 < roll <= 45:
            # down
            brown_coord = (
                long_center_line_coord[0], long_center_line_coord[1], 
                long_center_line_coord[2], long_center_line_coord[3],
                self.ATT_A, self.ATT_A,
                0, self.ATT_A
            )

        self.att_cvs.coords(self.brown_poly, (brown_coord))

        for i in range(25):
            coord = self._att_line_coord(self.ATT_A, roll, pitch, 3 / 8 * self.ATT_A - (i % 2) * 1 / 8 * self.ATT_A, 1 / 8 * self.ATT_A, i - 12, 5)
            self.att_cvs.coords(self.att_lines[i], 
                coord
            )
            if i % 2 == 0:
                self.att_cvs.coords(self.att_texts[i], (coord[0] - math.cos(math.radians(roll)) * 1 / 40 * self.ATT_A, coord[1] - math.sin(math.radians(roll)) * 1 / 40 * self.ATT_A))
                self.att_cvs.coords(self.att_texts[i + 1], (coord[2] + math.cos(math.radians(roll)) * 1 / 40 * self.ATT_A, coord[3] + math.sin(math.radians(roll)) * 1 / 40 * self.ATT_A))
        
        for i in range(26):
            self.att_cvs.itemconfigure(self.att_texts[i], angle = -roll)

    def _update_alt(self, alt, fd_on, tar_alt):
        self.alt_cvs.itemconfigure(self.alt_val_text, text = str(round(alt)))

        for i in range(16):
            if i % 2:
                is_short = alt % 10 < 5
            else:
                is_short = not(alt % 10 < 5)

            self.alt_cvs.coords(self.alt_lines[i], self._rollbar_line_coord(self.ALT_W / 2, self.ALT_H, 1 / 16 * self.ALT_H, 1 / 4 * self.ALT_W - 1 / 8 * self.ALT_W * is_short, 1 / 4 * self.ALT_W, 0, i - 8, 5, alt, side = "l"))
            
            if is_short == 0:
                
                self.alt_cvs.coords(self.alt_texts[int(i / 2)], (5 / 8 * self.ALT_W, self._rollbar_line_coord(self.ALT_W / 2, self.ALT_H, 1 / 16 * self.ALT_H, 1 / 4 * self.ALT_W, 1 / 4 * self.ALT_W, 0, i - 8, 5, alt, side = "l")[1]))
                self.alt_cvs.itemconfigure(self.alt_texts[int(i / 2)], text = str(self._rollbar_num_val(alt, 5, i - 8)))
            
        if fd_on:
            self.alt_cvs.coords(
                self.alt_fd, 
                self._rollbar_fd_coord(
                    (1 / 4 * self.ALT_W, self.ALT_H / 2 - (tar_alt - alt) * self.ALT_H / 80),
                    self.ALT_W / 10
                )
            )
        else:
            self.alt_cvs.coords(self.alt_fd, (-114, -114, -114, -114))
        
    def _update_vs(self, vs):
        self.vs_cvs.coords(self.vs_line, self._vs_line_coord(vs))
        if abs(vs) <= 300:
            color = "green"
        elif 300 < abs(vs) <= 600:
            color = "yellow"
        elif abs(vs) > 600:
            color = "red"
        self.vs_cvs.itemconfigure(self.vs_line, fill = color)

    def _update_hdg(self, hdg):
        for i in range(self.hdg_line_num):
            if i % 2:
                # short
                coord = self._hdg_line_coord(4 * self.hdg_delta_r_of_circ, 3.8 * self.hdg_delta_r_of_circ, 360 / self.hdg_line_num, self.HDG_A / 2, self.HDG_A / 2, i, hdg)
            else:
                # long
                coord = self._hdg_line_coord(4 * self.hdg_delta_r_of_circ, 3.6 * self.hdg_delta_r_of_circ, 360 / self.hdg_line_num, self.HDG_A / 2, self.HDG_A / 2, i, hdg)
                
                coord_t = self._hdg_line_coord(4.2 * self.hdg_delta_r_of_circ, 4 * self.hdg_delta_r_of_circ, 360 / self.hdg_line_num, self.HDG_A / 2, self.HDG_A / 2, i, hdg)[0:2]
                self.hdg_cvs.coords(
                    self.hdg_text_list[int(i / 2)],
                    coord_t
                )
                self.hdg_cvs.itemconfigure(
                    self.hdg_text_list[int(i / 2)],
                    angle = hdg - i * 360 / self.hdg_line_num
                )

            self.hdg_cvs.coords(
                self.hdg_line_list[i],
                coord
            )
        
        self.hdg_cvs.itemconfigure(self.hdg_val_text, text = str(round(hdg % 360)))
            

    def _update_ewd(self, eng1, thrust1, i1, eng2, thrust2, i2, vbat, vbus, exttmp, cputmp):
        self.eng_ind_1.set_val(thrust1, eng1)
        self.eng_ind_2.set_val(thrust2, eng2)
        self.vbat_disp.set_content(str(round(vbat, 2)))
        self.vbus_disp.set_content(str(round(vbus, 2)))
        self.exttmp_disp.set_content(str(round(exttmp, 2)))
        self.cputmp_disp.set_content(str(round(cputmp, 2)))
    
    def _update_md(self, elevator, aileron_l, aileron_r, rudder):
        self.elevator_disp.set_val(elevator)
        self.aileron_l_disp.set_val(aileron_l)
        self.aileron_r_disp.set_val(aileron_r)
        self.rudder_disp.set_val(rudder)

    def _att_line_coord(self, a, r, p, l, d, n, u):
        """
            a: length of square
            r: roll in deg
            p: pitch in deg
            l: line length
            d: distance between lines
            n: n th line

            RETURN:
                (X0, Y0, X1, Y1)
        """

        """
            TODO: Deal with 90 deg
        """
        return (
            a / 2 - math.cos(math.radians(r)) * l / 2 - math.sin(math.radians(r)) * d * n  - math.sin(math.radians(r)) * p / u * d,
            p / u * d * math.cos(math.radians(r)) + n * math.cos(math.radians(r)) * d - math.sin(math.radians(r)) * l / 2 + 1 / 2 * a,
            a / 2 + math.cos(math.radians(r)) * l / 2 - math.sin(math.radians(r)) * d * n  - math.sin(math.radians(r)) * p / u * d,
            p / u * d * math.cos(math.radians(r)) + n * math.cos(math.radians(r)) * d + math.sin(math.radians(r)) * l / 2 + 1 / 2 * a

        )
    
    def _rollbar_line_coord(self, w, h, d, l, dx, dy, n, u, v, side = "r"):
        """
            w: width
            h: height
            d: dis between lines
            l: len of line
            n: nth line
            v: value
            u: each line sperate's value MEIYIGE JIANGE DAIBIAODE ZHI
        """

        if side == "r":
            return (
                w - l + dx,
                ((v % u) / u + n) * d + 0.5 * h + dy,
                w - 1 + dx,
                ((v % u) / u + n) * d + 0.5 * h + dy
            )
        else:
            return (
                dx,
                ((v % u) / u + n) * d + 0.5 * h + dy,
                l + dx,
                ((v % u) / u + n) * d + 0.5 * h + dy
            )

    def _rollbar_fd_coord(self, o, a):
        """
            o: (x, y) or origin point
            a: side length
        """
        return (
            o[0] - a / 2, o[1] - a / 2,
            o[0] + a / 2, o[1] - a / 2,
            o[0] + a / 2, o[1] - 3 / 10 * a,
            o[0] + a / 4, o[1] - 1 / 10 * a,
            o[0] + a / 4, o[1] + 1 / 10 * a,
            o[0] + a / 2, o[1] + 3 / 10 * a,
            o[0] + a / 2, o[1] + a / 2,
            o[0] - a / 2, o[1] + a / 2,
            o[0] - a / 2, o[1] + 3 / 10 * a,
            o[0] - a / 4, o[1] + 1 / 10 * a,
            o[0] - a / 4, o[1] - 1 / 10 * a,
            o[0] - a / 2, o[1] - 3 / 10 * a
        )

    def _rollbar_num_val(self, v, u, n):
        return v - (v % u) - n * u
        
    def _vs_line_coord(self, v):
        if v > 600:
            v = 600
        elif v < -600:
            v = -600
        
        return (
            1 / 4 * self.VS_W, 1 / 2 * self.VS_H - 10 * self.VS_W * math.tan(v / 600 * math.atan(self.VS_H / (20 * self.VS_W))),
            3 / 4 * self.VS_W, 1 / 2 * self.VS_H - 19 / 2 * self.VS_W * math.tan(v / 600 * math.atan(self.VS_H / (20 * self.VS_W)))
        )
        
        """
            return (
                20, 200 - 800 * math.tan(0.0004083 * v),
                60, 200 - 760 * math.tan(0.0004083 * v)
            )
            # Fucking magic numbers when 80x400
        """

    def _hdg_line_coord(self, R, r, d, xo, yo, n, v):
        """
            R: Big circle radi
            r: Samll circle radi
            d: deg between two line
            xo: center x
            yo: center y
            n: nth line
            v: value(deg)
        """

        theta = n * d - v
        
        return (
            xo + math.sin(math.radians(theta)) * R, yo - math.cos(math.radians(theta)) * R,
            xo + math.sin(math.radians(theta)) * r, yo - math.cos(math.radians(theta)) * r
        )

    def _hdg_num_val(self, v, d, n):
        """
            v: hdg in deg
            d: deg diff between lines
            n: nth number
        """

        return n * d

    def _hdg_planesign_coord(self, xo, yo, a):
        return (
            xo, yo - a,
            xo + a / 2, yo - a / 4,
            xo + a / 2, yo + a,
            xo - a / 2, yo + a,
            xo - a / 2, yo - a / 4,
        )

    def _hdg_numbox_coord(self, x, y, a):
        return (
            x, y,
            x + a / 2, y - a / 4,
            x + a / 2, y - a / 3 * 2,
            x - a / 2, y - a / 3 * 2,
            x - a / 2, y - a / 4
        )

    def _hdg_fd_coord(self, xo, yo, r, deg):
        # 
        pass
    
if __name__ == "__main__":
    UT = updateTest()
    UT.run()

