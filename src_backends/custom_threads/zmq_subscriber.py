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


class ZMQSubscriber(Thread):
    TOPIC_PRICEFEED = 'priceticker'
    TOPIC_STATUS = 'status'

    def __init__(self, callback_message, zmq_url, topic):
        super().__init__()
        self.daemon = True
        self._stop_listening = Event()
        self._callback_message = callback_message
        self._zmq_url = zmq_url
        self._topic = topic

    def run(self):
        """Run Worker Thread."""
        z_ctx = zmq.Context.instance()
        z_sock = z_ctx.socket(zmq.SUB)
        z_sock.connect(self._zmq_url)
        z_sock.setsockopt_string(zmq.SUBSCRIBE, self._topic)

        self._stop_listening.clear()

        while not self._stop_listening.is_set():
            msg = z_sock.recv_multipart()
            self._callback_message(msg[1].decode('utf-8'))

        z_sock.close()
        z_ctx.destroy()

    def stop_listening(self):
        self._stop_listening.set()
