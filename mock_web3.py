import zmq
import json
from time import time, sleep
port = '5557'

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:{}'.format(port))

print("Mock web3")

success = False # auto success, use an arg parser to add this as cli option


try:
    while True:
        #  Wait for next request from client
        message = socket.recv().decode('utf-8')
        msg_json = json.loads(message)
        print("Received request: ", message)
        if msg_json['method'] == "buy":
            print("Buy order")
            if success == True:
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
