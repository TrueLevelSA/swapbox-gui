import zmq
import math
from time import time, sleep
import json
port = '5558'

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:{}'.format(port))


current_block = 1000
sync_block = 1000
is_in_sync = True

def get_next_status(current_block, sync_block):
    current_block += 1
    # for testing purposes, 3 out of 5 status messages are in sync
    if current_block % 5 > 1:
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
        print(" Sending {}".format(obeuhjeuh))
        socket.send_multipart(["status".encode('utf-8'), json.dumps(obeuhjeuh).encode('utf-8')])
        sleep(1)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
