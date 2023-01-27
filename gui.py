import tkinter as tk
import keyboard

import shared


class MainMenuBar(tk.Menu):
    def __init__(self, main_window):
        super().__init__()

        # File menu
        self.file_menu = tk.Menu(self)
        self.file_menu.add_command(label="Change Password", command=lambda: print("HIHIIHA"))
        self.add_cascade(label="File", menu=self.file_menu)


class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Attributes
        self.input_password = ""

        # Initialize GUI
        self.title("Protecc")
        self.bind("<Key>", self.key_press)

        self.title_label = tk.Label(self, text="This folder is \n\"protecc\"ted", font=("Raleway", 48))
        self.title_label.pack(padx=10, pady=10)

        self.subtitle_label = tk.Label(self, text="Enter password to continue", font=("Raleway", 18))
        self.subtitle_label.pack(padx=10, pady=10)

        self.password_label = tk.Label(self, text="", font=("Raleway", 24))
        self.password_label.pack()

        self.menu_bar = MainMenuBar(self)
        self.config(menu=self.menu_bar)

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
        self.password_label["text"] = ((shared.PASS_DOT + " ") * len(self.input_password))[:-1]

        shrink_length = 16  # Length of the input password before the the password label becomes smaller
        font_size = 24 if len(self.input_password) < shrink_length else int(24 * shrink_length / len(self.input_password))

        self.password_label["font"] = "Raleway", font_size
