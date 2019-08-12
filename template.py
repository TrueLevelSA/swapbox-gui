from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
import strictyaml
from path import Path
from threading import Thread, Lock
import json

from config_tools import parse_args as parse_args
from config_tools import Config as ConfigApp
import price_tools


class ButtonLanguage(Button):
    _language = StringProperty(None)

    def __init__(self, language, callback=None, **kwargs):
        self._language = language
        self._callback =  callback
        #self.text = language
        self.background_down = 'img/flags/large/' + language + '.png'
        self.background_normal = self.background_down
        super().__init__(**kwargs)

    def on_press(self):
        App.get_running_app().change_language(self._language)
        if self._callback is not None:
            self._callback()

class LayoutPopup(BoxLayout):
    pass

class FullScreenPopup(ModalView):
    pass

class LanguagePopup(FullScreenPopup):
    def __init__(self):
        super().__init__()
        # has to match the array in lang_template.yaml
        languages = ['FR', 'EN', 'PT']
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
        _sell_screen1 = ScreenSell1(name='sell1')
        wid.add_widget(_sell_screen1)
        _sell_screen2 = ScreenSell2(name='sell2')
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
        if qr is not None:
            self.manager.get_screen('insert_screen').set_address_from_qr(qr)
            self.manager.transition.direction = 'left'
            self.manager.current = 'insert_screen'
        else:
            print("QR not found")

class ScreenBuyInsert(Screen):
    _qr_code_ether = StringProperty("ethereum:0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _address_ether = StringProperty("0x6129A2F6a9CA0Cf814ED278DA8f30ddAD5B424e2")
    _cash_in = NumericProperty(0)
    _minimum_eth = NumericProperty(0)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._CASHIN = config.CASHIN_THREAD
        self._valid_notes = config.NOTES_VALUES
        self._node_rpc = config.NODE_RPC

    def on_pre_enter(self):
        t = Thread(target = self._CASHIN.start_cashin(), daemon=True)
        t.start()

    def on_pre_leave(self):
        self._CASHIN.stop_cashin()

    def _update_message_cashin(self, message):
        amount_received = message.split(':')[1]
        if amount_received in self._valid_notes:
            self._cash_in += int(amount_received)

    def set_address_from_qr(self, qr):
        self._qr_code_ether = qr
        self._address_ether = self._qr_code_ether.split(":")[1]

    def _leave_without_buy(self):
        # reseting cash in, might want to give money back
        # might use on_pre_leave or on_leave
        self._cash_in = 0
        self._minimum_eth = 0

    def _get_eth_price(self, app, cash_in):
        if self._cash_in == 0:
            return 0
        amount_xchf = self._cash_in * 1e18
        eth_amount = price_tools.get_buy_price(amount_xchf, app._xchf_reserve, app._eth_reserve)
        self._minimum_eth = eth_amount
        return eth_amount/1e18


    def _buy(self):
        self.manager.transition.direction = 'left'
        self.manager.current = "loading_screen"
        Thread(target=self._threaded_buy, daemon=True).start()

    def _threaded_buy(self):
        min_eth = self._minimum_eth//1000000000000
        print("exact min eth", self._minimum_eth)
        print("min eth", min_eth)
        success, value = self._node_rpc.buy(str(int(1e18*self._cash_in)), self._address_ether, min_eth)
        if success:
            self.manager.get_screen("final_buy_screen")._chf_sold = self._cash_in
            self.manager.get_screen("final_buy_screen")._eth_bought = float(value)/1e18
            print("got", int(value))
            self._cash_in = 0
            self.manager.transition.direction = 'left'
            self.manager.current = "final_buy_screen"
        else:
            self.manager.transition.direction = 'right'
            self.manager.current = "insert_screen"

class ScreenBuyFinal(Screen):
    _address = StringProperty('')
    _chf_sold = NumericProperty(0)
    _eth_bought = NumericProperty(0)

    def on_leave(self):
        self._chf_sold = 0
        self._eth_bought = 0

class ScreenSettings(Screen):
    pass

class ScreenRedeem(Screen):
    pass

class ScreenSell1(Screen):
    pass

class ScreenSell2(Screen):
    pass

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
    _current_block = NumericProperty(-1)
    _sync_block = NumericProperty(-1)
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
        self._eth_reserve = eth_reserve
        xchf_reserve = msg_json['token_reserve']
        self._xchf_reserve = xchf_reserve
        # we use 20CHF as the standard amount people will buy
        sample_amount = 20e18
        # received values are in weis
        one_xchf_buys = price_tools.get_buy_price(sample_amount, xchf_reserve, eth_reserve) / sample_amount
        self._chf_to_eth = 1/one_xchf_buys
        sample_chf_buys = price_tools.get_sell_price(sample_amount, eth_reserve, xchf_reserve) 
        self._eth_to_chf = sample_amount / sample_chf_buys

    def _update_message_cashin(self, message):
        ''' only dispatching the message to the right screen'''
        screen = self._m._main_screen.ids['sm1'].get_screen('insert_screen')
        screen._update_message_cashin(message)

    def _update_message_status(self, message):
        self._first_status_message_received = True
        msg_json = json.loads(message)
        is_in_sync = msg_json["blockchain"]["is_in_sync"]
        self._current_block = int(msg_json["blockchain"]["current_block"])
        self._sync_block = int(msg_json["blockchain"]["sync_block"])

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
