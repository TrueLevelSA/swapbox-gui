__version__ = "1.3.0"

import os

from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button

# Kivy's install_twisted_rector MUST be called early on!
#from kivy.support import install_twisted_reactor
#install_twisted_reactor()

#from kivy.uix.camera import Camera
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.logger import Logger
import time
# from kivy.clock import Clock, mainthread
from functools import partial
import threading
import pexpect
#for Note Validator
if os.uname()[4].startswith("arm"):
    from eSSP.constants import Status
    from eSSP import eSSP  # Import the library
#import eSSP
from decimal import Decimal, ROUND_UP, ROUND_DOWN
import requests
import json
import zmq
from threading import Thread
import qrcode
import strictyaml
from path import Path

from config_tools import parse_args as parse_args
from config_tools import CameraMethod as CameraMethod
from config_tools import RelayMethod as RelayMethod
# "force" people to use logger
from config_tools import print_debug as print

from custom_threads.cashin_thread import CashInThread
from custom_threads.zmq_price_ticker_thread import ZmqPriceTickerThread

#for fullscreen
#from kivy.core.window import Window
#Window.size = (800, 600)
#Window.fullscreen = False


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


class WelcomeScreen(Screen):
    pass


class ScanWalletScreen(Screen):
    pass


class BuyScreen(Screen):
    pass


class BuyFinishScreen(Screen):
    pass


class SellSelectScreen(Screen):
    pass

class SellFinishScreen(Screen):
    pass


class MyScreenManager(ScreenManager):
    pass

class RootWidget(FloatLayout):
    '''
       This the class representing your root widget.
       By default it is inherited from ScreenManager,
       you can use any other layout/widget depending on your usage.
    '''
    root_manager = ObjectProperty()
    current_btm_process_id = NumericProperty()

    stop = threading.Event()
    stop_scan = threading.Event()
    # current_ticker = Decimal(0)

    def __init__(self, config, app, **kwargs):
        self._config = config

        self._led_driver = Config.select_led_driver(config)
        self._qr_scanner = Config.select_qr_scanner(config)
        self._cashin_thread = Config.select_cashin_thread(config, app.cashin_update_label_text)

        super(RootWidget, self).__init__(**kwargs)

    # imports in functions because we cannot import not-installed stuff
    def start_sendcoins_thread(self):
        Logger.debug("start_sendcoinds_thread")
        threading.Thread(target=self.sendcoins_thread).start()

    def sendcoins_thread(self):
        # Worker thread to call the backend when transaction complete to actually send the coins
        # unneeded now
        pass

    def start_qr_thread(self):
        Logger.debug("start qr")
        threading.Thread(target=self.qr_thread).start()

    def qr_thread(self):
        # This is the code executing in the new thread.

        self._led_driver.led_on()
        qr = self._qr_scanner.scan()
        self._led_driver.led_off()
        if qr is not None:
            self.qr_thread_update_label_text(qr)


    ###@mainthread
    def qr_thread_update_label_text(self, new_text):
        app = App.get_running_app()
        text = str(new_text)
        Logger.debug("the text")
        Logger.debug(text)
        address = text.split(":")
        Logger.debug(address)
        if address[0] == 'bitcoin':
            Logger.debug("not for now :(")
            # label.text = address[1].rstrip()
            # Logger.debug(address[1])
            # self.root_manager.current = 'buy'
            # self.start_cashin_thread()
        elif address[0] == 'ethereum':
            Logger.debug("ok")
            app.clientaddress = address[1].rstrip()
            self.root_manager.current = 'buy'
        else:
            label.text = "Invalid QR Code"


    def stop_scanning(self):
        self._qr_scanner.stop_scan()

    def cashin_reset_session(self):
        app = App.get_running_app()

        app.clientaddress = ""
        app.cashintotal = 0
        for k in self._config.NOTES_VALUES:
            app.cash_in[k] = 0

    ###@mainthread
    def generate_qr(self):

        new_text = '0x123456789abcdef'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(new_text)
        qr.make(fit=True)
        img = self.root_manager.get_screen('sellfinish').ids["'generate_qr'"]
        imgn = qr.make_image()
        Logger.debug(imgn)
        Logger.debug(dir(imgn))
        #data = io.BytesIO(open("image.png", "rb").read())
        Logger.debug("before coreimage")
        #imgo = CoreImage(imgn)
        Logger.debug("after coreimage")
        #print imgo
        Logger.debug(dir(img))
        #img.canvas.clear()
        img_tmp_file = open(os.path.join('tmp', 'qr.png'), 'wb')
        imgn.save(img_tmp_file, 'PNG')
        img_tmp_file.close()
        self.root_manager.get_screen('sellfinish').ids["'generate_qr'"].source = os.path.join('tmp', 'qr.png')




