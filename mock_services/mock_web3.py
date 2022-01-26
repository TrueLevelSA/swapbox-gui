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

import json
import os
import sys
from typing import Any

import argument
import zmq
from zmq import Socket

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from src_backends.node_rpc.node_rpc import ResponseBuy


class MockBackend:
    base_url = 'tcp://*'
    port = '5557'

    def __init__(self, auto_success: bool):
        context = zmq.Context()
        self.socket: Socket = context.socket(zmq.REP)
        self.socket.bind(f'{self.base_url}:{self.port}')
        self.auto_success = auto_success

        self.methods = {
            "buy": self.buy
        }

    def _handle_requests(self) -> Any:
        message = self.socket.recv_string()
        req = json.loads(message)
        print("Received request: \n", req)

        if req['method'] in self.methods:
            self.methods[req['method']]()
        else:
            print("unknown method")
            print(message)

    def start(self):
        try:
            while True:
                self._handle_requests()
        except KeyboardInterrupt:  # If user do CTRL+C
            print("Exiting")
            exit(0)

    def buy(self):
        print("buy order:")
        if self.auto_success:
            self._buy(True)
        else:
            choice = input("What to do: (s)uccess (f)ail or (q)uit + Enter\n")
            if choice in ("q", "quit"):
                exit(0)
            else:
                success = choice in ("s", "success")
                self._buy(success)

    def _buy(self, success: bool):
        status = "success" if success else "error"
        response = ResponseBuy(status=status, result=0.2)
        self.socket.send_string(response.json())


if __name__ == '__main__':
    f = argument.Arguments()
    f.switch("success", help="Auto success", abbr="s")
    arguments, errors = f.parse()

    m = MockBackend(arguments["success"])
    m.start()
