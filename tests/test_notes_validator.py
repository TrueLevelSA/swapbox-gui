import os
import sys
# i hate importes in python
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")
from cashin_driver.essp_cashin_driver import EsspCashinDriver

import time

def test():

    validator_port = '/dev/ttyUSB0'

    driver = EsspCashinDriver(print, validator_port)

    try:
        driver.start_cashin()
        input("Enter or ^C to quit\n")
        driver.stop_cashin()
    except KeyboardInterrupt:
        driver.stop_cashin()

    time.sleep(5)

if __name__ == "__main__":
    test()
