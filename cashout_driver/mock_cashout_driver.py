from cashout_driver.cashout_driver_base import CashoutDriver

class MockCashoutDriver(CashoutDriver):

    def start_cashout(self):
        pass

    def stop_cashout(self):
        pass

    def get_balance(self, denomination):
        return 1

    def do_cashout(self, amount, currency="CHF"):
        print("Cashout: {} {}".format(amount, currency))
