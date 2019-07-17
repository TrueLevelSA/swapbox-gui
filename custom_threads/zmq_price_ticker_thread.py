import zmq
from threading import Thread


class ZmqPriceTickerThread(Thread):
    def __init__(self, callback_message, zmq_port):
        super().__init__()
        self.daemon = True
        self._callback_message = callback_message
        self._zmq_port = zmq_port

    def run(self):
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect('tcp://localhost:{}'.format(self._zmq_port))
        zsock.setsockopt_string(zmq.SUBSCRIBE,'priceticker')

        while True:
            topic, msg = zsock.recv_multipart()
            if self._config.DEBUG:
                Logger.info('   Topic: %s, msg:%s' % (topic, msg))
            self._callback_message(msg)
