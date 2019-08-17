# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        self._overlay_auto_on = False
        self._stop_locally()

    def _is_qr_found(self, line):
        if line != "" and line != None:
            return line.startswith(b'decoded QR-Code symbol')
        return False

    def _get_qr_from_line(self, line):
        return line[22:]

    def _hide_overlay(self):
        subprocess.call("v4l2-ctl --overlay 0".split(" "))

    def _show_overlay(self):
        subprocess.call("v4l2-ctl --overlay 1".split(" "))

    def _start_locally(self):
        self._overlay_auto_on = True
        self._show_overlay()

    def _stop_locally(self):
        self._overlay_auto_on = False
        self._hide_overlay()
