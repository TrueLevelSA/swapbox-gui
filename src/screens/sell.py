#  Swap-box
#  Copyright (c) 2022 TrueLevel SA
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Optional

from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src.components.buttons import ButtonLight, ButtonDark
from src.components.recycle_view_crypto import TokensRecycleView
from src.components.steps import StepsWidget, TransactionOrder, Action


class NoteButton(ButtonLight):
    def __init__(self, value, callback, **kwargs):
        super(NoteButton, self).__init__(**kwargs)
        self.value = int(value)
        self.callback = callback
        self.text = f"+ {self.value}"

    def on_press(self):
        self.callback(self.value)


class StepsScreen(Screen):
    def __init__(self, **kwargs):
        super(StepsScreen, self).__init__(**kwargs)
        self.steps: StepsWidget = self.ids.steps

    def set_tx_order(self, tx_order: TransactionOrder):
        self.steps.set_tx_order(tx_order)


class ScreenSellAmount(StepsScreen):
    _amount = NumericProperty(0)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._currency = config.note_machine.currency

        self._tx_order = TransactionOrder()
        self._tx_order.action = Action.SELL
        self.set_tx_order(self._tx_order)

        self._create_note_buttons()

    def _create_note_buttons(self):
        """Create the note buttons"""
        for note in self._valid_notes:
            note_button = NoteButton(note, self._add_amount)
            self.ids.grid_notes.add_widget(note_button)

        self.ids.grid_notes.add_widget(ButtonDark(text="clear"))

    def on_enter(self):
        self._CASHOUT.start_cashout()
        self._NOTE_BALANCE = self._CASHOUT.get_balance()
        # success, value = self._node_rpc.buy(self._cash_in, self._address_ether)

    def on_leave(self, *args):
        self._amount = 0

    def button_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"

    def button_confirm(self):
        self.manager.get_screen("sell_select_token").set_tx_order(self._tx_order)
        self.manager.transition.direction = "left"
        self.manager.current = "sell_select_token"

    def _add_amount(self, amount):
        if self._CASHOUT.check_available_notes(self._NOTE_BALANCE, amount):
            self._amount += amount
        else:
            # TODO: tell user cash machine doesn't have a bill
            # Thread(target=self._threaded_buy, daemon=True).start()
            print("NotImplemented: Note not available")


class ScreenSellSelectToken(StepsScreen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        # init recycle view
        self._list_view: TokensRecycleView = self.ids.rv_tokens
        self._list_view.populate(config.backends)

    def button_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "sell_amount"

    def button_confirm(self):
        self.manager.get_screen("sell_scan").set_tx_order(self._tx_order)
        self.manager.transition.direction = "left"
        self.manager.current = "sell_scan"


class ScreenSellScan(StepsScreen):
    _payment_address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _qr_image_uri = ObjectProperty()
    _sell_amount = NumericProperty()

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHOUT = config.CASHOUT_DRIVER
        self._QR_GENERATOR = config.QR_GENERATOR
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC

        self._tx_order: Optional[TransactionOrder] = None

    def on_enter(self):
        # TODO: generate qr code for any target currency
        # request backend for the tx string
        self._qr_image_uri = os.path.join('tmp', 'qr.png')
        self._QR_GENERATOR.generate_qr_image("some address", self._qr_image_uri)

    def set_tx_order(self, tx_order: TransactionOrder):
        self._tx_order = tx_order
