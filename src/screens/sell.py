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
import threading
from typing import Optional, Dict

from kivy import Logger
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src.components.buttons import ButtonLight, ButtonDark
from src.components.recycle_view_crypto import TokensRecycleView
from src.components.steps import StepsWidgetSell, TransactionOrder, Action
from src.zmq.pricefeed_subscriber import Prices
from src_backends.config_tools import Config
from src_backends.qr_generator.qr_generator import QRGenerator


class NoteButton(ButtonLight):
    def __init__(self, value, callback, **kwargs):
        super(NoteButton, self).__init__(**kwargs)
        self.value = int(value)
        self.callback = callback
        self.text = f"+ {self.value}"

    def on_press(self):
        self.callback(self.value)


class StepsScreen(Screen):
    """Base class for screens that uses a StepsWidget.

    A StepsWidget must exist in the screen layout with `id: steps`
    """
    _tx_order: Optional[TransactionOrder] = None

    def __init__(self, **kwargs):
        super(StepsScreen, self).__init__(**kwargs)
        self.steps: StepsWidgetSell = self.ids.steps

    def set_tx_order(self, tx_order: TransactionOrder):
        self._tx_order = tx_order
        self.steps.set_tx_order(tx_order)


class ScreenSellAmount(StepsScreen):
    """Screen in the sell process to choose the amount to withdraw."""

    _amount = NumericProperty(0)
    _label_max_amount = StringProperty("")

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._app = App.get_running_app()

        self._CASHOUT = config.CASHOUT_DRIVER
        self._valid_notes = config.notes_values
        self._currency = config.note_machine.currency
        self._buy_limit = config.buy_limit
        self._label_max_amount = self._app.format_fiat_price(self._buy_limit)

        self._note_balance = {}
        self._reset()

    def on_pre_enter(self):
        self.set_tx_order(self._tx_order)

        t = threading.Thread(target=self._create_note_buttons, daemon=True)
        t.start()
        self._CASHOUT.start_cashout()
        # success, value = self._node_rpc.buy(self._cash_in, self._address_ether)

    def on_leave(self, *args):
        self._reset()

    def button_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"

    def button_confirm(self):
        self._tx_order.amount_fiat = self._amount
        self.manager.get_screen("sell_select_token").set_tx_order(self._tx_order)
        self.manager.transition.direction = "left"
        self.manager.current = "sell_select_token"

    def _create_note_buttons(self):
        """Create the note buttons.

        This can take some time, it will lock the UI and unlock it when ready.
        You'd rather call that in a non-blocking thread.
        """
        self.ids.grid_notes.clear_widgets()
        self.ids.grid_notes.add_widget(ButtonDark(text_id="loading", disabled=True))

        self._note_balance = self._retrieve_note_balance()
        self.ids.grid_notes.clear_widgets()

        for note in self._valid_notes:
            note_button = NoteButton(note, self._add_amount)
            self.ids.grid_notes.add_widget(note_button)

        self.ids.grid_notes.add_widget(
            ButtonDark(text="clear", on_release=lambda _: self._reset())
        )

    def _retrieve_note_balance(self) -> Dict[int, int]:
        return self._CASHOUT.get_balance()

    def _reset(self):
        """Resets screen to be ready for next use."""
        self._amount = 0
        self._tx_order = TransactionOrder(action=Action.SELL)

    def _add_amount(self, amount):
        """Adds amount chose by the user to internal count."""
        if self._CASHOUT.check_available_notes(self._note_balance, amount):
            if self._amount + amount <= self._buy_limit:
                self._amount += amount
            else:
                self.ids.max_amount_title.color = "red"
                self.ids.max_amount_text.color = "red"
        else:
            # TODO: tell user cash machine doesn't have a bill
            # Thread(target=self._threaded_buy, daemon=True).start()
            print("NotImplemented: Note not available")


class ScreenSellSelectToken(StepsScreen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)

        self._app = App.get_running_app()

        self._tx_order: Optional[TransactionOrder] = None

        # init recycle view
        self._list_view: TokensRecycleView = self.ids.rv_tokens
        self._list_view.populate(config.backends[0].tokens)

    def on_pre_enter(self, *args):
        self._app.subscribe_prices(self._update_prices)

    def button_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "sell_amount"

    def button_confirm(self):
        tp = self._list_view.get_selected_token()
        self._tx_order.network = "zkSync"
        self._tx_order.token = tp.token
        self._tx_order.amount_crypto = self._tx_order.amount_fiat / tp.price
        self.manager.get_screen("sell_scan").set_tx_order(self._tx_order)
        self.manager.transition.direction = "left"
        self.manager.current = "sell_scan"

    def _update_prices(self, prices: Prices):
        self._list_view.update_prices({k: v.price for (k, v) in prices.items()})


class ScreenSellScan(StepsScreen):
    _payment_address_ether = StringProperty("")
    _qr_image_uri = ObjectProperty()

    _sell_amount = NumericProperty()
    _token = StringProperty()

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)

        self._CASHOUT = config.CASHOUT_DRIVER
        self._NOTE_BALANCE = {}
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC

        self._backends = config.backends

        self._tx_order: Optional[TransactionOrder] = None

    def on_pre_enter(self):
        self._payment_address_ether = self._get_backend_address()
        # TODO: generate qr code for any target currency
        img_uri = os.path.join('tmp', 'qr.png')
        QRGenerator.generate_qr_image(self._payment_address_ether, img_uri)
        self._qr_image_uri = img_uri

    def button_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "sell_select_token"

    def set_tx_order(self, tx_order: TransactionOrder):
        super(ScreenSellScan, self).set_tx_order(tx_order)
        self._sell_amount = tx_order.amount_crypto
        self._token = tx_order.token.symbol

    def _get_backend_address(self):
        for backend in self._backends:
            if backend.type == self._tx_order.network:
                return backend.address
        Logger.error(f"swapbox: no backend address for: {self._tx_order.network}")
