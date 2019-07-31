import zmq

class NodeRPC():
    def __init__(self, config):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect('tcp://localhost:{}'.format(config.ZMQ_PORT_BUY))
        print("ICH BINE CONNECTEADEUH")

    def stop(self):
        ''' closes socket and stuff'''
        self.zmq_socket.close()
        self.zmq_context.destroy()

    def buy(self, chf_amount, client_address):
        ''' tries to buy some eth using chf
        returns true when the node could buy and send eth to the client
        and false when an error occured '''
        data = {'method': 'buy', 'amount': chf_amount, 'address': client_address}
        print("SENDING", data)
        self.zmq_socket.send_json(data)
        print("RECEIVING")
        message = self.zmq_socket.recv().decode('utf-8')
        print("RECEIVED")
        return message == 'success'
