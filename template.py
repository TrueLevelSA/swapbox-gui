from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty
import strictyaml
from path import Path
from threading import Thread

from config_tools import parse_args as parse_args
from config_tools import Config as ConfigApp

# bad but for now it will be ok
# if this is still here in 2 weeks then that's very bad
CONFIG = None

Window.size = (1380, 770)

class WelcomeScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class ScreenBuyScan(Screen):
    _qr_scanner = ObjectProperty(None)

    def on_enter(self):
        print("sdlkfj")
        self._qr_scanner = CONFIG.QR_SCANNER
        thread = Thread(target=self._start_scan)
        thread.setDaemon(True)
        thread.start()

    def _start_scan(self):
        CONFIG.LED_DRIVER.led_on()
        qr = self._qr_scanner.scan()
        CONFIG.LED_DRIVER.led_off()
        if qr is not None:
            print("QR FOUND")
            print(qr)
        else:
            print("QR not found")

    def on_pre_leave(self):
        self._qr_scanner.stop_scan()

class BuyScreen2(Screen):
    pass

class BuyScreen3(Screen):
    pass

class SettingsScreen(Screen):
    pass

class BuyScreen(Screen):
    pass

class RedeemScreen(Screen):
    pass

class SellScreen1(Screen):
    pass

class SellScreen2(Screen):
    pass

class SellScreen3(Screen):
    pass

class ConfirmationScreen(Screen):
    pass

class Manager(ScreenManager):

    welcome_screen = ObjectProperty(None)
    main_screen = ObjectProperty(None)
    menu_screen = ObjectProperty(None)
    settings_screen = ObjectProperty(None)
    redeem_screen = ObjectProperty(None)
    _scan_screen = ObjectProperty(None)
    buy_screen2 = ObjectProperty(None)
    buy_screen3 = ObjectProperty(None)
    sell_screen1 = ObjectProperty(None)
    sell_screen2 = ObjectProperty(None)
    sell_screen3 = ObjectProperty(None)
    confirmation_screen = ObjectProperty(None)


class TemplateApp(App):

    def __init__(self, config):
        super().__init__()
        self._config = config


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
        m = Manager(transition=SlideTransition())
        return m

    def change_language(self, selected_language):
        self._selected_language = selected_language

if __name__ == '__main__':
    config = parse_args()
    ConfigApp._select_all_drivers(config, lambda x: print(x))
    CONFIG = config

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
