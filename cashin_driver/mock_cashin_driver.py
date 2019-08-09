from cashin_driver.cashin_driver_base import CashinDriver
import zmq

class MockCashinDriver(CashinDriver):

    def __init__(self, callback_message, zmq_mock_url):
        super().__init__(callback_message)
        self._zmq_mock_url = zmq_mock_url

    def _start_cashin(self):
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect(self._zmq_mock_url)
        zsock.setsockopt_string(zmq.SUBSCRIBE, '')

        while not self._stop_cashin.is_set():
            msg = zsock.recv_multipart()
            self._callback_message(msg[0].decode('utf-8'))

        zctx.destroy()

