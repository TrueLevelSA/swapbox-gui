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
from src.types.pricefeed import Price
from src_backends.cashin_driver.cashin_driver_base import CashinDriver
from src_backends.config_tools import Config
from src_backends.qr_scanner.util import parse_ethereum_address


class Action(Enum):
    BUY = 0
    SELL = 1


class Wallet(Enum):
    PAPER = 0
    HOT = 1


class TransactionOrder:
    """A transaction order representing what the user want to do.

    It is gradually built screen after screen, until when it's ready and will be sent to the connector.

    Attributes:
        action          The type of order, buy or sell.
        token           The token the user want to buy.
        backend         The backend of the token.
        to              To whom the token will be forwarded while/after the tx.
        amount_fiat     The amount of fiat the user cashed in.
        amount_crypto   The amount of crypto the user has received.
        wallet_type     The type of the wallet.
    """

    def __init__(self):
        self.action: Optional[Action] = None
        self.token: Optional[str] = ""
        self.backend: str = ""
        self.to: Optional[str] = None
        self.amount_fiat: Optional[int] = None
        self.amount_crypto: Optional[int] = None
        self.wallet_type: Optional[Wallet] = None


class ScreenBuyI(Screen):
    def title(self):
        """Return the title of the current screen, it will be displayed at the top."""
        pass

    def back(self):
        """Called when user clicks on the back button"""
        pass

    def confirm(self):
        """Called when user clicks on the confirm button"""
        pass


class ScreenBuy(Screen):
    _title = StringProperty("")

    _step_action = StringProperty("")
    _step_network = StringProperty("")
    _step_currency = StringProperty("")
    _step_wallet = StringProperty("")
    _step_amount = StringProperty("")

    # remembers IDs for translations
    _id_title: str
    _id_confirm: str
    _id_back: str

    def __init__(self, config: Config, **kw):
        super(ScreenBuy, self).__init__(**kw)

        self._app = App.get_running_app()

        # Child screens
        sm: ScreenManager = self.ids.sm_buy
        sm.add_widget(ScreenSelectCrypto(self, config, name="select_token"))
        sm.add_widget(ScreenBuyScan(self, config, name="scan"))
        sm.add_widget(ScreenBuyInsert(self, config, name="cash_in"))
        sm.add_widget(ScreenBuyFinal(self, name="final"))
        self._sm_buy = sm

        # Prepare tx order
        self._tx_order = TransactionOrder()
        self.set_tx_action(Action.BUY)

    def on_pre_enter(self, *args):
        self.ids.button_back.text = self._app._languages[self._app._selected_language]["menu"]

        self._sm_buy.current = "select_token"

        # manual firing of KV events, KV 'forgot' to call event on the sub screens ¯\_(ツ)_/¯
        self._sm_buy.current_screen.on_pre_enter()

    def on_leave(self, *args):
        self._clear_steps()

        # manual firing of KV events, KV 'forgot' to call event on the sub screens ¯\_(ツ)_/¯
        self._sm_buy.current_screen.on_leave()

    def change_language(self):
        self.set_string_title(self._id_title)
        self.set_string_confirm(self._id_confirm)
        self.set_string_back(self._id_back)

    def set_string_title(self, string_id: str):
        """Set main buy screen's title"""
        self._id_title = string_id
        self._title = self._app.get_string(string_id)

    def set_string_back(self, string_id: str):
        """Set main buy screen's back button"""
        self._id_back = string_id
        self.ids.button_back.text = self._app.get_string(string_id)

    def set_string_confirm(self, string_id: str):
        """Set main buy screen's confirm button"""
        self._id_confirm = string_id
        self.ids.button_confirm.text = self._app.get_string(string_id)

    def set_tx_action(self, action: Action):
        self._tx_order.action = action
        self._update_steps()

    def set_tx_network(self, backend: str):
        self._tx_order.backend = backend
        self._update_steps()

    def set_tx_token(self, token: str):
        self._tx_order.token = token
        self._update_steps()

    def set_tx_address(self, to: str):
        self._tx_order.to = to
        self._update_steps()

    def set_tx_amount(self, amount: int):
        self._tx_order.amount_fiat = amount
        self._update_steps()

    def _update_steps(self):
        o = self._tx_order

        if o.action:
            self._step_action = o.action.name
        if o.wallet_type:
            self._step_wallet = o.wallet_type.name
        if o.backend:
            self._step_network = o.backend
        if o.token:
            self._step_currency = o.token
        if o.amount_fiat:
            self._step_amount = self._app.format_fiat_price(o.amount_fiat)

    def _clear_steps(self):
        self._tx_order = TransactionOrder()

        self._step_action = ""
        self._step_network = ""
        self._step_currency = ""
        self._step_wallet = ""
        self._step_amount = ""

    def get_tx_order(self):
        return self._tx_order

    def go_to_menu(self):
        """Cancel everything and goes back to the main menu"""
        self.manager.transition.direction = 'right'
        self.manager.current = "menu"

    def button_back(self):
        """Button back (left) calls current screen `back()` method"""
        current: ScreenBuyI = self.ids.sm_buy.current_screen
        current.back()

    def button_confirm(self):
        """Button confirm (right) calls current screen `confirm()` method"""
        current: ScreenBuyI = self.ids.sm_buy.current_screen
        current.confirm()

    def disable_back(self, disable=True):
        self.ids.button_back.set_disabled(disable)

    def disable_confirm(self, disable=True):
        self.ids.button_confirm.set_disabled(disable)



