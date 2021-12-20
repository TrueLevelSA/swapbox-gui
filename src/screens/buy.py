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
from enum import Enum
from threading import Thread
from typing import Optional, Dict

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

from src.components.recycle_view_crypto import TokensRecycleView
from src.components.steps import StepsWidget, TransactionOrder, Action
from src.types.pricefeed import Price
from src_backends.cashin_driver.cashin_driver_base import CashinDriver
from src_backends.config_tools import Config
from src_backends.qr_scanner.util import parse_ethereum_address


class ScreenSelectCrypto(Screen):
    """
    Screen for token selection.
    """

    def __init__(self, config: Config, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self.manager: ScreenManager

        self._tx_order: Optional[TransactionOrder] = None

        # init recycle view
        self._list_view: TokensRecycleView = self.ids.rv_tokens
        self._list_view.populate(config.backends)

    # KV screen life cycle hooks
    ################################
    def on_pre_enter(self, *args):
        # select first node default
        self.ids.rv_tokens.ids.controller.selected_nodes = [0]
        self._app.subscribe_prices(self._update_prices)

        # init tx order
        self._tx_order = TransactionOrder()
        self._tx_order.action = Action.BUY
        self._tx_order.backend = "zkSync"
        steps: StepsWidget = self.ids.steps
        steps.set_tx_order(self._tx_order)

    def on_leave(self, *args):
        self._app.unsubscribe_prices(self._update_prices)

    def button_confirm(self):
        token = self._list_view.get_selected_token()
        self._tx_order.token = token

        self.manager.get_screen('buy_scan').set_tx_order(self._tx_order)
        self.manager.transition.direction = 'left'
        self.manager.current = 'buy_scan'

    def button_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order

    def _update_prices(self, prices: Dict[str, Price]):
        self.ids.rv_tokens.update_prices({k: v.price for (k, v) in prices.items()})


class ScreenBuyScan(Screen):
    _qr_scanner = ObjectProperty(None)
    _tx_order: TransactionOrder

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._qr_scanner = config.QR_SCANNER
        self._led_driver = config.LED_DRIVER
        self._tx_order: Optional[TransactionOrder] = None

    def on_pre_enter(self, *args):
        # self.ids.steps.clear()
        self.ids.steps.set_tx_order(self._tx_order)

    def on_enter(self):
        thread = Thread(target=self._start_scan)
        thread.setDaemon(True)
        thread.start()

    def on_pre_leave(self):
        self._qr_scanner.stop_scan()

    def button_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'buy_select'

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order

    def _start_scan(self):
        self._led_driver.led_on()
        qr = self._qr_scanner.scan()
        self._led_driver.led_off()
        address = parse_ethereum_address(qr, quiet=True)
        if address is not None:
            self._tx_order.to = address
            self.manager.get_screen('buy_insert').set_tx_order(self._tx_order)
            self.manager.transition.direction = 'left'
            self.manager.current = 'buy_insert'
        else:
            print("QR not found")
            self._screen_parent.go_to_menu()


class ScreenBuyInsert(Screen):
    _label_address_to = StringProperty("")
    _label_minimum_received = StringProperty("")
    _label_max_amount = StringProperty("")
    _token_symbol = StringProperty("")
    _token_price = NumericProperty(1)

    _inserted_cash = NumericProperty(0)
    _estimated_eth = NumericProperty(0)
    _minimum_wei = NumericProperty(0)

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self._app = App.get_running_app()

        self._thread_cashin = ScreenBuyInsert._create_thread_cashin(
            config,
            self._update_cashin
        )
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC
        self._buy_limit = config.buy_limit
        self._label_max_amount = self._app.format_fiat_price(self._buy_limit)

        self._tx_order: Optional[TransactionOrder] = None
        self._token_price = 1.0

    def on_pre_enter(self):
        """Screen.on_pre_enter()"""
        self._thread_cashin.start_cashin()
        self._app.subscribe_prices(self._update_prices)
        self._label_address_to = self._tx_order.to
        self._token_symbol = self._tx_order.token
        self.ids.steps.set_tx_order(self._tx_order)

    def on_leave(self):
        """Screen.on_leave()"""
        self._thread_cashin.stop_cashin()
        self._app.unsubscribe_prices(self._update_prices)

        self._inserted_cash = 0
        self._minimum_wei = 0
        self._label_address_to = '0x0'

        self.ids.button_confirm.text = self._app.get_string('buy')

    def button_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def button_confirm(self):
        self._async_buy()

    def set_tx_order(self, tx_order: TransactionOrder):
        self._tx_order = tx_order

    def _update_prices(self, prices: Dict[str, Price]):
        if self._tx_order.token not in prices:
            print("token price not received")
            return
        self._token_price = prices[self._tx_order.token].price
        self._update_price_labels()

    def _update_cashin(self, message):
        """
        Callback when the cashin thread sends an update.
        :param message: The cashin thread raw message. Format: <currency>:<amount>
        """
        try:
            amount_received = int(message.split(':')[1])
        except ValueError as e:
            print("failed to parse cashin message", e)
            # cash out whatever happened here ?
            return

        if amount_received in self._valid_notes:
            self._inserted_cash += amount_received
            self._update_price_labels()

            if self._inserted_cash > 0:
                self.ids.button_back.disabled = True
                self.ids.button_confirm.disabled = False

            # for this limit to be half effective we must only accept notes smaller than the limit
            if self._inserted_cash >= self._buy_limit:
                self._thread_cashin.stop_cashin()
                self._highlight_max_amount()

    def _highlight_max_amount(self):
        """Highlights the max_amount label (title and value)"""
        self.ids.max_amount_title.color = "red"
        self.ids.max_amount_text.color = "red"

    def _update_price_labels(self):
        self._estimated_eth = self._inserted_cash / self._token_price

    def _async_buy(self):
        """Sends a buy order to the node RPC, in a thread"""
        button_confirm: Button = self.ids.button_confirm
        button_confirm.disabled = True
        button_confirm.text = self._app.get_string("please_wait")

        # Stop cash in and start tx
        self._thread_cashin.stop_cashin()
        Thread(target=self._buy, daemon=True).start()

    def _buy(self):
        """Sends a buy order to the node RPC."""
        min_eth = self._minimum_wei / 1e18
        print("exact min wei", self._minimum_wei)
        print("min eth", min_eth)
        success, value = self._node_rpc.buy(str(int(1e18 * self._inserted_cash)), self._label_address_to,
                                            self._minimum_wei)
        print(success, value)
        if success:
            self._tx_order.amount_fiat = self._inserted_cash
            self._tx_order.amount_crypto = value
            self.manager.get_screen("buy_final").set_tx_order(self._tx_order)
            self.manager.transition.direction = 'left'
            self.manager.current = "buy_final"
        else:
            # TODO: handle failure better than this ?
            self.manager.transition.direction = 'right'
            self.manager.current = "cash_in"

    @staticmethod
    def _create_thread_cashin(c: Config, callback: ()) -> CashinDriver:
        if c.note_machine.mock.enabled:
            from src_backends.cashin_driver.mock_cashin_driver import MockCashinDriver
            return MockCashinDriver(callback, c.note_machine.mock.zmq_url)
        else:
            from src_backends.cashin_driver.essp_cashin_driver import EsspCashinDriver
            return EsspCashinDriver(callback, c.note_machine.port)


class ScreenBuyFinal(Screen):
    _label_address_to = StringProperty('')

    _inserted_cash = NumericProperty(0.0)
    _crypto_bought = NumericProperty(0.0)
    _token_symbol = StringProperty("")

    # TODO: Real fees
    _operator_fee_percent = NumericProperty(0.5)
    _network_fee_percent = NumericProperty(0.3)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._app = App.get_running_app()

        self._tx_order: Optional[TransactionOrder] = None

    def button_confirm(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"

    def on_pre_enter(self, *args):
        # TODO: Print
        pass

    def on_leave(self):
        pass

    def set_tx_order(self, tx_order: TransactionOrder):
        self._tx_order = tx_order
        self.ids.steps.set_tx_order(self._tx_order)
        self._label_address_to = self._tx_order.to
        self._inserted_cash = self._tx_order.amount_fiat
        self._token_symbol = self._tx_order.token
        self._crypto_bought = self._tx_order.amount_crypto
