import zmq
import math
from time import time, sleep
port = '5550'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))


value = 100
index = 0.1
increment = 0.1

def get_next_price():
    global index
    global increment
    global value
    index += increment
    return value + math.sin(index) * 10

crypto_fiat = "eth:chf"

try:  # Command Interpreter
    while True:
        data = "{}:{}".format(crypto_fiat, get_next_price())
        print(" Sending {}".format(data))
        socket.send_string(data)
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
