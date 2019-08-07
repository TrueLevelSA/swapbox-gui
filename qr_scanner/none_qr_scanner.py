from qr_scanner.qr_scanner_base import QrScanner


class QrScannerNone(QrScanner):

    def __init__(self, video_port):
        super().__init__('echo nope')

    def _is_qr_found(self, line):
        return True

    def _get_qr_from_line(self, line):
        return None

    def _start_locally(self):
        pass

    def _stop_locally(self):
        pass
