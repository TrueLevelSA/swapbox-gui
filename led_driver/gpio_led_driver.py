from led_driver.led_driver_base import LedDriver
import RPi.GPIO as GPIO
GPIO.cleanup()

class LedDriverGPIO(LedDriver):
    def __init__(self):
        super(LedDriverPiFace, self).__init__()
        self._led_pin = 7
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._led_pin, GPIO.OUT)
        GPIO.output(self._led_pin, GPIO.HIGH)

    def led_on(self):
        GPIO.output(self._led_pin, GPIO.LOW)

    def led_off(self):
        GPIO.output(self._led_pin, GPIO.HIGH)

    def close(self):
        pass
