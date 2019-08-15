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
from threading import Thread
import json

from config_tools import parse_args as parse_args
from config_tools import Config as ConfigApp


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
            wid.add_widget(ButtonLanguage(l, self.dismiss))
        self.add_widget(wid)

class SyncPopup(FullScreenPopup):
    pass

class ScreenWelcome(Screen):
    def on_enter(self):
        #ugly trick to prevent the user to interact with the GUI
        # before the app receives sync packetes
        def test():
            import time
            time.sleep(0.5)
            App.get_running_app()._create_popup()
        Thread(target=test, daemon=True).start()

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

    def _buy(self):
        self.manager.transition.direction = 'left'
        self.manager.current = "loading_screen"
        Thread(target=self._threaded_buy, daemon=True).start()

    def _threaded_buy(self):
        success, value = self._node_rpc.buy(self._cash_in, self._address_ether)
        if success:
            self.manager.get_screen("final_buy_screen")._chf_sold = self._cash_in
            self.manager.get_screen("final_buy_screen")._eth_bought = value
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
    _current_block = NumericProperty(-1)
    _sync_block = NumericProperty(-1)

    def __init__(self, config):
        super().__init__()
        ConfigApp._select_all_drivers(config, self._update_message_cashin, self._update_message_pricefeed, self._update_message_status)
        self._config = config
        self._m = None
        self._chf_to_eth = -1
        self._eth_to_chf = -1
        self._popup_sync = None


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
        # received values are in weis
        self._chf_to_eth = float(msg_json['buy_price'])/1e18
        self._eth_to_chf = float(msg_json['sell_price'])/1e18

    def _update_message_cashin(self, message):
        ''' only dispatching the message to the right screen'''
        screen = self._m._main_screen.ids['sm1'].get_screen('insert_screen')
        screen._update_message_cashin(message)

    def _update_message_status(self, message):
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
            self._popup_sync = SyncPopup()
            self._popup_sync.open()

    def _delete_popup(self):
        if self._popup_sync is not None:
            self._popup_sync.dismiss()
            self._popup_sync = None

    def on_stop(self):
        self._config.CASHIN_THREAD.stop_cashin()
        self._config.PRICEFEED.stop_listening()
        self._config.NODE_RPC.stop()

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
