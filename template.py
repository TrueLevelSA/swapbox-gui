from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
import strictyaml
from path import Path
from threading import Thread
import json

from config_tools import parse_args as parse_args
from config_tools import Config as ConfigApp


Window.size = (1380, 770)

class ScreenWelcome(Screen):
    pass

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
        _buy_screen3 = ScreenBuy3(name='buy3')
        wid.add_widget(_buy_screen3)
        _sell_screen1 = ScreenSell1(name='sell1')
        wid.add_widget(_sell_screen1)
        _sell_screen2 = ScreenSell2(name='sell2')
        wid.add_widget(_sell_screen2)
        _sell_screen3 = ScreenSell3(name='sell3')
        wid.add_widget(_sell_screen3)
        _confirmation_screen = ScreenConfirmation(name='confirmation')
        wid.add_widget(_confirmation_screen)

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
            print(qr)
            self.manager.get_screen('insert_screen')._qr_code_ether = qr
            self.manager.transition.direction = 'left'
            self.manager.current = 'insert_screen'
        else:
            print("QR not found")

class ScreenBuyInsert(Screen):
    _qr_code_ether = StringProperty("nothing:nothing")
    _cash_in = NumericProperty(0)

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._thread = config.CASHIN_THREAD
        self._thread.start()

    def _update_message_cashin(self, message):
        print(message)


class ScreenBuy3(Screen):
    _address = StringProperty('')

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

    def __init__(self, config):
        super().__init__()
        ConfigApp._select_all_drivers(config, self._update_message_cashin, self._update_message_pricefeed)
        self._config = config
        self._m = None
        self._chf_to_eth = -1
        self._eth_to_chf = -1


    def build(self):
        languages_yaml = strictyaml.load(Path("lang_template.yaml").bytes().decode('utf8')).data
        self._languages = {k: dict(v) for k, v in languages_yaml.items()}
        self._selected_language = next(iter(self._languages)) # get a language

        self.transactions = {
            'txid':
                {
                    'timestamp': 28581305,
                    'amount_fiat': 50,
                    'type_fiat': 'CHF',
                    'amount_crypto': 1.2,
                    'type_crypto': 'ETH'
                }
        }
        self.redeemcodes = {
            'code1':
                {
                    'fiat': 70,
                    'type': 'CHF'
                }
        }
        self._m = Manager(self._config, transition=RiseInTransition())
        self._config.PRICEFEED.start()
        return self._m

    def change_language(self, selected_language):
        self._selected_language = selected_language

    def _update_message_pricefeed(self, message):
        ''' only updates the _chf_to_eth attribute '''
        ''' only dispatching the message to the right screen'''
        msg_json = json.loads(message)
        self._chf_to_eth = float(msg_json['buy_price'])/1e18
        self._eth_to_chf = float(msg_json['sell_price'])/1e18

    def _update_message_cashin(self, message):
        ''' only dispatching the message to the right screen'''
        screen = self._m._main_screen.ids['sm1'].get_screen('insert_screen')
        screen._update_message_cashin(message)

    def on_stop(self):
        self._config.CASHIN_THREAD.stop_cashin()
        self._config.PRICEFEED.stop_listening()

if __name__ == '__main__':
    config = parse_args()

    from kivy.config import Config
    #Config.set('graphics', 'fullscreen', 'fake')
    Config.set('kivy', 'exit_on_escape', 1)
    #Config.set('kivy', 'desktop', 1)
    Config.set('kivy', 'invert_x', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    if config.DEBUG:
        Config.set('kivy', 'log_level', 'debug')
    Config.write()
    TemplateApp(config).run()
