"""
Protecc
by Patrick Kosasih

A python program that encrypts and decrypts files.
Initially made to keep my super private files safe from outsiders and to learn the fundamentals of data encryption.

Note: The encryption and security algorithm of Protecc is slow and bad. Any hacker with a few months of experience could
easily crack the encryption in minutes. :(
"""

import file_manager
import gui


def main():
    gui.MainWindow("D:\\protecc").mainloop()


if __name__ == '__main__':
    main()
