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

    def buy(self, chf_amount, client_address, minimum_eth):
        ''' tries to buy some eth using chf
        returns true when the node could buy and send eth to the client
        and false when an error occured '''
        data = {'method': 'buy', 'amount': chf_amount, 'address': client_address, 'min_eth': str(minimum_eth)}
        self.zmq_socket.send_json(data)
        message = self.zmq_socket.recv()
        message = json.loads(message)
        if message['status'] == 'success':
            return (True, float(message['result']))
        else:
            return (False, message['result'])
