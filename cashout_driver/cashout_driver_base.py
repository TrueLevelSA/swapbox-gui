from abc import ABC, abstractmethod
from threading import Event, Thread

class CashoutDriver(ABC):
    _MAP_CHANNEL_NOTES = {
        1: 10,
        2: 20,
        3: 50,
        4: 100,
        5: 200,
    }

    @abstractmethod
    def start_cashout(self):
        pass

    @abstractmethod
    def stop_cashout(self):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def do_cashout(self):
        pass

    def check_available_notes(self, balance, amount):
        notes = CashoutDriver._MAP_CHANNEL_NOTES.values()
        note_counter = [0, 0, 0, 0, 0]
        for note, distribute in zip(notes, note_counter):
            if amount >= note:
                c = amount // note
                if c >= balance[note]:
                    distribute = balance[note]
                else:
                    distribute = c
                amount = amount - distribute * note
        if amount == 0:
            return True
        else:
            return False
