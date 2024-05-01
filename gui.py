import tkinter as tk
from tkinter import messagebox, simpledialog
import keyboard
from typing import Callable

import shared
import passwords


DEFAULT_FONT = "Raleway"
PASS_DOT = chr(0x2022)


LOCKED_COLOR = "#ff584d"


class MainMenuBar(tk.Menu):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()

        self.main_window = main_window

        # File menu
        self.settings_menu = tk.Menu(self)
        self.settings_menu.add_command(label="Change Password", command=lambda: print("HIHIIHA"))

        self.add_cascade(label="Settings", menu=self.settings_menu)


class PadlockIcon(tk.Canvas):
    def __init__(self, root, width=250, height=250, **kwargs):
        super().__init__(root, width=width, height=height, **kwargs)

        self.size = width, height
        self.color = LOCKED_COLOR
        self.angle = 180

        """
        Padlock canvas components
        """
        self.inner_arc = -1
        self.outer_arc = -1
        self.rounded_rect = [-1 for _ in range(6)]

        self.draw()

    def draw(self):
        """
        Draw/initialize the components of the padlock on the canvas.
        """

        w, h = self.size
        mid = h * 0.42

        rrr = h // 8
        rrd = rrr * 2

        rao = w * 0.38
        rai = w * 0.22

        self.outer_arc = self.create_arc(w / 2 - rao, mid - rao, w / 2 + rao, mid + rao,
                                         start=0, extent=self.angle, fill=self.color, outline="")

        self.inner_arc = self.create_arc(w / 2 - rai, mid - rai, w / 2 + rai, mid + rai,
                                         start=0, extent=self.angle, fill=self["background"],outline="")


        self.rounded_rect[0] = self.create_oval(0, mid, rrd, mid + rrd, fill=self.color, outline="")
        self.rounded_rect[1] = self.create_oval(0, h, rrd, h - rrd, fill=self.color, outline="")
        self.rounded_rect[2] = self.create_oval(w, mid, w - rrd, mid + rrd, fill=self.color, outline="")
        self.rounded_rect[3] = self.create_oval(w, h, w - rrd, h - rrd, fill=self.color, outline="")
        self.rounded_rect[4] = self.create_rectangle(0, mid + rrr, w, h - rrr, fill=self.color, outline="")
        self.rounded_rect[5] = self.create_rectangle(rrr, mid, w - rrr, h, fill=self.color, outline="")


class RoundedButton(tk.Canvas):
    def __init__(self, root, width, height, color: str or tuple = "#9c9c9c",
                 command: Callable[[], None] = lambda: None,
                 text="",
                 **kwargs):

        super().__init__(root, width=width, height=height, **kwargs)

        """
        General attributes
        """
        self.size = width, height
        self._original_color = color
        self.command = command
        self.text_str = text

        """
        Button canvas components
        """
        self.components = [-1 for _ in range(3)]
        self.text = -1
        self.draw()

        """
        Mouse bindings
        """
        self.bind("<Button-1>", self.on_mouse_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.bind("<Enter>", self.on_mouse_enter)
        self.bind("<Leave>", self.on_mouse_leave)

        self.hover = False
        self.mouse_down = False

    def draw(self):
        w, h = self.size
        m = 3

        self.components[0] = self.create_oval(m, m, h - m, h - m, fill=self._original_color, outline="")
        self.components[1] = self.create_oval(m + w - h, m, w - m, h - m, fill=self._original_color, outline="")
        self.components[2] = self.create_rectangle(h / 2, m, w - h / 2, h - m, fill=self._original_color, outline="")

        self.text = self.create_text(w / 2, h / 2, text=self.text_str, font=(DEFAULT_FONT, 24))

    def _set_color(self, color: str or tuple):
        for x in self.components:
            self.itemconfig(x, fill=color)

    def on_mouse_down(self, event):
        self.mouse_down = True
        self._set_color(shared.hsv_factor(self._original_color, vf=0.9))

    def on_mouse_up(self, event):
        self.mouse_down = False
        if self.hover:
            self._set_color(shared.hsv_factor(self._original_color, vf=1.1))
            self.command()
        else:
            self._set_color(self._original_color)

    def on_mouse_enter(self, event):
        self.hover = True
        self._set_color(shared.hsv_factor(self._original_color, vf=0.9 if self.mouse_down else 1.1))

    def on_mouse_leave(self, event):
        self.hover = False
        self._set_color(self._original_color)


class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()

        """
        Attributes
        """
        self.input_password = ""
        self.pass_label_cursor = True

        """
        GUI Widgets
        """
        self.title("Protecc")
        self.bind("<Key>", self.key_press)

        self.title_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=(DEFAULT_FONT, 48))
        self.title_label.pack(padx=30, pady=20)

        self.padlock_icon = PadlockIcon(self)
        self.padlock_icon.pack()

        self.pass_label = tk.Label(self, text="|", font=(DEFAULT_FONT, 24))
        self.pass_label.pack(pady=10)

        self.subtitle_label = tk.Label(self, text="Enter password to continue\n", font=(DEFAULT_FONT, 18))
        self.subtitle_label.pack(padx=10, pady=10)

        self.enter_button = RoundedButton(self, 250, 75, text="Enter", command=self.enter_password)
        self.enter_button.pack(pady=10)

        self.menu_bar = MainMenuBar(self)
        self.config(menu=self.menu_bar)

        self.after(500, self.pass_label_blink)

        if not passwords.pass_file_exists():
            self.setup()

    def key_press(self, event):
        if shared.valid_char(event.char) and len(self.input_password) < 100:
            self.input_password += event.char

        elif event.keysym == "BackSpace":
            if keyboard.is_pressed("ctrl"):
                self.input_password = ""
            else:
                self.input_password = self.input_password[:-1]

        elif event.keysym == "Return":
            self.enter_password()

        self.update_pass_label()

    def enter_password(self):
        print("Correct!" if passwords.check_password(self.input_password) else "Wrong!")

    def set_unlocked(self, unlocked: bool):
        ...

    def setup(self):
        while True:
            password = simpledialog.askstring("Initialize Password",
                                              "To finish setting up Protecc, please set a password:", show=PASS_DOT)

            if password == "":  # OK button but text box is empty
                messagebox.showwarning("Error", "Password is empty!")
                continue
            elif password is None:  # Cancel or X button
                self.destroy()
                return

            confirm = simpledialog.askstring("Confirm Password",
                                              "Enter your password again:", show=PASS_DOT)

            if confirm is None:
                self.destroy()
                return
            elif password != confirm:
                messagebox.showwarning("Error", "Passwords do not match!")
                continue
            else:
                break

        passwords.init_pass_file(password)
        messagebox.showinfo("Success", "Your password has been set!")

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
