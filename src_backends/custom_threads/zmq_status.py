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

from threading import Thread, Event
import zmq
import json

class ZMQStatus(Thread):

    def __init__(self, callback_message, zmq_url):
        super().__init__()
        self.daemon = True
        self._stop_listening = Event()
        self._callback_message = callback_message
        self._zmq_url = zmq_url

    def run(self):
        """Run Worker Thread."""
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect(self._zmq_url)
        zsock.setsockopt_string(zmq.SUBSCRIBE,'status')

        self._stop_listening.clear()

        while not self._stop_listening.is_set():
            msg = zsock.recv_multipart()
            self._callback_message(msg[1].decode('utf-8'))

        zsock.close()
        zctx.destroy()

    def stop_listening(self):
        self._stop_listening.set()
