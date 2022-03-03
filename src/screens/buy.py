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
from threading import Thread
from typing import Optional

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager

from src.components.recycle_view_crypto import TokensRecycleView
from src.components.steps import TransactionOrder, Action, StepsWidgetBuy
from src.types.tx import TransactionReceipt
from src.zmq.pricefeed_subscriber import Prices
from src_backends.cashin_driver.cashin_driver_base import CashinDriver
from src_backends.config_tools import Config
from src_backends.qr_generator.qr_generator import QRGenerator
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
        self._list_view.populate(config.backends[0].tokens)

        self._app.pricefeed.subscribe(self._update_prices)

    def on_pre_enter(self, *args):
        """
        KV Lifecycle: Before 'enter screen' animation.
        """
        # select first node default
        self.ids.rv_tokens.ids.controller.selected_nodes = [0]

        # init tx order
        self._tx_order = TransactionOrder()
        self._tx_order.action = Action.BUY
        self._tx_order.network = "zkSync"
        steps: StepsWidgetBuy = self.ids.steps
        steps.set_tx_order(self._tx_order)

    def button_confirm(self):
        tp = self._list_view.get_selected_token()
        self._tx_order.token = tp.token

        self.manager.get_screen('buy_scan').set_tx_order(self._tx_order)
        self.manager.transition.direction = 'left'
        self.manager.current = 'buy_scan'

    def button_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order

    def _update_prices(self, prices: Prices):
        self.ids.rv_tokens.update_prices({k: v.price for (k, v) in prices.items()})


class ScreenBuyScan(Screen):
    """
    Screen for scanning user address.
    """

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._qr_scanner = config.QR_SCANNER
        self._led_driver = config.LED_DRIVER
        self._tx_order: Optional[TransactionOrder] = None

    def on_pre_enter(self, *args):
        """
        KV Lifecycle: Before 'enter screen' animation.
        """
        thread = Thread(target=self._start_scan)
        thread.setDaemon(True)
        thread.start()

    def on_leave(self):
        """
        KV Lifecycle: After 'leave screen' animation.
        """
        self._qr_scanner.stop_scan()

    def button_back(self):
        """
        GUI Callback: Left button callback.
        """
        self.manager.transition.direction = 'right'
        self.manager.current = 'buy_select'

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order
        self.ids.steps.set_tx_order(self._tx_order)

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
            self.manager.transition.direction = "right"
            self.manager.current = "menu"


