from threading import Thread, Event
import zmq
import json

class ZMQStatus(Thread):

    def __init__(self, callback_message, config):
        super().__init__()
        self.daemon = True
        self._stop_listening = Event()
        self._callback_message = callback_message
        self._zmq_port = config.ZMQ_STATUS

    def run(self):
        """Run Worker Thread."""
        zctx = zmq.Context()
        self.zsock = zctx.socket(zmq.SUB)
        self.zsock.connect(self._zmq_port)
        self.zsock.setsockopt_string(zmq.SUBSCRIBE,'status')

        self._stop_listening.clear()

        while not self._stop_listening.is_set():
            msg = self.zsock.recv_multipart()
            self._callback_message(msg[1].decode('utf-8'))

    def stop_listening(self):
        self._stop_listening.set()
