from cashout_driver.cashout_driver_base import CashoutDriver
import time

class MockCashoutDriver(CashoutDriver):

    def start_cashout(self):
        pass

    def stop_cashout(self):
        pass

    def get_balance(self):
        balance = {}
        for note in CashoutDriver._MAP_CHANNEL_NOTES.values():
            balance[note] = 1
            time.sleep(0.5)
        return balance

    def do_cashout(self, amount, currency="CHF"):
        print("Cashout: {} {}".format(amount, currency))
