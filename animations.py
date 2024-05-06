import tkinter as tk
from abc import ABC, abstractmethod
from typing import Callable, Any

from shared import *


class Interpolations:
    @staticmethod
    def linear(x):
        return x

    @staticmethod
    def ease_in_out(x: float, power: float = 2.0) -> float:
        if x <= 0.5:
            return (2 * x) ** power / 2
        else:
            return 1 - (2 - 2 * x) ** power / 2


class Animation(ABC):
    def __init__(self, root: tk.Tk,
                 duration: int or float,
                 frame_period: int = 8,
                 interpol_func: Callable[[float], float] = Interpolations.linear,
                 call_on_finish: Callable[[], Any] = lambda: None):

        self.root = root
        self._duration = duration
        self.frame_period = frame_period  # Delay between each frame in milliseconds.
        self.interpol_func = interpol_func
        self.call_on_finish = call_on_finish

        self._running = False
        self._current_time = 0.0  # How long the animation has been running in seconds.

    def start(self):
        self._running = True
        self.root.after(self.frame_period, self._loop)

    def stop(self):
        self._running = False

    def restart(self):
        self._current_time = 0.0
        self.start()

    def _loop(self):
        self._current_time += self.frame_period / 1000

        if self._current_time >= self._duration:
            self.finish()
            self.call_on_finish()
            self._running = False

        if self._running:
            self.update()
            self.root.after(self.frame_period, self._loop)

    @property
    def anim_phase(self) -> float:
        return max(0.0, min(self._current_time / self._duration, 1.0))

    @property
    def interpol_phase(self) -> float:
        return self.interpol_func(self.anim_phase)

    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def finish(self):
        ...


class VarSlider(Animation):
    def __init__(self, root: tk.Tk, duration: int or float,
                 start_val: int or float,
                 end_val: int or float,
                 setter_func: Callable[[int or float], None],
                 **kwargs):

        super().__init__(root, duration, **kwargs)

        self._start_val = start_val
        self._end_val = end_val
        self.setter_func = setter_func

        self._current_val = start_val

    def update(self):
        self._current_val = self.interpol_phase * (self._end_val - self._start_val) + self._start_val
        self.setter_func(self._current_val)

    def finish(self):
        self._current_val = self._end_val
        self.setter_func(self._current_val)


class FadeColor(Animation):
    def __init__(self, root: tk.Tk, duration: int or float,
                 start_color: tuple or str,
                 end_color: tuple or str,
                 set_color_func: Callable[[str], None],
                 **kwargs):

        super().__init__(root, duration, **kwargs)

        self._start_color = start_color
        self._end_color = end_color
        self.set_color_func = set_color_func

    def update(self):
        self.set_color_func(mix_color(self._start_color, self._end_color, self.interpol_phase))

    def finish(self):
        self.set_color_func(self._end_color)
