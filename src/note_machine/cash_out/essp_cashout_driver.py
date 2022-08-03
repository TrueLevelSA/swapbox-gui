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

import time

from eSSP import eSSP

from src.note_machine.cash_out.cashout_driver_base import CashoutDriver


class EsspCashoutDriver(CashoutDriver):
    _MAP_CHANNEL_NOTES = {
        1: 10,
        2: 20,
        3: 50,
        4: 100,
        5: 200,
    }

    def __init__(self, validator_port):
        self._validator_port = validator_port
        self.validator = None

    def start_cashout(self):
        #  Create a new object ( Validator Object ) and initialize it
        print("Start cashin")
        self.validator = eSSP(com_port=self._validator_port, ssp_address="0", nv11=False, debug=True)

    def stop_cashout(self):
        print("Stop cashout")
        self._close_validator()

    def get_balance(self):
        balance = {}
        for note in EsspCashoutDriver._MAP_CHANNEL_NOTES.values():
            balance[note] = self.validator.get_note_amount(int(note))
            time.sleep(0.5)
        return balance

    def do_cashout(self, amount, currency):
        validator.payout(int(amount), currency)

    def _close_validator(self):
        self.validator.close()
