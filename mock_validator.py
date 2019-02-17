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
        choice = input("")
        if choice == "i":  # Input "choice" value bill ( 10, 20, 50, 100, etc. )
            choice = input("")
            data = "{}:{}".format(currency, choice)
            #data = {'currency': currency, 'choice': choice}
            print(" Sending {}".format(data))
            socket.send_string(data)

        elif choice == "q":  # Exit
            exit(0)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
