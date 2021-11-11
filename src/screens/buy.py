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
from threading import Thread
from typing import Optional

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src_backends import price_tools
from src_backends.cashin_driver.cashin_driver_base import CashinDriver
from src_backends.config_tools import Config
from src_backends.qr_scanner.util import parse_ethereum_address


class TransactionOrder:
    """A transaction order representing what the user want to do.

    It is gradually built screen after screen, until when it's ready and will be sent to the connector.

    Attributes:
        token           The token the user want to buy.
        backend         The backend of the token.
        to              To whom the token will be forwarded while/after the tx.
        amount_fiat_wei The amount of fiat the user cashed in.

    """

    def __init__(self, token: str, backend: str):
        self.token = token
        self.backend = backend
        self.to: str
        self.amount_wei: int


class ScreenBuyScan(Screen):
    _qr_scanner = ObjectProperty(None)
    _tx_order: TransactionOrder

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._qr_scanner = config.QR_SCANNER
        self._led_driver = config.LED_DRIVER

    def on_enter(self):
        thread = Thread(target=self._start_scan)
        thread.setDaemon(True)
        thread.start()

    def on_pre_leave(self):
        self._qr_scanner.stop_scan()

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order

    def _start_scan(self):
        self._led_driver.led_on()
        qr = self._qr_scanner.scan()
        self._led_driver.led_off()
        address = parse_ethereum_address(qr, quiet=True)
        if address is not None:
            self._tx_order.to = address
            self.manager.get_screen('insert_screen').set_tx_order(self._tx_order)
            self.manager.transition.direction = 'left'
            self.manager.current = 'insert_screen'
        else:
            print("QR not found")
            self.manager.transition.direction = 'right'
            self.manager.current = 'menu'


class ScreenBuyInsert(Screen):
    _address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _cash_in = NumericProperty(0)
    _estimated_eth = NumericProperty(0)
    _minimum_wei = NumericProperty(0)

    _tx_order_to = StringProperty('')

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._thread_cashin = ScreenBuyInsert._create_thread_cashin(
            config,
            self._update_message_cashin
        )
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC
        self._buy_limit = config.buy_limit

        self._tx_order: Optional[TransactionOrder] = None

    def on_pre_enter(self):
        self._thread_cashin.start_cashin()

    def on_pre_leave(self):
        self._thread_cashin.stop_cashin()

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order
        self._tx_order_to = tx_order.to

    def _update_message_cashin(self, message):
        amount_received = int(message.split(':')[1])
        if amount_received in self._valid_notes:
            self._cash_in += amount_received
            self._get_eth_price(App.get_running_app())
            # for this limit to be half effective we must only accept notes smaller than the limit
            if self._cash_in >= self._buy_limit:
                self._thread_cashin.stop_cashin()
                self.ids.buy_limit.text = App.get_running_app()._languages[App.get_running_app()._selected_language][
                    "limitreached"]

    def _leave_without_buy(self):
        # reseting cash in, might want to give money back
        # might use on_pre_leave or on_leave
        self._thread_cashin.stop_cashin()
        self._cash_in = 0
        self._minimum_wei = 0
        self._address_ether = '0x0'

    def _get_eth_price(self, app):
        if self._cash_in == 0:
            return 0
        amount_stablecoin = self._cash_in * 1e18
        eth_amount = price_tools.get_buy_price(amount_stablecoin, app._stablecoin_reserve, app._eth_reserve)
        self._estimated_eth = eth_amount
        self._minimum_wei = eth_amount * 0.98
        return eth_amount / 1e18

    def _buy(self):
        self.ids.buy_confirm.text = App.get_running_app()._languages[App.get_running_app()._selected_language][
            "pleasewait"]
        self.ids.buy_confirm.disabled = True
        self._thread_cashin.stop_cashin()
        Thread(target=self._threaded_buy, daemon=True).start()

    def _threaded_buy(self):
        min_eth = self._minimum_wei / 1e18
        print("exact min wei", self._minimum_wei)
        print("min eth", min_eth)
        success, value = self._node_rpc.buy(str(int(1e18 * self._cash_in)), self._address_ether, self._minimum_wei)
        if success:
            self.manager.get_screen("final_buy_screen")._fiat_sold = self._cash_in
            self.manager.get_screen("final_buy_screen")._eth_bought = min_eth
            self.manager.get_screen("final_buy_screen")._address_ether = self._address_ether
            self.ids.buy_confirm.text = App.get_running_app()._languages[App.get_running_app()._selected_language][
                "confirm"]
            self.ids.buy_confirm.disabled = False
            self.ids.buy_limit.text = ""
            self._cash_in = 0
            self._minimum_wei = 0
            self._estimated_eth = 0
            self._address_ether = '0x0'
            self.manager.transition.direction = 'left'
            self.manager.current = "final_buy_screen"
        else:
            self.manager.transition.direction = 'right'
            self.manager.current = "insert_screen"

    @staticmethod
    def _create_thread_cashin(c: Config, callback: ()) -> CashinDriver:
        if c.note_machine.mock.enabled:
            from src_backends.cashin_driver.mock_cashin_driver import MockCashinDriver
            return MockCashinDriver(callback, c.note_machine.mock.zmq_url)
        else:
            from src_backends.cashin_driver.essp_cashin_driver import EsspCashinDriver
            return EsspCashinDriver(callback, c.note_machine.port)


class ScreenBuyFinal(Screen):
    _address_ether = StringProperty('')
    _fiat_sold = NumericProperty(0)
    _eth_bought = NumericProperty(0)

    def on_leave(self):
        self._fiat_sold = 0
        self._eth_bought = 0
        self.address = ''
