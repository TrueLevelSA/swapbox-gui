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
from time import sleep
import json
import argument

port = '5558'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))

current_block = 1000
sync_block = 1000
is_in_sync = False

# change this to false if you want to emulate syncing issues
status_is_sync = True

f = argument.Arguments()
# add a switch, a flag with no argument
f.switch("verbose",
         help="Verbose output",
         abbr="v"
         )
arguments, errors = f.parse()


def get_next_status(current_block, sync_block):
    current_block += 1
    # for testing purposes, 3 out of 5 status messages are in sync
    if current_block % 5 > 1 or status_is_sync:
        return current_block, current_block, True
    else:
        return current_block, sync_block, False


obeuhjeuh = {
    'blockchain': {
        'current_block': current_block,
        'sync_block': sync_block,
        'is_in_sync': is_in_sync,
    },
    'system': {
        'temp': 100,
        'cpu': 50,
    }
}

try:  # Command Interpreter
    while True:
        current_block, sync_block, is_in_sync = get_next_status(current_block, sync_block)
        obeuhjeuh['blockchain']['current_block'] = current_block
        obeuhjeuh['blockchain']['sync_block'] = sync_block
        obeuhjeuh['blockchain']['is_in_sync'] = is_in_sync
        if arguments["verbose"]:
            print(" Sending {}".format(obeuhjeuh))
        socket.send_multipart(["status".encode('utf-8'), json.dumps(obeuhjeuh).encode('utf-8')])
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    # send not in sync
    obeuhjeuh['blockchain']['is_in_sync'] = False
    socket.send_multipart(["status".encode('utf-8'), json.dumps(obeuhjeuh).encode('utf-8')])
    print("cucu")
    print(obeuhjeuh)
    print("Exiting")
    exit(0)
