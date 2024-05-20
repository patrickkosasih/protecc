import os
import tkinter as tk
from threading import Thread
from tkinter.ttk import Progressbar
from tkinter import messagebox, simpledialog
import keyboard
from typing import Callable

import file_manager
import shared
import passwords
import animations as anim

DEFAULT_FONT = "Raleway"
PASS_DOT = chr(0x2022)
GUI_STATES = ["locked", "unlocked", "locking", "unlocking"]


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
        "locking": "#ffe066",
        "unlocking": "#ffa666"
    }

    ANGLES = {
        "locked": 180,
        "unlocked": 150,
        "locking": 165,
        "unlocking": 180
    }

    def __init__(self, root, width=250, height=250, bg="SystemButtonFace", **kwargs):
        super().__init__(root, width=width, height=height, **kwargs)

        self.configure(bg=bg, highlightthickness=0)

        self._root = root
        self._size = width, height
        self._gui_state = "locked"

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

        w, h = self._size
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

    def set_gui_state(self, state: str, duration=0.5):
        if state not in GUI_STATES:
            raise ValueError(f"invalid state argument: {state}")

        prev_state = self._gui_state
        self._gui_state = state

        old_color, new_color = PadlockIcon.COLORS[prev_state], PadlockIcon.COLORS[state]
        old_angle, new_angle = PadlockIcon.ANGLES[prev_state], PadlockIcon.ANGLES[state]

        if duration <= 0:
            self.set_color(new_color)
            self.set_angle(new_angle)
        else:
            anim.FadeColor(self._root, duration, old_color, new_color, self.set_color).start()
            anim.VarSlider(self._root, duration, old_angle, new_angle, self.set_angle,
                           interpol_func=anim.Interpolations.ease_in_out).start()

    def set_color(self, color: str):
        for x in self.rounded_rect + [self.outer_arc]:
            self.itemconfig(x, fill=color)

    def set_angle(self, angle: int):
        self.itemconfig(self.outer_arc, extent=angle)


class RoundedButton(tk.Canvas):
    DEFAULT_COLOR = "#bababa"

    def __init__(self, root, width, height,
                 bg: str = "", color: str = DEFAULT_COLOR,
                 command: Callable[[], None] = lambda: None,
                 text="",
                 **kwargs):

        super().__init__(root, width=width, height=height, **kwargs)
        self.configure(bg=bg, highlightthickness=0)

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
    def __init__(self, folder_path: str):
        super(MainWindow, self).__init__()

        """
        Attributes
        """
        self.folder = file_manager.ProteccFolder(folder_path, self.update_progress)
        self._gui_state = "locked"

        self.input_password = ""
        self.pass_label_cursor = False
        self.subtitle_flash_anim: anim.FadeColor or None = None

        self.bg = "#f1f1f1"
        self.fg = "#292a2e"

        """
        Window configurations
        """
        # self.title(f"Protecc - {folder_path}")
        self.title("Protecc")
        self.bind("<Key>", self.key_press)
        self.configure(bg=self.bg)

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
        self.title_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=(DEFAULT_FONT, 48), bg=self.bg, fg=self.fg)
        self.padlock_icon = PadlockIcon(self, bg=self.bg)
        self.pass_label = tk.Label(self, text="", font=(DEFAULT_FONT, 24), bg=self.bg, fg=self.fg)
        self.subtitle_label = tk.Label(self, text="Enter password to continue.", font=(DEFAULT_FONT, 18), bg=self.bg, fg=self.fg)

        self.bottom_frame = tk.Frame(self, height=75, bg=self.bg)
        self.enter_button = RoundedButton(self.bottom_frame, 250, 75, text="Enter", command=self.enter_password, bg=self.bg)
        self.open_button = RoundedButton(self.bottom_frame, 150, 75, text="Open", command=self.open_folder, bg=self.bg)
        self.lock_button = RoundedButton(self.bottom_frame, 150, 75, text="Lock", command=self.lock_folder, bg=self.bg)
        self.progress_bar = Progressbar(self.bottom_frame, length=300)
        self.progress_label = tk.Label(self.bottom_frame, text="", font=(DEFAULT_FONT, 12), bg=self.bg, fg=self.fg)

        self.title_label.pack(padx=30, pady=20)
        self.padlock_icon.pack()
        self.pass_label.pack(pady=10)
        self.subtitle_label.pack(padx=10, pady=10)
        self.bottom_frame.pack(pady=10)

        self.menu_bar = MainMenuBar(self)
        self.config(menu=self.menu_bar)

        self.set_gui_state("locked" if self.folder.locked else "unlocked", 0.0)
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

        self.subtitle_label["text"] = "Enter password to continue."

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
            self.flash_subtitle("ff0000", 0.5)

    def open_folder(self):
        os.system(f"explorer {self.folder.path}")

    def lock_folder(self):
        self.set_gui_state("locking")
        Thread(target=self.folder.encrypt).start()

    def set_gui_state(self, state: str, duration=0.25):
        if state not in GUI_STATES:
            raise ValueError(f"invalid state argument: {state}")

        self._gui_state = state
        self.padlock_icon.set_gui_state(state, duration)

        match state:
            case "locked":
                self.set_text_fade(self.title_label, "This folder is \n\"protecc\"ted.", duration * 2.5)
                self.set_text_fade(self.subtitle_label, "Enter password to continue.", duration * 1.5)
                self.input_password = ""
                self.update_pass_label()

                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.enter_button.pack()

            case "unlocked":
                self.set_text_fade(self.title_label, "This folder is \nunlocked.", duration * 2.5)
                self.set_text_fade(self.subtitle_label, "What would you like to do?", duration * 1.5)

                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.open_button.pack(side=tk.LEFT, padx=5)
                self.lock_button.pack(side=tk.RIGHT, padx=5)

            case "locking":
                self.set_text_fade(self.subtitle_label, "Locking folder. Please wait...", duration)

                self.open_button.pack_forget()
                self.lock_button.pack_forget()
                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()

                self.progress_bar.pack(pady=5)
                self.progress_label.pack(pady=5)

            case "unlocking":
                self.subtitle_label["text"] = "Access granted! Please wait..."
                self.flash_subtitle("#00ff00", 0.75)

                self.enter_button.pack_forget()

                self.progress_bar.pack(pady=5)
                self.progress_label.pack(pady=5)

    def update_progress(self, current, total):
        if current > total:
            if self._gui_state == "locking":
                self.set_gui_state("locked")
            elif self._gui_state == "unlocking":
                self.set_gui_state("unlocked")
                self.open_folder()
        else:
            self.progress_bar["value"] = current / total * 100
            self.progress_label["text"] = f"{'En' if self._gui_state == 'locking' else 'De'}crypting {current}/{total}"

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

    def flash_subtitle(self, color: str, duration=0.4):
        if duration <= 0:
            return
        elif self.subtitle_flash_anim:
            self.subtitle_flash_anim.stop()

        self.subtitle_flash_anim = anim.FadeColor(self, duration, color, self.fg,
                                                  lambda c: self.subtitle_label.configure(fg=c))
        self.subtitle_flash_anim.start()

    def set_text_fade(self, label: tk.Label, text: str, duration=0.4):
        def fade_back():
            label["text"] = text
            anim.FadeColor(self, duration / 2, self.bg, self.fg,
                           set_color_func=lambda c: label.configure(fg=c)).start()

        anim.FadeColor(self, duration / 2, self.fg, self.bg,
                       set_color_func=lambda c: label.configure(fg=c),
                       call_on_finish=fade_back).start()
