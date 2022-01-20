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
import math
from time import sleep

import argument
import zmq
from zmq import Socket


class MockPricefeed:
    base_url = 'tcp://*'
    port_prices = 5556
    port_rep = 5559
    name = 'mock_pricefeed'

    increment = 0.025

    def __init__(self, verbose: bool):
        context = zmq.Context()

        # prepare sockets
        self.socket_prices: Socket = context.socket(zmq.PUB)
        self.socket_rep: Socket = context.socket(zmq.REP)
        self.socket_prices.bind(f'{self.base_url}:{self.port_prices}')
        self.socket_rep.bind(f'{self.base_url}:{self.port_rep}')

        # base prices then sinus over +- 0.1% of the price
        self.base_prices = {
            'ETH': {
                'price': 4000.0,
                'buy_fee': 120,
                'sell_fee': 120,
            },
            'DAI': {
                'price': 0.9,
                'buy_fee': 110,
                'sell_fee': 110,
            }
        }

        # how much we move over the sinus each time next_price is called
        self.price_i = 0.1

        self.verbose = verbose

    def next_price(self):
        self.price_i += self.increment

        prices = self.base_prices.copy()
        for token, price in self.base_prices.items():
            p = price['price'] + price['price'] / 1000.0 * math.sin(self.price_i)
            prices[token]['price'] = p
        return prices

    def start(self):
        try:  # Command Interpreter
            while True:
                msg = {'prices': self.next_price()}
                if self.verbose:
                    print(json.dumps(msg, indent=2))
                self.socket_prices.send_string(f"pricefeed {json.dumps(msg)}")
                sleep(1)
        except KeyboardInterrupt:  # If user do CTRL+C
            print("Exiting")
            exit(0)


if __name__ == '__main__':
    f = argument.Arguments()
    f.switch("verbose", help="Verbose output", abbr="v")
    arguments, errors = f.parse()

    m = MockPricefeed(arguments["verbose"])
    m.start()
