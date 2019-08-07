from qr_scanner.qr_scanner_base import QrScanner
import subprocess
from pathlib import Path

class QrScannerOpenCV(QrScanner):
    # path to the opencv executable
    _PATH_OPENCV = str(Path(__file__).absolute().parent) + "/zbar_c/main.run"
    _CMD_OVERLAY = "v4l2-ctl --set-fmt-overlay top={},left={},width={},height={}".format(
        180, # top
        615, # left
        508, # width
        310, # height
        )

    def __init__(self):
        super().__init__(QrScannerOpenCV._PATH_OPENCV)
        subprocess.call(QrScannerOpenCV._CMD_OVERLAY.split(" "))

    def _is_qr_found(self, line):
        if line != "" and line != None:
            return line.startswith(b'decoded QR-Code symbol')
        return False

    def _get_qr_from_line(self, line):
        return line[22:]

    def _start_locally(self):
        subprocess.call("v4l2-ctl --overlay 1".split(" "))

    def _stop_locally(self):
        subprocess.call("v4l2-ctl --overlay 0".split(" "))
