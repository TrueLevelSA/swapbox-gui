from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen


class ScreenSell1(Screen):
    _sell_choice = NumericProperty(0)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._NOTE_BALANCE = {}
        self._valid_notes = config.NOTES_VALUES

    def on_enter(self):
        self._CASHOUT.start_cashout()
        self._NOTE_BALANCE = self._CASHOUT.get_balance()
        # success, value = self._node_rpc.buy(self._cash_in, self._address_ether)

    def _leave_without_sell_select(self):
        # reseting cash out process
        # might use on_pre_leave or on_leave
        self._sell_choice = 0

    def _sell_select(self, amount):
        if self._CASHOUT.check_available_notes(self._NOTE_BALANCE, amount):
            self._sell_choice = amount
            self.manager.transition.direction = 'left'
            self.manager.current = "sell2"

        else:
            # requested amount not available
            print("dosomething")
        # Thread(target=self._threaded_buy, daemon=True).start()


class ScreenSell2(Screen):
    _payment_address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _qr_image = ObjectProperty()

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._QR_GENERATOR = config.QR_GENERATOR
        self._NOTE_BALANCE = {}
        self._valid_notes = config.NOTES_VALUES
        self._node_rpc = config.NODE_RPC

    def on_enter(self):
        self._QR_GENERATOR.generate_qr_image("some address", os.path.join('tmp', 'qr.png'))
        self._qr_image = os.path.join('tmp', 'qr.png')


class ScreenSell3(Screen):
    pass
