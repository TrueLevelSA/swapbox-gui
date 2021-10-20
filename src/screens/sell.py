# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src.components.button_color_down import MediumButton


class NoteButton(MediumButton):
    def __init__(self, value, currency, callback, **kwargs):
        super(NoteButton, self).__init__(**kwargs)
        self.value = int(value)
        self.callback = callback
        self.text = NoteButton._format_currency(value, currency)

    def on_press(self):
        self.callback(self.value)
        self.focus()

    def on_release(self):
        # remove unselect effect
        pass

    @staticmethod
    def _format_currency(value, currency):
        return "{} {}".format(value, currency)


class ScreenSell1(Screen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._currency = config.base_currency
        self._sell_choice = None

        # keep ref of buttons in order to unselect them
        self._banknote_buttons = {}

        for note in self._valid_notes:
            note_button = NoteButton(note, self._currency, self._sell_select)
            self._banknote_buttons[note] = note_button
            self.ids.grid_notes.add_widget(note_button)

    def on_enter(self):
        self._CASHOUT.start_cashout()
        self._NOTE_BALANCE = self._CASHOUT.get_balance()
        # success, value = self._node_rpc.buy(self._cash_in, self._address_ether)

    def _unselect_active(self):
        if self._sell_choice:
            self._banknote_buttons[self._sell_choice].unfocus()

    def on_leave(self, *args):
        # reset cash out process
        self._unselect_active()
        self._sell_choice = None

    def _sell_select(self, amount):
        self._unselect_active()

        if self._CASHOUT.check_available_notes(self._NOTE_BALANCE, amount):
            self._sell_choice = amount

        else:
            # TODO: tell user cash machine doesn't have a bill
            # Thread(target=self._threaded_buy, daemon=True).start()
            print("NotImplemented: Note not available")

    def _buy(self):
        if self._sell_choice:
            self.manager.get_screen("sell2").set_sell_amount(self._sell_choice)
            self.manager.transition.direction = 'left'
            self.manager.current = "sell2"


class ScreenSell2(Screen):
    _payment_address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _qr_image = ObjectProperty()
    _sell_amount = NumericProperty()

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._QR_GENERATOR = config.QR_GENERATOR
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC

    def on_enter(self):
        # TODO: generate qr code for any target currency
        self._QR_GENERATOR.generate_qr_image("some address", os.path.join('tmp', 'qr.png'))
        self._qr_image = os.path.join('tmp', 'qr.png')

    def set_sell_amount(self, amount):
        self._sell_amount = amount


class ScreenSell3(Screen):
    pass
