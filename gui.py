import os
import tkinter as tk
from threading import Thread
from tkinter.ttk import Progressbar
from tkinter import messagebox, simpledialog
import keyboard
from typing import Callable

import file_codec
import shared
import passwords


DEFAULT_FONT = "Raleway"
PASS_DOT = chr(0x2022)


class MainMenuBar(tk.Menu):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()

        self.main_window = main_window

        # File menu
        self.settings_menu = tk.Menu(self)
        self.settings_menu.add_command(label="Change Password", command=self.main_window.verify_and_change_password)

        self.add_cascade(label="Settings", menu=self.settings_menu)


class PadlockIcon(tk.Canvas):
    COLORS = {
        "locked": "#ff6666",
        "unlocked": "#8fff8f",
        "locking": "#ffa666",
        "unlocking": "#ffe066"
    }

    ANGLES = {
        "locked": 180,
        "unlocked": 150,
        "locking": 165,
        "unlocking": 180
    }

    def __init__(self, root, width=250, height=250, **kwargs):
        super().__init__(root, width=width, height=height, **kwargs)

        self.size = width, height

        """
        Padlock canvas components
        """
        self.inner_arc = -1
        self.outer_arc = -1
        self.rounded_rect = [-1 for _ in range(6)]

        self.draw()

    def draw(self):
        """
        Draw/initialize the components of the padlock on the canvas. Only called once in the constructor.
        """

        w, h = self.size
        mid = h * 0.42

        rrr = h // 8
        rrd = rrr * 2

        rao = w * 0.38
        rai = w * 0.22

        color = PadlockIcon.COLORS["locked"]
        angle = 180

        self.outer_arc = self.create_arc(w / 2 - rao, mid - rao, w / 2 + rao, mid + rao,
                                         start=0, extent=angle, fill=color, outline="")

        self.inner_arc = self.create_arc(w / 2 - rai, mid - rai, w / 2 + rai, mid + rai,
                                         start=0, extent=angle, fill=self["background"],outline="")

        self.rounded_rect[0] = self.create_oval(0, mid, rrd, mid + rrd, fill=color, outline="")
        self.rounded_rect[1] = self.create_oval(0, h, rrd, h - rrd, fill=color, outline="")
        self.rounded_rect[2] = self.create_oval(w, mid, w - rrd, mid + rrd, fill=color, outline="")
        self.rounded_rect[3] = self.create_oval(w, h, w - rrd, h - rrd, fill=color, outline="")
        self.rounded_rect[4] = self.create_rectangle(0, mid + rrr, w, h - rrr, fill=color, outline="")
        self.rounded_rect[5] = self.create_rectangle(rrr, mid, w - rrr, h, fill=color, outline="")

    def set_gui_state(self, state: str):
        if state not in PadlockIcon.COLORS:
            raise ValueError(f"invalid state argument: {state}")

        color = PadlockIcon.COLORS[state]
        angle = PadlockIcon.ANGLES[state]

        for x in self.rounded_rect + [self.outer_arc]:
            self.itemconfig(x, fill=color)

        self.itemconfig(self.outer_arc, extent=angle)
        self.itemconfig(self.inner_arc, extent=180)


