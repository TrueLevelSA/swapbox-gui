import os
import sys
# i hate importes in python
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")
from qr_scanner.zbar_qr_scanner import QrScannerZbar

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
