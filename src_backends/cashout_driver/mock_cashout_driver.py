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

from src_backends.cashout_driver.cashout_driver_base import CashoutDriver
import time

class MockCashoutDriver(CashoutDriver):

    def start_cashout(self):
        pass

    def stop_cashout(self):
        pass

    def get_balance(self):
        balance = {}
        for note in CashoutDriver._MAP_CHANNEL_NOTES.values():
            balance[note] = 1
            time.sleep(0.5)
        return balance

    def do_cashout(self, amount, currency="CHF"):
        print("Cashout: {} {}".format(amount, currency))
