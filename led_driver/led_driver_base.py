

class LedDriver(object):
    ''' LedDriver abstract class, implements led_on(), led_off()'''
    def __init__(self):
        pass

    def led_on(self):
        raise NotImplementedError()

    def led_off(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()
