from qr_scanner.qr_scanner_base import QrScanner


class QrScannerZbar(QrScanner):

    def __init__(self, video_port):
        super().__init__()
        self._cmd_txt = 'zbarcam --prescale=640x480 --nodisplay {}'.format(video_port)

    def _cmd(self):
        return self._cmd_txt

    def _is_qr_found(self, line):
        if line != "" and line != None:
            return line.startswith(b"QR-Code:")
        return False

    def _get_qr_from_line(self, line):
        return line[8:]

