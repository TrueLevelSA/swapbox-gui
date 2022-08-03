#  Swap-box
#  Copyright (c) 2022 TrueLevel SA
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
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

import RPi.GPIO as GPIO

from src.led.led_driver_base import LedDriver

GPIO.cleanup()


class LedDriverGPIO(LedDriver):
    def __init__(self):
        super().__init__()
        self._led_pin = 7
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._led_pin, GPIO.OUT)
        GPIO.output(self._led_pin, GPIO.HIGH)

    def led_on(self):
        GPIO.output(self._led_pin, GPIO.LOW)

    def led_off(self):
        GPIO.output(self._led_pin, GPIO.HIGH)

    def close(self):
        GPIO.cleanup()
