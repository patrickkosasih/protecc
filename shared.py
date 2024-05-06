"""
shared.py
A shared module containing constants and functions that is used in multiple other modules
"""
import colorsys
import time
import os


def func_timer(func):
    # A decorator to measure the time taken to run a function
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)  # Call function
        time_taken = time.perf_counter() - time_before

        print(f"{func.__name__} took {time_taken} seconds to run")
        return ret

    return wrapper


"""
Color functions
"""


def rgb_hex_to_int(hex_rgb: str) -> tuple:
    """
    Converts a hex RGB string into three 8-bit values in a tuple

    e.g. "#ffe4ad" -> (255, 228, 173)
    """

    return tuple(int(hex_rgb[i: i + 2], base=16) for i in range(1, 7, 2))


def rgb_int_to_hex(rgb: tuple) -> str:
    return "#%02x%02x%02x" % rgb


def hsv_factor(rgb: tuple or str, hf=0, sf=1, vf=1) -> str:
    """
    Takes a 24 bit RGB value and changes it according to the given HSV factors (hue, saturation, and value)

    :param rgb: The RGB value can be in tuple (e.g. (255, 255, 255)) or a string with the "#RRGGBB" format

    :param hf: Hue factor
    :param sf: Saturation factor
    :param vf: Value (brightness) factor
    """

    if type(rgb) is str:
        rgb = rgb_hex_to_int(rgb)

    r, g, b = (x / 255.0 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    new_hsv = h + hf, s * sf, v * vf
    new_hsv = tuple(max(0, min(1, x)) for x in new_hsv)  # Clamp values between 0-1
    new_rgb = colorsys.hsv_to_rgb(*new_hsv)
    int_rgb = tuple(int(x * 255) for x in new_rgb)  # Convert RGB values from 0.0 - 1.0 to 0 - 255

    return rgb_int_to_hex(int_rgb)


def mix_color(c1: tuple or str, c2: tuple or str, fac=0.5) -> str:
    """
    Mixes two colors by averaging the RGB values. Colors must be in RGB tuple format.

    :param c1: Color 1.
    :param c2: Color 2.
    :param fac: The factor of the color mixing, with 0 being closer to c1 and 1 being closer to c2.
    """
    c1 = rgb_hex_to_int(c1) if type(c1) is str else c1
    c2 = rgb_hex_to_int(c2) if type(c2) is str else c2

    return rgb_int_to_hex(tuple(int((1 - fac) * x + fac * y) for x, y in zip(c1, c2)))
