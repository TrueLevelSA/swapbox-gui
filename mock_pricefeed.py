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
increment = 0.1

def get_next_price():
    global index
    global increment
    global value
    index += increment
    return value + math.sin(index) * 10e18


obeuhjeuh = {
        'buy_price': -1.0,
        'sell_price': -2.0
}

try:  # Command Interpreter
    while True:
        data = "{}:{}".format(crypto_fiat, get_next_price())
        obeuhjeuh['buy_price'] = get_next_price()
        obeuhjeuh['sell_price'] = get_next_price()
        print(" Sending {}".format(obeuhjeuh))
        socket.send_multipart(["priceticker".encode('utf-8'), json.dumps(obeuhjeuh).encode('utf-8')])
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
