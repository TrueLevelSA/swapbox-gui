from qr_scanner.qr_scanner_base import QrScanner


class QrScannerZbar(QrScanner):

    def __init__(self, video_port):
        cmd =  'zbarcam --prescale=960x720 {}'.format(video_port)
        super().__init__(cmd)

    def _is_qr_found(self, line):
        if line != "" and line != None:
            return line.startswith(b"QR-Code:")
        return False

    def _get_qr_from_line(self, line):
        return line[8:]

    def _start_locally(self):
        pass

    def _stop_locally(self):
        pass
