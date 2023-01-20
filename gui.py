import tkinter as tk
import keyboard

import shared


class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Attributes
        self.input_password = ""

        # Initialize GUI
        self.title("Protecc")
        self.bind("<Key>", self.key_press)

        self.info_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=("Raleway", 36))
        self.info_label.pack(padx=10, pady=10)

        self.info_label2 = tk.Label(self, text="Enter password to continue", font=("Raleway", 18))
        self.info_label2.pack(padx=10, pady=10)

        self.password_label = tk.Label(self, text="", font=("Raleway", 24))
        self.password_label.pack()

    def key_press(self, event):
        if shared.valid_char(event.char):
            self.input_password += event.char
        elif event.keysym == "BackSpace":
            if keyboard.is_pressed("ctrl"):
                self.input_password = ""
            else:
                self.input_password = self.input_password[:-1]

        self.update_pass_label()

    def update_pass_label(self):
        self.password_label["text"] = ((shared.PASS_DOT + " ") * len(self.input_password))[:-1]
