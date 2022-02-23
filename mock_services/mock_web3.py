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
from pydantic import BaseModel
from zmq import Socket

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.types.tx import Fees, TransactionReceipt
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
            self.methods[req['method']](req)
        else:
            print("unknown method")
            print(message)

    def _send_response(self, message: BaseModel):
        self.socket.send_string(message.json())

    def start(self):
        try:
            while True:
                self._handle_requests()
        except KeyboardInterrupt:  # If user do CTRL+C
            print("Exiting")
            exit(0)

    def buy(self, req):
        print("buy order:")
        if self.auto_success:
            self._buy_success(req)
        else:
            choice = input("What to do: (s)uccess (f)ail or (q)uit + Enter\n")
            if choice in ("q", "quit"):
                exit(0)
            elif choice in ("s", "success"):
                self._buy_success(req)
            else:
                response = ResponseBuy(status="error", errors="this is a failure message")
                self._send_response(response)

    def _buy_success(self, req):
        decimals = 18
        amount_bought = float(req['minimum_buy_amount']) * 1.01
        fiat_amount = req['fiat_amount']
        fees = 0.015
        tx_url = "https://etherscan.io/tx/0xc215b9356db58ce05412439f49a842f8a3abe6c1792ff8f2c3ee425c3501023c"
        response = ResponseBuy(
            status="success",
            receipt=TransactionReceipt(
                decimals=decimals,
                token=req['token'],
                amount_bought=amount_bought,
                fees=Fees(
                    network=fees,
                    operator=fees * 2,
                    liquidity_provider=fees * 3
                ),
                url=tx_url
            )
        )
        self._send_response(response)


if __name__ == '__main__':
    f = argument.Arguments()
    f.switch("success", help="Auto success", abbr="s")
    arguments, errors = f.parse()

    m = MockBackend(arguments["success"])
    m.start()
