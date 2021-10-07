from threading import Thread

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from src_backends import price_tools
from src_backends.qr_scanner.util import parse_ethereum_address


class ScreenBuyScan(Screen):
    _qr_scanner = ObjectProperty(None)

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

    def _start_scan(self):
        self._led_driver.led_on()
        qr = self._qr_scanner.scan()
        self._led_driver.led_off()
        address = parse_ethereum_address(qr, quiet=True)
        if address is not None:
            self.manager.get_screen('insert_screen').set_address(address)
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

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHIN = config.CASHIN_THREAD
        self._valid_notes = config.NOTES_VALUES
        self._node_rpc = config.NODE_RPC
        self._buy_limit = config.BUY_LIMIT

    def on_pre_enter(self):
        t = Thread(target=self._CASHIN.start_cashin(), daemon=True)
        t.start()

    def on_pre_leave(self):
        self._CASHIN.stop_cashin()

    def _update_message_cashin(self, message):
        amount_received = message.split(':')[1]
        if amount_received in self._valid_notes:
            self._cash_in += int(amount_received)
            self._get_eth_price(App.get_running_app())
            # for this limit to be half effective we must only accept notes smaller than the limit
            if self._cash_in >= self._buy_limit:
                self._CASHIN.stop_cashin()
                self.ids.buy_limit.text = App.get_running_app()._languages[App.get_running_app()._selected_language][
                    "limitreached"]

    def set_address(self, address):
        self._address_ether = address

    def _leave_without_buy(self):
        # reseting cash in, might want to give money back
        # might use on_pre_leave or on_leave
        self._CASHIN.stop_cashin()
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
        self._CASHIN.stop_cashin()
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


class ScreenBuyFinal(Screen):
    _address_ether = StringProperty('')
    _fiat_sold = NumericProperty(0)
    _eth_bought = NumericProperty(0)

    def on_leave(self):
        self._fiat_sold = 0
        self._eth_bought = 0
        self.address = ''
