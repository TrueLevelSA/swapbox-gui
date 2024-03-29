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

import os
import sys

# i hate importes in python
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from src.qr import QrScannerZbar


# expected output:
# "ethereum:[ADDRESS]"
# i.e.
# "ethereum:0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e1"
def test():
    video_port = '/dev/video0'

    scanner = QrScannerZbar(video_port)

    print("Scan your QR-Code please")
    print(scanner.scan())


if __name__ == "__main__":
    test()
