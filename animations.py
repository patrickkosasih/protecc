import tkinter as tk
from abc import ABC, abstractmethod
from typing import Callable, Any


class Animation(ABC):
    def __init__(self, root: tk.Tk,
                 duration: int,
                 frame_period: int = 16,
                 call_on_finish: Callable[[], Any] = lambda: None):

        self.root = root
        self.duration = duration
        self.frame_period = frame_period  # Delay between each frame in milliseconds.
        self.call_on_finish = call_on_finish

        self.current_time = 0.0  # How long the animation has been running in seconds.

    def start(self):
        self.root.after(self.frame_period, self._loop)

    def _loop(self):
        self.update()

        self.current_time += self.frame_period
        if self.current_time < self.duration:
            self.root.after(self.frame_period, self._loop)

    @abstractmethod
    def update(self):
        ...
