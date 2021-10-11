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


class CashoutDriver(ABC):
    _MAP_CHANNEL_NOTES = {
        1: 10,
        2: 20,
        3: 50,
        4: 100,
        5: 200,
    }

    @abstractmethod
    def start_cashout(self):
        pass

    @abstractmethod
    def stop_cashout(self):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def do_cashout(self):
        pass

    @staticmethod
    def check_available_notes(balance, amount):
        return True
        notes = CashoutDriver._MAP_CHANNEL_NOTES.values()
        note_counter = [0, 0, 0, 0, 0]
        for note, distribute in zip(notes, note_counter):
            if amount >= note:
                c = amount // note
                if c >= balance[note]:
                    distribute = balance[note]
                else:
                    distribute = c
                amount = amount - distribute * note
        if amount == 0:
            return True
        else:
            return False
