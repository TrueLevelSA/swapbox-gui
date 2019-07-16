from abc import ABC, abstractmethod

class LedDriver(ABC):
    ''' LedDriver abstract class, implements led_on(), led_off()'''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def led_on(self):
        pass

    @abstractmethod
    def led_off(self):
        pass

    @abstractmethod
    def close(self):
        pass
