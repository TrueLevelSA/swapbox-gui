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
from random import random
from time import time, sleep
port = '5555'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))

currency = "CHF"

try:  # Command Interpreter
    while True:
        choice = input("What to do: (i)nsert (q)uit + Enter\n")
        if choice == "i" or choice == "insert":  # Input "choice" value bill ( 10, 20, 50, 100, etc. )
            choice = input("Amount:\n")
            data = "{}:{}".format(currency, choice)
            #data = {'currency': currency, 'choice': choice}
            print(" Sending {}".format(data))
            socket.send_string(data)

        elif choice == "q" or choice == "quit":  # Exit
            exit(0)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