class SwapBoxApp(App):
    # def stop_scan(self):
    #     # The Kivy event loop is about to stop, set a stop signal;
    #     # otherwise the app window will close, but the Python process will
    #     # keep running until all secondary threads exit.
    #     self.root.stop_scan.set()

    price = ObjectProperty({'buy_price': 0, 'sell_price': 0})
    l = ObjectProperty(strictyaml.load(Path("lang.yaml").bytes().decode('utf8')).data['English'])
    # current_buy_transaction = ObjectProperty({'cashin10': 0, 'cashin20': 0, 'cashin50': 0, 'cashin100': 0, 'cashin200': 0})


    # current buy vars
    cash_in = ObjectProperty({})
    cashintotal = NumericProperty(0)
    clientaddress = ObjectProperty('N/A')

    def __init__(self, config, **kwargs):
        # see build function as well
        self._config = config

        super(SwapBoxApp, self).__init__(**kwargs)

    def build(self):
        for k in config.NOTES_VALUES:
            self.cash_in[k] = 0

        self.zmq_connect()
        self._cashinthread = CashInThread(self, self._config)
        self._cashinthread.start()

        self.lang = strictyaml.load(Path("lang.yaml").bytes().decode('utf8')).data
        self.LANGUAGES = [language for language in self.lang]
        # self.language = self.lang

        self.root = RootWidget(self._config, self)

        Logger.info('Frontend Started')

        self.root.root_manager.current = 'welcome'

        return self.root


    def on_stop(self):
        # cleanup low level stuff
        self.root._led_driver.close()

    def zmq_connect(self):
        self._zthread = ZmqPriceTickerThread(self.on_message, self._config.ZMQ_PORT)
        self._zthread.start()

    ###@mainthread
    def on_message(self, data):
        ''' callback for zmq price '''
        Logger.debug(data)
        self.price = json.loads(data)

    ###@mainthread
    def change_language(self, lang):
        Logger.debug("change language to %s" % lang)
        self.l = self.lang[lang]


    # called on click in swapbox.kv, but thread is never restarded?
    def stop_cashin(self):
        Logger.debug("set stop.cashin")
        self._cashinthread.stop_cashin()

    def process_buy(self):
        Logger.debug("process buy")
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.REQ)
        zsock.connect('tcp://localhost:{}'.format(self._config.ZMQ_PORT_BUY))
        data = {'method': 'buy', 'amount': self.cashintotal, 'address': self.clientaddress}
        zsock.send_json(data)
        message = zsock.recv()

        self.root.cashin_reset_session()


    ###@mainthread
    def cashin_update_label_text(self, new_credit):
        ''' callback on cashin events '''
        Logger.debug(new_credit)
        credit = new_credit.decode('utf-8')
        credit = credit.split(':')

        if len(credit) < 2:
            Logger.debug("wrong format for credit message")
            return

        if credit[1] in self._config.NOTES_VALUES:
            note = credit[1]
            self.cash_in[note] += 1
            self.cashintotal += int(note)
            Logger.debug("cashtotal {}".format(self.cashintotal))
            Logger.debug("cash {}".format(self.cash_in))
        else:
            Logger.debug("wrong format for credit message")


if __name__ == '__main__':
    config = parse_args()
    from kivy.config import Config
    #Config.set('graphics', 'fullscreen', 'fake')
    Config.set('kivy', 'exit_on_escape', 1)
    #Config.set('kivy', 'desktop', 1)
    Config.set('kivy', 'invert_x', 1)
    if config.DEBUG:
        Config.set('kivy', 'log_level', 'debug')
    Config.write()
    SwapBoxApp(config).run()
