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
import json
from json import JSONDecodeError
from typing import List, Optional, Callable

from pydantic import BaseModel

from src.zmq.subscriber import ZMQSubscriber


class Blockchain(BaseModel):
    current_block: int
    sync_block: int
    is_in_sync: bool


class System(BaseModel):
    temp: int
    cpu: int


class Status(BaseModel):
    blockchain: Blockchain
    system: System


StatusCallback = Callable[[Status], None]


class StatusSubscriber:
    def __init__(self, url: str):
        self._callbacks: List[StatusCallback] = []
        self._subscriber = ZMQSubscriber(self._update_status, url, "status")
        self._last_status: Optional[Status] = None

    def _update_status(self, message):
        """Update status with newly received status"""
        self._last_status = self._parse_message(message)

        for callback in self._callbacks:
            callback(self._last_status)

    @staticmethod
    def _parse_message(message: str) -> Status:
        """
        Parses message back from status raw message

        :argument message raw message from status updates
        """
        try:
            return Status(**json.loads(message))
        except JSONDecodeError as e:
            print(e)

    def start(self):
        self._subscriber.start()

    def stop(self):
        self._subscriber.stop_listening()

    def get_last_status(self) -> Status:
        """Get last known status"""
        return self._last_status

    def subscribe(self, callback: StatusCallback):
        """Subscribe to the status updates.
        """
        self._callbacks.append(callback)
