from threading import Thread, Event
import zmq

class CashInThreadMock(Thread):

    def __init__(self, callback_message, config):
        super().__init__()
        self.daemon = True
        self._stop_cashin = Event()
        self._callback_message = callback_message
        self._mock_port = config.MOCKPORT

    def run(self):
        """Run Worker Thread."""
        zctx = zmq.Context()
        self.zsock = zctx.socket(zmq.SUB)
        self.zsock.connect('tcp://localhost:{}'.format(self._mock_port))
        self.zsock.setsockopt_string(zmq.SUBSCRIBE,'')

        self._stop_cashin.clear()

        while not self._stop_cashin.is_set():
            msg = self.zsock.recv_multipart()
            self._callback_message(msg[0])

    def stop_cashin(self):
        self._stop_cashin.set()
