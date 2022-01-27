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
from typing import Any, List

import zmq
from pydantic import BaseModel
from zmq import Socket


class BaseResponse(BaseModel):
    """
    The base response for backend interactions.

    If the request succeeded, the status should be `"success"` and the wrapping
    response should add relevant attributes. If it failed, the errors list
    should contain at least one error.

    Attributes:
        status  The status of the order
        errors  Potential list of errors
    """
    status: str
    errors: List[str] = []


class ResponseBuy(BaseResponse):
    """
    A Backend response structure after a buy order request.

    Attributes:
        amount_bought   Confirmed bought amount after tx success
        fees            total amount of paid fees
        tx_url          The transaction URL, the gui will generate a QR Code for
                        it. It can be empty if the network doesn't have a block
                        explorer.
    """
    amount_bought: int
    fees_network: int
    fees_operator: int
    fees_liquidity_provider: int
    tx_url: str


class NodeRPC:
    def __init__(self, zmq_url):
        self._zmq_context = zmq.Context()
        self._zmq_socket: Socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(zmq_url)

    def _call(self, method_name: str, **kwargs: Any) -> str:
        order = dict(method=method_name, **kwargs)
        print(order)
        self._zmq_socket.send_json(order)
        return self._zmq_socket.recv_string()

    def stop(self):
        """ closes socket and stuff"""
        self._zmq_socket.close()
        self._zmq_context.destroy()

    def buy(
            self,
            fiat_amount: int,
            token: str,
            minimum_buy_amount: int,
            client_address: str
    ) -> ResponseBuy:
        """
        Sends a buy token order to the backend.

        :param fiat_amount:         Fiat amount user cashed in.
        :param token:               The token name.
        :param minimum_buy_amount:  Under this threshold the order shouldn't
                                    pass.
        :param client_address:      Destination for bought token
        :returns: Backend response
        """
        response_str = self._call(
            'buy',
            token=token,
            fiat_amount=fiat_amount,
            client_address=client_address,
            minimum_buy_amount=minimum_buy_amount
        )
        return ResponseBuy(**json.loads(response_str))

    def sell(self):
        """
        Sends a sell order to the backend

        :return:
        """
        pass
