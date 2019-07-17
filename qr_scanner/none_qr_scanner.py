from qr_scanner.qr_scanner_base import QrScanner


class QrScannerNone(QrScanner):

    def __init__(self, video_port):
        super().__init__()
        self._cmd_txt = 'echo nope'

    def _cmd(self):
        return self._cmd_txt

    def _is_qr_found(self, line):
        return True

    def _get_qr_from_line(self, line):
        return None

