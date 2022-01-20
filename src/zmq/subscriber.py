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
from threading import Thread, Event

import zmq


class ZMQSubscriber(Thread):
    TOPIC_PRICEFEED = 'pricefeed'
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
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.SUB)
        socket.connect(self._zmq_url)
        socket.subscribe(self._topic)

        self._stop_listening.clear()

        while not self._stop_listening.is_set():
            _, msg = self._split_topic_data(socket.recv_string())
            self._callback_message(msg)

        socket.close()
        context.destroy()

    def stop_listening(self):
        self._stop_listening.set()

    @staticmethod
    def _split_topic_data(msg: str):
        """Split topic and data."""
        # that's the beginning of the JSON
        s = msg.find('{')
        return msg[0:s].strip(), msg[s:]