class ScreenBuyInsert(Screen):
    _label_address_to = StringProperty()
    _label_minimum_received = StringProperty()
    _label_max_amount = StringProperty()
    _token_symbol = StringProperty()
    _token_price = NumericProperty(1)

    _total_cash_in = NumericProperty()
    _estimated_crypto_amount = NumericProperty()

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self._app = App.get_running_app()
        self._config = config

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
        """
        KV Lifecycle: Before 'enter screen' animation.
        """
        self._thread_cashin.start_cashin()
        self._app.subscribe_prices(self._update_prices)

    def on_leave(self):
        """
        KV Lifecycle: After 'leave screen' animation.
        """
        self._thread_cashin.stop_cashin()

        self._total_cash_in = 0
        self._label_address_to = '0x0'

        self.ids.button_confirm.text_id = "buy"

    def button_back(self):
        """
        GUI Callback: Left button callback.
        """
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def button_confirm(self):
        """
        GUI Callback: Right button callback.
        """
        self._async_buy()

    def set_tx_order(self, tx_order: TransactionOrder):
        """
        Set screen tx order.

        This should be called from a previous screen when the tx order is ready,
        probably just before the screen transition.

        :param tx_order: Tx order
        :return:
        """
        self._tx_order = tx_order
        self._label_address_to = self._tx_order.to
        self._token_symbol = self._tx_order.token.symbol
        self.ids.steps.set_tx_order(self._tx_order)

    def _update_prices(self, prices: Prices):
        if self._tx_order.token.symbol not in prices.keys():
            print("token price not received")
            return
        token = prices[self._tx_order.token.symbol]
        self._token_price = token.price
        self._update_price_labels()

    def _update_cashin(self, message):
        """
        Callback when the cashin thread sends an update.
        :param message: The cashin thread raw message. Format: <currency>:<amount>
        """
        try:
            cash_in = int(message.split(':')[1])
        except ValueError as e:
            print("failed to parse cashin message", e)
            # cash out whatever happened here ?
            return

        if cash_in in self._valid_notes:
            self._total_cash_in += cash_in
            self._update_price_labels()

            # for this limit to be half effective we must only accept notes smaller than the limit
            if self._total_cash_in >= self._buy_limit:
                self._thread_cashin.stop_cashin()
                self._highlight_max_amount()

    def _highlight_max_amount(self):
        """Highlights the max_amount label (title and value)"""
        self.ids.max_amount_title.color = "red"
        self.ids.max_amount_text.color = "red"

    def _update_price_labels(self):
        self._estimated_crypto_amount = self._total_cash_in / self._token_price
        self._min_buy_amount_wei = self._estimated_crypto_amount * 10 ** self._tx_order.token.decimals

    def _async_buy(self):
        """Sends a buy order to the node RPC, in a thread"""
        # disable confirm button
        button_confirm: Button = self.ids.button_confirm
        button_confirm.disabled = True
        button_confirm.text_id = "please_wait"

        # Stop cash in and start tx
        self._thread_cashin.stop_cashin()
        Thread(target=self._buy, daemon=True).start()

    def _buy(self):
        """Sends a buy order to the node RPC."""
        response = self._node_rpc.buy(
            self._total_cash_in,
            self._tx_order.token.symbol,
            self._min_buy_amount_wei,
            self._label_address_to,
        )

        if self._config.debug:
            print(response)

        if response.status == "success":
            self._tx_order.amount_fiat = self._total_cash_in
            next_screen = self.manager.get_screen("buy_final")
            next_screen.set_tx(self._tx_order, response.receipt)
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
    _inserted_cash = NumericProperty(0.0)
    _crypto_bought = NumericProperty(0.0)
    _token_symbol = StringProperty("")

    _fees_total = NumericProperty(0.0)
    _fee_percent = NumericProperty(0.0)

    _label_address_to = StringProperty('')

    _qr_uri = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self._app = App.get_running_app()
        self._tx_order: Optional[TransactionOrder] = None
        self.receipt: Optional[TransactionReceipt] = None

        self.img_qr: Image = self.ids.img_qr

    def button_confirm(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"

    def on_pre_enter(self, *args):
        pass

    def on_leave(self):
        pass

    def show_details(self):
        view = FeesDetailsModal(self._inserted_cash, self.receipt, size_hint=(0.5, 0.4))
        view.open()

    def set_tx(self, tx_order: TransactionOrder, receipt: TransactionReceipt):
        self._tx_order = tx_order
        self.ids.steps.set_tx_order(self._tx_order)
        self.receipt = receipt

        # tx summary
        self._inserted_cash = tx_order.amount_fiat
        self._crypto_bought = receipt.amount_bought / 10 ** receipt.decimals
        self._token_symbol = tx_order.token.symbol

        # fees summary
        self._fee_percent = receipt.fees.total * 100.0
        self._fees_total = receipt.fees.total * self._inserted_cash

        # last box
        self._label_address_to = self._tx_order.to
        # set qr (FAILS: black image)
        img_uri = os.path.join('tmp', 'tx_url_qr.png')
        QRGenerator.generate_qr_image(receipt.url, img_uri)
        self._qr_uri = img_uri


class FeesDetailsModal(ModalView):
    fee_operator = NumericProperty()
    fee_operator_percent = NumericProperty()
    fee_network = NumericProperty()
    fee_network_percent = NumericProperty()
    fee_lp = NumericProperty()
    fee_lp_percent = NumericProperty()
    fee_total = NumericProperty()
    fee_total_percent = NumericProperty()

    def __init__(self, cash_in: int, tx: TransactionReceipt, **kwargs):
        super().__init__(**kwargs)

        self.fee_operator = tx.fees.operator * cash_in
        self.fee_operator_percent = tx.fees.operator * 100.0
        self.fee_network = tx.fees.network * cash_in
        self.fee_network_percent = tx.fees.network * 100.0
        self.fee_lp = tx.fees.liquidity_provider * cash_in
        self.fee_lp_percent = tx.fees.liquidity_provider * 100.0
        self.fee_total = tx.fees.total * cash_in
        self.fee_total_percent = tx.fees.total * 100.0
