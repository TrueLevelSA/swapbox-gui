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
from threading import Event, Thread


class CashinDriver(ABC):

    def __init__(self, callback_message):
        super().__init__()
        self._stop_cashin = Event()
        self._callback_message = callback_message

    def start_cashin(self):
        """ async method, is stopped by calling stop_cashin """
        self._stop_cashin.clear()
        thread = Thread(target=self._start_cashin, daemon=True)
        thread.start()

    @abstractmethod
    def _start_cashin(self):
        """ this function is to be started in a separated thread and should loop while
        self._stop_cashin is not set"""
        pass

    def stop_cashin(self):
        self._stop_cashin.set()
