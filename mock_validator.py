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
        choice = input("What to do: (i)nsert (q)uit + Enter\n")
        if choice == "i" or choice == "insert":  # Input "choice" value bill ( 10, 20, 50, 100, etc. )
            choice = input("Amount:\n")
            data = "{}:{}".format(currency, choice)
            #data = {'currency': currency, 'choice': choice}
            print(" Sending {}".format(data))
            socket.send_string(data)

        elif choice == "q" or choice == "quit":  # Exit
            exit(0)

except KeyboardInterrupt:  # If user do CTRL+C
    print("Exiting")
    exit(0)
