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
from typing import Dict, List, Optional, Callable

from pydantic import BaseModel, ValidationError

from src.zmq.subscriber import ZMQSubscriber
from src_backends import config_tools


class Price(BaseModel):
    price: float
    buy_fee: int
    sell_fee: int


Prices = Dict[str, Price]


class PricefeedResponse(BaseModel):
    prices: Dict[str, Price]


PricefeedCallback = Callable[[Prices], None]


class PricefeedSubscriber:
    def __init__(self, c: config_tools.Pricefeed):
        url = f"{c.address}:{c.port_sub}"
        self._callbacks: List[PricefeedCallback] = []
        self._subscriber = ZMQSubscriber(self._update_prices, url, "pricefeed")
        self._last_prices: Optional[Prices] = None

    def _update_prices(self, message):
        """Update prices with newly received message"""
        self._last_prices = self._parse_message(message)

        for callback in self._callbacks:
            callback(self._last_prices)

    @staticmethod
    def _parse_message(message: str) -> Prices:
        """
        Parses message back from pricefeed raw message

        :argument message raw message from pricefeed
        """
        try:
            return PricefeedResponse(**json.loads(message)).prices
        except ValidationError as e:
            print("failed to decode pricefeed response")
            print(e.json())
            raise ValidationError

    def start(self):
        self._subscriber.start()

    def stop(self):
        self._subscriber.stop_listening()

    def get_last_prices(self) -> Prices:
        """Get last known prices"""
        return self._last_prices

    def subscribe(self, callback: PricefeedCallback):
        """Subscribe to the price updates."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
