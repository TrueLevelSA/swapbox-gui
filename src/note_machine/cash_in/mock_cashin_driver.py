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

import zmq

from src.note_machine.cash_in.cashin_driver_base import CashinDriver


class MockCashinDriver(CashinDriver):

    def __init__(self, callback_message, zmq_mock_url):
        super().__init__(callback_message)
        self._zmq_mock_url = zmq_mock_url

    def _start_cashin(self):
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect(self._zmq_mock_url)
        zsock.setsockopt_string(zmq.SUBSCRIBE, '')

        while not self._stop_cashin.is_set():
            msg = zsock.recv_multipart()
            self._callback_message(msg[0].decode('utf-8'))

        zctx.destroy()
