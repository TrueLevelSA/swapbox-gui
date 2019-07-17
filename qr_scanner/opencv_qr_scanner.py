from qr_scanner.qr_scanner_base import QrScanner


class QrScannerOpenCV(QrScanner):
    # path to the opencv executable
    _PATH_OPENCV = "/home/pi/Prog/zbar-build/a.out"

    def __init__(self):
        super().__init__(QrScannerOpenCV._PATH_OPENCV)

    def _is_qr_found(self, line):
        if line != "" and line != None:
            return line.startswith("decoded QR-Code symbol")
        return False

    def _get_qr_from_line(self, line):
        return line[22:]
