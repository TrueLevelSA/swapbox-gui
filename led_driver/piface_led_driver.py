from led_driver.led_driver_base import LedDriver
import pifacedigitalio

class LedDriverPiFace(LedDriver):
    def __init__(self):
        super().__init__()
        self._pifacedigital = pifacedigitalio.PiFaceDigital()

    def led_on(self):
        self._pifacedigital.output_pins[0].turn_on() # this command does the same thing..
        self._pifacedigital.leds[0].turn_on() # as this command

    def led_off(self):
        self._pifacedigital.output_pins[0].turn_off() # this command does the same thing..
        self._pifacedigital.leds[0].turn_off() # as this command

    def close(self):
        self._pifacedigital.deinit_board()
