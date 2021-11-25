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
import json
from time import time, sleep
import argument

port = '5557'

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:{}'.format(port))

print("Mock web3")


f = argument.Arguments()
#add a switch, a flag with no argument
f.switch("success",
    help="Auto success",
    abbr="s"
)
arguments, errors = f.parse()

success = arguments["success"] # auto success, use an arg parser to add this as cli option


try:
    while True:
        #  Wait for next request from client
        message = socket.recv().decode('utf-8')
        msg_json = json.loads(message)
        print("Received request: ", message)
        if msg_json['method'] == "buy":
            print("Buy order")
            if success == True:
                sleep(0.5)

                response = {'status': "success", 'result': msg_json['min_eth']}
                socket.send_multipart([json.dumps(response).encode('utf-8')])
            else:
            #     response = {'status': "error", 'result': "Unspecified pretend error"}
            #     socket.send_multipart([json.dumps(response).encode('utf-8')])

                choice = input("What to do: (s)uccess (f)ail or (q)uit + Enter\n")
                if choice == "s" or choice == "success":
                    response = {'status': "success", 'result': msg_json['min_eth']}
                    socket.send_multipart([json.dumps(response).encode('utf-8')])
                elif choice == "f" or choice == "fail":
                    response = {'status': "error", 'result': "Unspecified pretend error"}
                    socket.send_multipart([json.dumps(response).encode('utf-8')])
                elif choice == "q" or choice == "quit":  # Exit
                    exit(0)


except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
