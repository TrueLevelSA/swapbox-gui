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

port = '5556'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))

value = 100e18
index = 0.1
increment = 0.1 / 4

f = argument.Arguments()
# add a switch, a flag with no argument
f.switch("verbose",
         help="Verbose output",
         abbr="v"
         )
arguments, errors = f.parse()


def noise_this_number(number, amplitude):
    global index
    global increment
    index += increment
    return number + amplitude * math.sin(index)


def noise_this_number_hex(number, amplitude):
    return hex(round(noise_this_number(number, amplitude)))[2:]


pricefeed = {
    'backend': 'zksync',
    'base_currency': 'CHF',
    'prices': {
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

}

try:  # Command Interpreter
    while True:
        for token, price in pricefeed['prices'].items():
            p = price['price']
            pricefeed['prices'][token]['price'] = noise_this_number(p, p / 1000)

        if arguments["verbose"]:
            print(" Sending {}".format(pricefeed))

        socket.send_multipart(["priceticker".encode('utf-8'), json.dumps(pricefeed).encode('utf-8')])
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
