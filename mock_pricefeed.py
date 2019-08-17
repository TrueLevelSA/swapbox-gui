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

import zmq
import math
from time import time, sleep
import json
port = '5556'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))


value = 100e18
index = 0.1
increment = 0.1/4


def noise_this_number(number, amplitude):
    global index
    global increment
    index += increment
    return number + amplitude * math.sin(index)

obeuhjeuh = {
        'eth_reserve': 20,
        'token_reserve': 100,
}

try:  # Command Interpreter
    while True:
        obeuhjeuh['eth_reserve'] = noise_this_number(1e18, 0.1e18)
        obeuhjeuh['token_reserve'] = noise_this_number(200e18, -10e18)
        print(" Sending {}".format(obeuhjeuh))
        socket.send_multipart(["priceticker".encode('utf-8'), json.dumps(obeuhjeuh).encode('utf-8')])
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
