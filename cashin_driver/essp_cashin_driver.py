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

from cashin_driver.cashin_driver_base import CashinDriver
import time
from eSSP import eSSP
from eSSP.constants import Status


i = 0
class EsspCashinDriver(CashinDriver):
    _MAP_CHANNEL_NOTES = {
        1: 10,
        2: 20,
        3: 50,
        4: 100,
        5: 200,
    }

    def __init__(self, callback_message, validator_port):
        super().__init__(callback_message)
        self._validator_port= validator_port

    def _start_cashin(self):
        #  Create a new object ( Validator Object ) and initialize it
        print("Start cashin lol")
        validator = eSSP(com_port=self._validator_port, ssp_address="0", nv11=False, debug=True)

        global i
        EsspCashinDriver._setup_validator(validator)

        while not self._stop_cashin.is_set():
            last_event = validator.get_last_event()

            if last_event is None:
                continue

            (note, currency, event) = last_event

            if event == Status.SSP_POLL_CREDIT:
                if note not in EsspCashinDriver._MAP_CHANNEL_NOTES.keys():
                    continue
                value = EsspCashinDriver._MAP_CHANNEL_NOTES[note]
                self._callback_message("CHF:{}".format(value))

        EsspCashinDriver._close_validator(validator)

    @staticmethod
    def _setup_validator(validator):
        # all notes are sent to cashbox
        for note in EsspCashinDriver._MAP_CHANNEL_NOTES.values():
            validator.set_route_cashbox(int(note))
            time.sleep(0.5)

    @staticmethod
    def _close_validator(validator):
        validator.disable_validator()
        time.sleep(1)
        validator.close()