class ScreenSelectCrypto(ScreenBuyI):
    """
    Screen for token selection.
    """

    def __init__(self, screen_parent: ScreenBuy, config: Config, **kw):
        super().__init__(**kw)

        self._app = App.get_running_app()
        self._screen_parent: ScreenBuy = screen_parent

        # init recycle view
        self._list_view: TokensRecycleView = self.ids.rv_tokens
        self._list_view.populate(config.backends)
        self._list_view.set_callback_update_focus(self._rv_focus_update)

    def on_pre_enter(self, *args):
        self._screen_parent.set_string_title('select_currency')
        self._screen_parent.disable_confirm()
        self._app.subscribe_prices(self._update_prices)

    def on_leave(self, *args):
        self._app.unsubscribe_prices(self._update_prices)
        self._list_view.deselect()

    def _rv_focus_update(self):
        self._screen_parent.disable_confirm(False)

    def _update_prices(self, prices: Dict[str, Price]):
        self.ids.rv_tokens.update_prices({k: v.price for (k, v) in prices.items()})

    def confirm(self):
        """ScreenBuyI.confirm()"""
        token, backend = self._list_view.get_selected_token()
        self._screen_parent.set_tx_token(token)
        self._screen_parent.set_tx_network(backend)

        self.manager.transition.direction = 'left'
        self.manager.current = 'scan'

    def back(self):
        """ScreenBuyI.back()"""
        self._screen_parent.go_to_menu()


class ScreenBuyScan(Screen):
    _qr_scanner = ObjectProperty(None)
    _tx_order: TransactionOrder

    def __init__(self, screen_parent: ScreenBuy, config, **kwargs):
        super().__init__(**kwargs)
        self._screen_parent = screen_parent
        self._qr_scanner = config.QR_SCANNER
        self._led_driver = config.LED_DRIVER

    def on_pre_enter(self, *args):
        self._screen_parent.disable_confirm()

    def on_enter(self):
        thread = Thread(target=self._start_scan)
        thread.setDaemon(True)
        thread.start()

    def on_pre_leave(self):
        self._qr_scanner.stop_scan()

    def back(self):
        self._screen_parent.go_to_menu()

    def set_tx_order(self, tx_order):
        self._tx_order = tx_order

    def _start_scan(self):
        self._led_driver.led_on()
        qr = self._qr_scanner.scan()
        self._led_driver.led_off()
        address = parse_ethereum_address(qr, quiet=True)
        if address is not None:
            self._screen_parent.set_tx_address(address)
            self.manager.transition.direction = 'left'
            self.manager.current = 'cash_in'
        else:
            print("QR not found")
            self._screen_parent.go_to_menu()


