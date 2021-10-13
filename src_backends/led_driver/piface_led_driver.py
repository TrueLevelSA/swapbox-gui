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

from src_backends.led_driver.led_driver_base import LedDriver
import pifacedigitalio


class LedDriverPiFace(LedDriver):
    def __init__(self):
        super().__init__()
        self._pifacedigital = pifacedigitalio.PiFaceDigital()

    def led_on(self):
        self._pifacedigital.output_pins[0].turn_on()  # this command does the same thing..
        self._pifacedigital.leds[0].turn_on()  # as this command

    def led_off(self):
        self._pifacedigital.output_pins[0].turn_off()  # this command does the same thing..
        self._pifacedigital.leds[0].turn_off()  # as this command

    def close(self):
        self._pifacedigital.deinit_board()
