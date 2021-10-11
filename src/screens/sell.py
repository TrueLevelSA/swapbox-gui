import os

from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src.components.button_color_down import MediumButton


class NoteButton(MediumButton):
    def __init__(self, value, currency, callback, **kwargs):
        super(NoteButton, self).__init__(**kwargs)
        self.value = int(value)
        self.callback = callback
        self.text = NoteButton._format_currency(value, currency)

    def on_release(self):
        super(NoteButton, self).on_release()
        self.callback(self.value)

    @staticmethod
    def _format_currency(value, currency):
        return "{} {}".format(value, currency)


class ScreenSell1(Screen):
    _sell_choice = NumericProperty(0)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._currency = config.base_currency

        for note in self._valid_notes:
            note_button = NoteButton(note, self._currency, self._sell_select)
            self.ids.grid_notes.add_widget(note_button)

    def on_enter(self):
        self._CASHOUT.start_cashout()
        self._NOTE_BALANCE = self._CASHOUT.get_balance()
        # success, value = self._node_rpc.buy(self._cash_in, self._address_ether)

    def _leave_without_sell_select(self):
        # resetting cash out process
        # might use on_pre_leave or on_leave
        self._sell_choice = 0

    def _sell_select(self, amount):
        if self._CASHOUT.check_available_notes(self._NOTE_BALANCE, amount):
            self._sell_choice = amount
            self.manager.transition.direction = 'left'
            self.manager.current = "sell2"

        else:
            # TODO: tell user cash machine doesn't have a bill
            # Thread(target=self._threaded_buy, daemon=True).start()
            print("NotImplemented: Note not available")


class ScreenSell2(Screen):
    _payment_address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _qr_image = ObjectProperty()

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._QR_GENERATOR = config.QR_GENERATOR
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC

    def on_enter(self):
        self._QR_GENERATOR.generate_qr_image("some address", os.path.join('tmp', 'qr.png'))
        self._qr_image = os.path.join('tmp', 'qr.png')


class ScreenSell3(Screen):
    pass
