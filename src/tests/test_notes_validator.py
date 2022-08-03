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

import os
import sys

# i hate importes in python
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from src.note_machine import EsspCashinDriver

import time


def test():
    validator_port = '/dev/ttyUSB0'

    driver = EsspCashinDriver(print, validator_port)

    try:
        driver.start_cashin()
        input("Enter or ^C to quit\n")
        driver.stop_cashin()
    except KeyboardInterrupt:
        driver.stop_cashin()

    time.sleep(5)


if __name__ == "__main__":
    test()
