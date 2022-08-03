# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time

from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image


class HomeLogo(ButtonBehavior, Image):
    __events__ = ('on_triple_tap', )

    def __init__(self, **kwargs):
        super(HomeLogo, self).__init__(**kwargs)
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
