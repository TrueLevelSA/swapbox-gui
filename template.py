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

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
import strictyaml
from path import Path
from threading import Thread, Lock
import json
import os

from config_tools import parse_args as parse_args
from config_tools import Config as ConfigApp
import price_tools
from qr_scanner.util import parse_ethereum_address


class ColorDownButton(Button):
    """
    Button with a possibility to change the color on on_press
    (similar to background_down in normal Button widget)
    """
    background_color_normal = ListProperty([0, 0, 0, 0.4])
    background_color_down = ListProperty([0, 0, 0, 0.6])

    def __init__(self, **kwargs):
        super(ColorDownButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal

    def on_press(self):
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal


class ButtonLanguage(Button):
    _language = StringProperty(None)

    def __init__(self, language, callback=None, **kwargs):
        self._language = language
        self._callback =  callback
        #self.text = language
        self.background_down = 'assets/img/flags/medium/' + language + '.png'
        self.background_normal = self.background_down
        super().__init__(**kwargs)

    def on_press(self):
        App.get_running_app().change_language(self._language)
        if self._callback is not None:
            self._callback()

class LanguageBar(BoxLayout):
    spacing = 10
    def __init__(self, **kwargs):
        super(LanguageBar, self).__init__(**kwargs)
        self.add_widgets()

    def add_widgets(self, *args, **kwargs):
        # has to match the array in lang_template.yaml
        languages = ['EN', 'DE', 'FR', 'IT', 'PT', 'ES']
        for l in languages:
            self.add_widget(ButtonLanguage(l))
        # self.add_widget(wid)

class LayoutPopup(BoxLayout):
    pass

class FullScreenPopup(ModalView):
    pass

class LanguagePopup(FullScreenPopup):
    def __init__(self):
        super().__init__()
        # has to match the array in lang_template.yaml
        languages = ['EN', 'DE', 'FR', 'PT']
        wid = LayoutPopup()
        for l in languages:
            wid.add_widget(ButtonLanguage(l, self._close))
        self.add_widget(wid)

    def _close(self):
        self.dismiss()
        App.get_running_app().after_popup()

class SyncPopup(FullScreenPopup):
    pass

class ScreenWelcome(Screen):
    def on_leave(self):
        # if we are not connected by the time we leave the welcome screen
        # then we show a popup
        app = App.get_running_app()
        if not app._first_status_message_received:
            App.get_running_app()._create_popup()

class ScreenMain(Screen):

    def __init__(self, config, **kwargs):
        self.config = config
        super().__init__(**kwargs)
        wid = self.ids.sm1
        _menu_screen = ScreenMenu(name='menu')
        wid.add_widget(_menu_screen)
        _settings_screen = ScreenSettings(name='settings')
        wid.add_widget(_settings_screen)
        _redeem_screen = ScreenRedeem(name='redeem')
        wid.add_widget(_redeem_screen)
        _scan_screen = ScreenBuyScan(config, name='scan_screen')
        wid.add_widget(_scan_screen)
        _insert_screen = ScreenBuyInsert(config, name='insert_screen')
        wid.add_widget(_insert_screen)
        _buy_screen3 = ScreenBuyFinal(name='final_buy_screen')
        wid.add_widget(_buy_screen3)
        _sell_screen1 = ScreenSell1(config, name='sell1')
        wid.add_widget(_sell_screen1)
        _sell_screen2 = ScreenSell2(config, name='sell2')
        wid.add_widget(_sell_screen2)
        _sell_screen3 = ScreenSell3(name='sell3')
        wid.add_widget(_sell_screen3)
        _confirmation_screen = ScreenConfirmation(name='confirmation')
        wid.add_widget(_confirmation_screen)
        _loading_screen = ScreenLoading(name='loading_screen')
        wid.add_widget(_loading_screen)

class ScreenMenu(Screen):
    pass

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
        t = Thread(target = self._CASHIN.start_cashin(), daemon=True)
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
                self.ids.buy_limit.text = App.get_running_app()._languages[App.get_running_app()._selected_language]["limitreached"]


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
        amount_xchf = self._cash_in * 1e18
        eth_amount = price_tools.get_buy_price(amount_xchf, app._xchf_reserve, app._eth_reserve)
        self._estimated_eth = eth_amount
        self._minimum_wei = eth_amount * 0.98
        return eth_amount/1e18


    def _buy(self):
        self.ids.buy_confirm.text = App.get_running_app()._languages[App.get_running_app()._selected_language]["pleasewait"]
        self.ids.buy_confirm.disabled = True
        self._CASHIN.stop_cashin()
        Thread(target=self._threaded_buy, daemon=True).start()

    def _threaded_buy(self):
        min_eth = self._minimum_wei/1e18
        print("exact min wei", self._minimum_wei)
        print("min eth", min_eth)
        success, value = self._node_rpc.buy(str(int(1e18*self._cash_in)), self._address_ether, self._minimum_wei)
        if success:
            self.manager.get_screen("final_buy_screen")._chf_sold = self._cash_in
            self.manager.get_screen("final_buy_screen")._eth_bought = min_eth
            self.manager.get_screen("final_buy_screen")._address_ether = self._address_ether
            self.ids.buy_confirm.text = App.get_running_app()._languages[App.get_running_app()._selected_language]["confirm"]
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
    _chf_sold = NumericProperty(0)
    _eth_bought = NumericProperty(0)

    def on_leave(self):
        self._chf_sold = 0
        self._eth_bought = 0
        self.address = ''

class ScreenSettings(Screen):
    pass

class ScreenRedeem(Screen):
    pass

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

class ScreenLoading(Screen):
    pass

class ScreenConfirmation(Screen):
    pass

class Manager(ScreenManager):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        _welcome_screen = ScreenWelcome(name='welcome')
        self.add_widget(_welcome_screen)
        _main_screen = ScreenMain(config, name='main')
        self.add_widget(_main_screen)
        self._main_screen = _main_screen
        self._welcome_screen = _welcome_screen


class TemplateApp(App):
    # with only eth/chf, that's ok but might have to
    # try to share a variable in another way
    _chf_to_eth = NumericProperty(0)
    _eth_to_chf = NumericProperty(0)
    _selected_language = StringProperty('English')
    #_current_block = NumericProperty(-1)
    #_sync_block = NumericProperty(-1)
    _xchf_reserve = NumericProperty(-1e18)
    _eth_reserve = NumericProperty(-1e18)

    def __init__(self, config):
        super().__init__()
        ConfigApp._select_all_drivers(config, self._update_message_cashin, self._update_message_pricefeed, self._update_message_status)
        self._config = config
        self._m = None
        self._chf_to_eth = -1
        self._eth_to_chf = -1
        self._popup_sync = None
        self._overlay_lock = Lock()
        self._popup_count = 0
        self._first_status_message_received = False

    def build(self):
        languages_yaml = strictyaml.load(Path("lang_template.yaml").bytes().decode('utf8')).data
        self._languages = {k: dict(v) for k, v in languages_yaml.items()}
        self._selected_language = next(iter(self._languages)) # get a language

        self._m = Manager(self._config, transition=RiseInTransition())
        self._config.PRICEFEED.start()
        self._config.STATUS.start()
        return self._m

    def change_language(self, selected_language):
        self._selected_language = selected_language

    def _update_message_pricefeed(self, message):
        ''' only updates the _chf_to_eth attribute '''
        ''' only dispatching the message to the right screen'''
        msg_json = json.loads(message)
        eth_reserve = msg_json['eth_reserve']
        self._eth_reserve = int("0x" + eth_reserve, 16)
        xchf_reserve = msg_json['token_reserve']
        self._xchf_reserve = int("0x" + xchf_reserve, 16)
        # we use 20CHF as the standard amount people will buy
        sample_amount = 20e18
        # received values are in weis
        one_xchf_buys = price_tools.get_buy_price(sample_amount, self._xchf_reserve, self._eth_reserve) / sample_amount
        self._chf_to_eth = 1/one_xchf_buys
        sample_chf_buys = price_tools.get_sell_price(sample_amount, self._eth_reserve, self._xchf_reserve)
        self._eth_to_chf = sample_amount / sample_chf_buys

    def _update_message_cashin(self, message):
        ''' only dispatching the message to the right screen'''
        screen = self._m._main_screen.ids['sm1'].get_screen('insert_screen')
        screen._update_message_cashin(message)

    def _update_message_status(self, message):
        self._first_status_message_received = True
        msg_json = json.loads(message)
        is_in_sync = msg_json["blockchain"]["is_in_sync"]
        #self._current_block = int(msg_json["blockchain"]["current_block"])
        #self._sync_block = int(msg_json["blockchain"]["sync_block"])

        self._show_sync_popup(is_in_sync)

    def _show_sync_popup(self, is_in_sync):
        if not is_in_sync:
            self._create_popup()
        if is_in_sync:
            self._delete_popup()

    def _create_popup(self):
        if self._popup_sync is None:
            self.before_popup()
            self._popup_sync = SyncPopup()
            self._popup_sync.open()

    def _delete_popup(self):
        if self._popup_sync is not None:
            self._popup_sync.dismiss()
            self._popup_sync = None
            self.after_popup()

    def on_stop(self):
        self._config.CASHIN_THREAD.stop_cashin()
        self._config.PRICEFEED.stop_listening()
        self._config.NODE_RPC.stop()

    # this method is ugly but we play with the raspicam overlay and have no choice
    def before_popup(self):
        ''' used to cleanup the overlay in case a popup is opened while in scanning mode
        this method must be called before a popup is opened'''
        driver = self._config.QR_SCANNER
        # this will raise an error when the driver has no _overlay_auto_on attribute
        # aka we're not on raspberry pi + raspicam
        try:
            _ = driver._overlay_auto_on
        except:
            return
        with self._overlay_lock:
            self._popup_count += 1
            if driver._overlay_auto_on and self._popup_count == 1:
                driver._hide_overlay()

    # this method is ugly but we play with the raspicam overlay and have no choice
    def after_popup(self):
        ''' used to show the overlay in case a popup is closed while in scanning mode
        this method must be called after a popup is closed'''
        driver = self._config.QR_SCANNER
        # this will raise an error when the driver has no _overlay_auto_on attribute
        # aka we're not on raspberry pi + raspicam
        try:
            _ = driver._overlay_auto_on
        except:
            return

        with self._overlay_lock:
            self._popup_count -= 1
            if driver._overlay_auto_on and self._popup_count == 0:
                driver._show_overlay()

if __name__ == '__main__':
    config = parse_args()

    from kivy.config import Config
    Config.set('kivy', 'exit_on_escape', 1)
    if config.DEBUG:
        Config.set('kivy', 'log_level', 'debug')
    Config.write()
    Window.size = (1280, 720)
    #Window.borderless = True
    if config.IS_FULLSCREEN:
        Window.fullscreen = True
        Window.show_cursor = False
    TemplateApp(config).run()
