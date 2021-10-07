import time

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image


class TripleTapImage(ButtonBehavior, Image):
    __events__ = ('on_triple_tap', )

    def __init__(self, **kwargs):
        super(TripleTapImage, self).__init__(**kwargs)
        self.taps = [0.0, 0.0]

    def on_press(self):
        now = time.time()
        if (now - self.taps[0]) < 1.0:
            self.dispatch('on_triple_tap')
        else:
            self.taps[0], self.taps[1] = self.taps[1], time.time()

    def on_double_tap(self):
        pass

    def on_triple_tap(self):
        pass