class ScreenBuyInsert(ScreenBuyI):
    _address_ether = StringProperty("")

    _cash_in = NumericProperty(0)
    _estimated_eth = NumericProperty(0)
    _minimum_wei = NumericProperty(0)

    def __init__(self, screen_parent: ScreenBuy, config, **kwargs):
        super().__init__(**kwargs)
        self._app = App.get_running_app()
        self._screen_parent = screen_parent

        self._thread_cashin = ScreenBuyInsert._create_thread_cashin(
            config,
            self._update_cashin
        )
        self._valid_notes = config.notes_values
        self._node_rpc = config.NODE_RPC
        self._buy_limit = config.buy_limit

        self._tx_order: Optional[TransactionOrder] = None
        self._token_price = 1.0

    def on_pre_enter(self):
        """Screen.on_pre_enter()"""
        self._thread_cashin.start_cashin()
        self._app.subscribe_prices(self._update_prices)
        self._screen_parent.set_string_title("inputfiat")
        self._address_ether = self._screen_parent.get_tx_order().to

    def on_leave(self):
        """Screen.on_leave()"""
        self._thread_cashin.stop_cashin()
        self._app.unsubscribe_prices(self._update_prices)

        self._cash_in = 0
        self._minimum_wei = 0
        self._address_ether = '0x0'

    def back(self):
        """ScreenBuyI.back()"""
        self._screen_parent.go_to_menu()

    def confirm(self):
        """ScreenBuyI.confirm()"""
        self._async_buy()

    def _update_prices(self, prices: Dict[str, Price]):
        token = self._screen_parent.get_tx_order().token
        if token not in prices:
            print("token price not received")
            return
        self._token_price = prices[token].price
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
            self._cash_in += amount_received
            self._update_price_labels()

            if self._cash_in > 0:
                self._screen_parent.disable_confirm(False)

            # for this limit to be half effective we must only accept notes smaller than the limit
            if self._cash_in >= self._buy_limit:
                self._thread_cashin.stop_cashin()
                self.ids.buy_limit.text = self._app.get_string("limitreached")

    def _update_price_labels(self):
        self._estimated_eth = self._cash_in / self._token_price

    def _async_buy(self):
        """Sends a buy order to the node RPC, in a thread"""
        button_confirm: Button = self._screen_parent.ids.button_confirm
        button_confirm.text = self._app.get_string("pleasewait")
        button_confirm.set_disabled(True)

        # Stop cash in and start tx
        self._thread_cashin.stop_cashin()
        Thread(target=self._buy, daemon=True).start()

    def _buy(self):
        """Sends a buy order to the node RPC."""
        min_eth = self._minimum_wei / 1e18
        print("exact min wei", self._minimum_wei)
        print("min eth", min_eth)
        success, value = self._node_rpc.buy(str(int(1e18 * self._cash_in)), self._address_ether, self._minimum_wei)
        print(success, value)
        if success:

            # self.manager.get_screen("final_buy_screen")._fiat_sold = self._cash_in
            # self.manager.get_screen("final_buy_screen")._eth_bought = min_eth
            # self.manager.get_screen("final_buy_screen")._address_ether = self._address_ether

            self._screen_parent.set_string_confirm('confirm')
            self._screen_parent.disable_confirm(False)
            self._screen_parent.set_tx_amount(self._cash_in)
            self.ids.buy_limit.text = ""

            self.manager.transition.direction = 'left'
            self.manager.current = "final"
        else:
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


class ScreenBuyFinal(ScreenBuyI):
    _address_ether = StringProperty('')
    _text_cash_in = StringProperty('')
    _crypto_bought = StringProperty('')
    _crypto_value_fiat = StringProperty('')
    _operator_fee_fiat = StringProperty('0.04')

    def __init__(self, screen_parent: ScreenBuy, **kw):
        super().__init__(**kw)
        self._screen_parent = screen_parent
        self._app = App.get_running_app()

    def confirm(self):
        self._screen_parent.go_to_menu()

    def on_pre_enter(self, *args):
        self._screen_parent.set_string_title("thank")
        self._screen_parent.set_string_confirm("thank")

        tx = self._screen_parent.get_tx_order()
        self._address_ether = tx.to
        self._text_cash_in = self._app.format_fiat_price(tx.amount_fiat)
        self._crypto_bought = self._app.format_crypto_price(tx.amount_crypto, tx.token)
        crypto_value_fiat = tx.amount_crypto
        self._crypto_value_fiat = "..."

        # TODO: Print
        self._screen_parent.set_string_back('print_receipt')
        self._screen_parent.disable_back()

    def on_leave(self):
        self._fiat_sold = 0
        self._eth_bought = 0
        self._address_ether = ''
