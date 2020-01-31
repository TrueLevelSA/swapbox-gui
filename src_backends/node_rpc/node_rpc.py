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

class NodeRPC():
    def __init__(self, zmq_url):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect(zmq_url)

    def stop(self):
        ''' closes socket and stuff'''
        self.zmq_socket.close()
        self.zmq_context.destroy()

    def buy(self, fiat_amount, client_address, minimum_eth):
        ''' tries to buy some eth using fiat
        returns true when the node could buy and send eth to the client
        and false when an error occured '''
        data = {'method': 'buy', 'amount': fiat_amount, 'address': client_address, 'min_eth': str(int(minimum_eth))}
        self.zmq_socket.send_json(data)
        message = self.zmq_socket.recv()
        message = json.loads(message)
        if message['status'] == 'success':
            return (True, float(message['result']))
        else:
            return (False, message['result'])
