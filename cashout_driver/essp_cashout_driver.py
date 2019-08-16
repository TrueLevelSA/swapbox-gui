from cashout_driver.cashout_driver_base import CashoutDriver
import time
from eSSP import eSSP
from eSSP.constants import Status


class EsspCashoutDriver(CashoutDriver):
    _MAP_CHANNEL_NOTES = {
        1: 10,
        2: 20,
        3: 50,
        4: 100,
        5: 200,
    }

    def __init__(self, validator_port):
        self._validator_port= validator_port
        self.validator = None

    def start_cashout(self):
        #  Create a new object ( Validator Object ) and initialize it
        print("Start cashin lol")
        self.validator = eSSP(com_port=self._validator_port, ssp_address="0", nv11=False, debug=True)

    def stop_cashout(self):
        print("Stop cashout")
        self._close_validator()


    def get_balance(self):
        balance = {}
        for note in EsspCashoutDriver._MAP_CHANNEL_NOTES.values():
            balance[note] = self.validator.get_note_amount(int(note))
            time.sleep(0.5)
        return balance

    def do_cashout(self, amount, currency):
        validator.payout(int(amount), currency)

    def _close_validator(self):
        self.validator.close()
