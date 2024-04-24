import tkinter as tk
import keyboard

import shared


DEFAULT_FONT = "Raleway"
PASS_DOT = chr(0x2022)


LOCKED_COLOR = "#ff584d"


class MainMenuBar(tk.Menu):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # File menu
        self.file_menu = tk.Menu(self)
        self.file_menu.add_command(label="Change Password", command=lambda: print("HIHIIHA"))
        self.add_cascade(label="File", menu=self.file_menu)


class PadlockIcon(tk.Canvas):
    def __init__(self, root, width=300, height=300, **kwargs):
        super().__init__(root, width=width, height=height, **kwargs)

        self.size = self.w, self.h = width, height
        self.color = LOCKED_COLOR
        self.angle = 180

        self.draw()

    def draw(self):
        # Black background (for testing)
        # self.create_rectangle(0, 0, *self.size, fill="black")

        w, h = self.size
        mid = h * 0.42

        rrr = self.h // 8
        rrd = rrr * 2

        rao = w * 0.38
        rai = w * 0.22

        self.create_arc(w / 2 - rao, mid - rao, w / 2 + rao, mid + rao,
                        start=0, extent=self.angle, fill=self.color, outline="")

        self.create_arc(w / 2 - rai, mid - rai, w / 2 + rai, mid + rai,
                        start=0, extent=self.angle, fill=self["background"],outline="")


        self.create_oval(0, mid, rrd, mid + rrd, fill=self.color, outline="")
        self.create_oval(0, h, rrd, h - rrd, fill=self.color, outline="")
        self.create_oval(w, mid, w - rrd, mid + rrd, fill=self.color, outline="")
        self.create_oval(w, h, w - rrd, h - rrd, fill=self.color, outline="")

        self.create_rectangle(0, mid + rrr, w, h - rrr, fill=self.color, outline="")
        self.create_rectangle(rrr, mid, w - rrr, h, fill=self.color, outline="")



class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Attributes
        self.input_password = ""
        self.pass_label_cursor = True

        # Initialize GUI
        self.title("Protecc")
        self.bind("<Key>", self.key_press)

        self.title_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=(DEFAULT_FONT, 48))
        self.title_label.pack(padx=10, pady=20)

        self.padlock_icon = PadlockIcon(self)
        self.padlock_icon.pack(pady=30)

        self.pass_label = tk.Label(self, text="|", font=(DEFAULT_FONT, 24))
        self.pass_label.pack()

        self.subtitle_label = tk.Label(self, text="Enter password to continue\n", font=(DEFAULT_FONT, 18))
        self.subtitle_label.pack(padx=10, pady=10)

        self.menu_bar = MainMenuBar(self)
        self.config(menu=self.menu_bar)

        self.after(500, self.pass_label_blink)

    def key_press(self, event):
        if shared.valid_char(event.char) and len(self.input_password) < 100:
            self.input_password += event.char

        elif event.keysym == "BackSpace":
            if keyboard.is_pressed("ctrl"):
                self.input_password = ""
            else:
                self.input_password = self.input_password[:-1]

        elif event.keysym == "Return":
            print(self.input_password)

        self.update_pass_label()

    def update_pass_label(self):
        self.pass_label["text"] = ((PASS_DOT + " ") * len(self.input_password))
        if self.pass_label_cursor:
            self.pass_label["text"] += "|"

        shrink_length = 16  # Length of the input password before the password label becomes smaller
        font_size = 24 if len(self.input_password) < shrink_length else int(24 * shrink_length / len(self.input_password))

        self.pass_label["font"] = DEFAULT_FONT, font_size

    def pass_label_blink(self):
        self.pass_label_cursor = not self.pass_label_cursor
        self.update_pass_label()
        self.after(500, self.pass_label_blink)