class RoundedButton(tk.Canvas):
    DEFAULT_COLOR = "#bababa"

    def __init__(self, root, width, height, color: str or tuple = DEFAULT_COLOR,
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

    def on_mouse_down(self, _):
        self.mouse_down = True
        self._set_color(shared.hsv_factor(self._original_color, vf=0.9))

    def on_mouse_up(self, _):
        self.mouse_down = False
        if self.hover:
            self._set_color(shared.hsv_factor(self._original_color, vf=1.1))
            self.command()
        else:
            self._set_color(self._original_color)

    def on_mouse_enter(self, _):
        self.hover = True
        self._set_color(shared.hsv_factor(self._original_color, vf=0.9 if self.mouse_down else 1.1))

    def on_mouse_leave(self, _):
        self.hover = False
        self._set_color(self._original_color)


class MainWindow(tk.Tk):
    def __init__(self, locked_folder_path: str):
        super(MainWindow, self).__init__()

        """
        Attributes
        """
        self.input_password = ""
        self.pass_label_cursor = True
        self._gui_state = "locked"

        self.folder = file_codec.ProteccFolder(locked_folder_path, self.update_progress)

        """
        GUI Widgets
        
        1. Title label
        2. Padlock icon
        3. Pass label
        4. Subtitle label
        5. Bottom frame
            a. Enter button     - When locked
            b. Open button      - When unlocked
            c. Lock button      - When unlocked
            d. Progress bar     - When locking/unlocking
            e. Progress label   - When locking/unlocking
        """
        self.title(f"Protecc - {locked_folder_path}")
        self.bind("<Key>", self.key_press)

        self.title_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=(DEFAULT_FONT, 48))
        self.padlock_icon = PadlockIcon(self)
        self.pass_label = tk.Label(self, text="|", font=(DEFAULT_FONT, 24))
        self.subtitle_label = tk.Label(self, text="Enter password to continue.", font=(DEFAULT_FONT, 18))

        self.bottom_frame = tk.Frame(self, height=75)
        self.enter_button = RoundedButton(self.bottom_frame, 250, 75, text="Enter", command=self.enter_password)
        self.open_button = RoundedButton(self.bottom_frame, 150, 75, text="Open", command=self.open_folder)
        self.lock_button = RoundedButton(self.bottom_frame, 150, 75, text="Lock", command=self.lock_folder)
        self.progress_bar = Progressbar(self.bottom_frame, length=300)
        self.progress_label = tk.Label(self.bottom_frame, text="", font=(DEFAULT_FONT, 12))

        self.title_label.pack(padx=30, pady=20)
        self.padlock_icon.pack()
        self.pass_label.pack(pady=10)
        self.subtitle_label.pack(padx=10, pady=10)
        self.bottom_frame.pack(pady=10)

        self.menu_bar = MainMenuBar(self)
        self.config(menu=self.menu_bar)

        self.set_gui_state("locked" if self.folder.locked else "unlocked")
        self.after(500, self.pass_label_blink)

        if not passwords.pass_file_exists():
            if self.folder.locked:
                messagebox.showerror("Error", "Password data not found! Folder cannot be unlocked.")
                self.destroy()
            else:
                self.set_password(setup_mode=True)

    def key_press(self, event):
        if not self.folder.locked:
            return

        self.subtitle_label["text"] = "Enter password to continue"

        if passwords.is_valid_char(event.char) and len(self.input_password) < 100:
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
        if not self.input_password or self._gui_state != "locked":
            return

        correct = passwords.verify_password(self.input_password)

        if correct:
            self.set_gui_state("unlocking")
            Thread(target=self.folder.decrypt).start()
        else:
            self.subtitle_label["text"] = "Incorrect password!"

    def open_folder(self):
        os.system(f"explorer {self.folder.path}")

    def lock_folder(self):
        self.set_gui_state("locking")
        Thread(target=self.folder.encrypt).start()

    def set_gui_state(self, state: str):
        self._gui_state = state

        match state:
            case "locked":
                self.title_label["text"] = "This folder is \n\"protecc\"ted."
                self.subtitle_label["text"] = "Enter password to continue."
                self.input_password = ""
                self.update_pass_label()

                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.enter_button.pack()

            case "unlocked":
                self.title_label["text"] = "This folder is \nunlocked."
                self.subtitle_label["text"] = "What do you want to do?"

                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.open_button.pack(side=tk.LEFT, padx=5)
                self.lock_button.pack(side=tk.RIGHT, padx=5)

            case "locking":
                self.subtitle_label["text"] = "Locking folder, please wait..."

                self.open_button.pack_forget()
                self.lock_button.pack_forget()
                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.progress_bar.pack(pady=5)
                self.progress_label.pack(pady=5)

            case "unlocking":
                self.subtitle_label["text"] = "Access granted! Please wait..."
                self.enter_button.pack_forget()

                self.progress_bar.pack(pady=5)
                self.progress_label.pack(pady=5)

            case _:
                raise ValueError(f"invalid state argument: {state}")

        self.padlock_icon.set_gui_state(state)

    def set_password(self, setup_mode=False):
        while True:
            new_pass = simpledialog.askstring("Initialize Password" if setup_mode else "Change Password",
                                              "To finish setting up Protecc, please set a password:" if setup_mode else
                                              "Enter your new password:" + 40 * " ",
                                              show=PASS_DOT)

            if new_pass == "":  # OK button and empty text box
                messagebox.showwarning("Error", "Password is empty!")
                continue
            elif new_pass is None:  # Cancel or X button
                self.destroy()
                return
            elif not passwords.is_valid_password(new_pass):
                messagebox.showwarning("Error", "Password contains illegal character(s)!")
                continue

            confirm_pass = simpledialog.askstring("Initialize Password" if setup_mode else "Change Password",
                                                  "Enter the password again:" + 40 * " ",
                                                  show=PASS_DOT)

            if confirm_pass is None:
                self.destroy()
                return
            elif new_pass != confirm_pass:
                messagebox.showwarning("Error", "Passwords do not match!")
                continue
            else:
                break

        passwords.init_pass_file(new_pass)
        messagebox.showinfo("Success", "Your password has been set!")

    def verify_and_change_password(self):
        while True:
            old_pass = simpledialog.askstring("Change Password",
                                              "Enter your current password:" + 40 * " ",
                                              show=PASS_DOT)

            if old_pass == "":  # OK button and empty text box
                messagebox.showwarning("Error", "Password is empty!")
            elif old_pass is None:  # Cancel or X button
                break
            elif not passwords.verify_password(old_pass):
                messagebox.showwarning("Error", "Incorrect password!")
            else:
                self.set_password()
                break


    def update_pass_label(self):
        if self._gui_state != "locked":
            self.pass_label["text"] = ""
            return

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

    def update_progress(self, current, total):
        if current == total:
            if self._gui_state == "locking":
                self.set_gui_state("locked")
            elif self._gui_state == "unlocking":
                self.set_gui_state("unlocked")
                self.open_folder()
        else:
            self.progress_bar["value"] = current / total * 100
            self.progress_label["text"] = f"{'En' if self._gui_state == 'locking' else 'De'}crypting {current}/{total}"
