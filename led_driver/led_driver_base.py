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

from abc import ABC, abstractmethod

class LedDriver(ABC):
    ''' LedDriver abstract class, implements led_on(), led_off()'''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def led_on(self):
        pass

    @abstractmethod
    def led_off(self):
        pass

    @abstractmethod
    def close(self):
        pass
