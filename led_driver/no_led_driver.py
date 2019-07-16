from led_driver.led_driver_base import LedDriver

class LedDriverNone(object):
    def __init__(self):
        super().__init__()

    def led_on(self):
       pass

    def led_off(self):
        pass

    def close(self):
        pass
