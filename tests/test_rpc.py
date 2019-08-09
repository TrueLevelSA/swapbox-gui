import os
import sys
# i hate importes in python
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")
from node_rpc.node_rpc import NodeRPC

def test():
    address = "0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e1"
    amount = 10

    zmq_url = "tcp://localhost:5557"
    node_rpc = NodeRPC(zmq_url)

    print(node_rpc.buy(amount, address))

if __name__ == "__main__":
    test()
