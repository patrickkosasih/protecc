"""
Protecc
by Patrick Kosasih

A python program that encrypts and decrypts files.
Initially made to keep my super private files safe from outsiders and to learn the fundamentals of data encryption.
"""

import file_manager
import gui

path = "D:/protecc"  # Path of folder to be encrypted


# # Manual encryption without password.
# match input("[E]ncrypt or [D]ecrypt? ").upper():
#     case "E":
#         print("Encrypting...")
#         count = file_manager.encrypt_dir(path)
#         print(f"Finished encrypting {count} files")
#     case "D":
#         print("Decrypting...")
#         count = file_manager.decrypt_dir(path)
#         print(f"Finished decrypting {count} files")
#     case _:
#         print("Invalid option bruh")


def main():
    gui.MainWindow().mainloop()


if __name__ == '__main__':
    main()
