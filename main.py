__version__ = "1.3.0"

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
import os
from path import Path

from config_tools import parse_args as parse_args
from config_tools import CameraMethod as CameraMethod
from config_tools import RelayMethod as RelayMethod

#for fullscreen
#from kivy.core.window import Window
#Window.size = (800, 600)
#Window.fullscreen = False

from kivy.config import Config
#Config.set('graphics', 'fullscreen', 'fake')
Config.set('kivy', 'exit_on_escape', 1)
#Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'invert_x', 1)

Config.write()

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

    def __init__(self, config, **kwargs):
        self._config = config
        super(RootWidget, self).__init__(**kwargs)

    def start_sendcoins_thread(self):
        threading.Thread(target=self.sendcoins_thread).start()

    def sendcoins_thread(self):
        # Worker thread to call the backend when transaction complete to actually send the coins
        # unneeded now
        pass

    def start_qr_thread(self):
        print("start qr")
        threading.Thread(target=self.qr_thread).start()
    def qr_thread(self):
        # This is the code executing in the new thread.
        #
        # cmd = 'pifacedigitalio(Relay(0)Ligth_on)'
        if self._config.RELAY_METHOD == 'piface':
            pifacedigital = pifacedigitalio.PiFaceDigital()
            pifacedigital.output_pins[0].turn_on() # this command does the same thing..
            pifacedigital.leds[0].turn_on() # as this command
        elif self._config.RELAY_METHOD == 'gpio':
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(7, GPIO.OUT)
            GPIO.output(7, GPIO.HIGH)
            GPIO.output(7, GPIO.LOW)

        if CameraMethod[self._config.CAMERA_METHOD] is CameraMethod.ZBARCAM:
            # fallback resolution of C270 is too low to scan
            cmd = 'zbarcam --prescale=640x480 --nodisplay {}'.format(self._config.ZBAR_VIDEO_DEVICE)
        elif CameraMethod[self._config.CAMERA_METHOD] is RelayMethod.OPENCV:
            cmd = '/home/pi/Prog/zbar-build/test/a.out'
        else:
            print("No CameraMethod selected")

        self.execute = pexpect.spawn(cmd, [], 300)

        # infinite loop
        while True:
            try:
                self.execute.expect('\n')
                # Get last line fron expect
                line = self.execute.before
                print(line)
                if os.uname()[4].startswith("arm"):
                    if line != "" and line != None and line.startswith("decoded QR-Code symbol"):
                        self.qr_thread_update_label_text(line[22:])
                        # wal.close()
                        print("found qr: %s" % line[22:])
                        execute.close(True)
                        if self._config.RELAY_METHOD is RelayMethod.PIFACE:
                            # pifacedigital(ligth_off)
                            pifacedigital.output_pins[0].turn_off()  # this command does the same thing..
                            pifacedigital.leds[0].turn_off()  # as this command
                        elif self._config.RELAY_METHOD is RelayMethod.GPIO:
                            GPIO.output(7, GPIO.HIGH)
                        break
                else:
                    if line != "" and line != None and line.startswith(b"QR-Code:"):
                        self.qr_thread_update_label_text(line[8:])
                        self.execute.close(True)
                        if self._config.RELAY_METHOD is RelayMethod.PIFACE:
                            # pifacedigital(ligth_off)
                            pifacedigital.output_pins[0].turn_off()  # this command does the same thing..
                            pifacedigital.leds[0].turn_off()  # as this command
                        elif self._config.RELAY_METHOD is RelayMethod.GPIO:
                            GPIO.output(7, GPIO.HIGH)
                        break
            except pexpect.EOF:
                # Ok maybe not a complete infinite loooop but you get what i mean
                break
            except pexpect.TIMEOUT:
                print("timeout")
                break
        print("clear stop scan")
        self.stop_scan.clear()
        return
    ###@mainthread
    def qr_thread_update_label_text(self, new_text):
        app = App.get_running_app()
        text = str(new_text)
        print("the text")
        print(text)
        text = text.replace('b\'', '').strip()
        text = text.replace('\\r\'', '').strip()
        text = text.replace('\"', '').strip()
        # text = ''.join(filter(str.isalnum, text))
        print(text)
        address = text.split(":")
        print(address)
        if address[0] == 'bitcoin':
            print("not for now :(")
            # label.text = address[1].rstrip()
            # print(address[1])
            # self.root_manager.current = 'buy'
            # self.start_cashin_thread()
        elif address[0] == 'ethereum':
            print("ok")
            app.clientaddress = address[1].rstrip()
            self.root_manager.current = 'buy'
        else:
            label.text = "Invalid QR Code"


    def stop_scanning(self):
        self.execute.close(True)
        #self.execute.terminate()

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
        print(imgn)
        print(dir(imgn))
        #data = io.BytesIO(open("image.png", "rb").read())
        print("before coreimage")
        #imgo = CoreImage(imgn)
        print("after coreimage")
        #print imgo
        print(dir(img))
        #img.canvas.clear()
        img_tmp_file = open(os.path.join('tmp', 'qr.png'), 'wb')
        imgn.save(img_tmp_file, 'PNG')
        img_tmp_file.close()
        self.root_manager.get_screen('sellfinish').ids["'generate_qr'"].source = os.path.join('tmp', 'qr.png')


class CashInThread(Thread):

    def __init__(self, app, config):
        super(CashInThread, self).__init__()
        self.app = app
        self._config = config
        self.stopcashin = threading.Event()
        self.daemon = True

    def run(self):
        """Run Worker Thread."""
        if self._config.MOCK_VALIDATOR:
            zctx = zmq.Context()
            self.zsock = zctx.socket(zmq.SUB)
            self.zsock.connect('tcp://localhost:{}'.format(self._config.MOCKPORT))
            self.zsock.setsockopt_string(zmq.SUBSCRIBE,'')

            while True:
                msg = self.zsock.recv_multipart()
                if not self.stopcashin.is_set():
                    if DEBUG:
                        Logger.info(' Mock Validator msg:%s' % (msg))
                    self.app.cashin_update_label_text(msg[0]) # "CHF:10"

        else:
            #  Create a new object ( Validator Object ) and initialize it
            validator = eSSP(com_port=self._config.VALIDATOR_PORT, ssp_address="0", nv11=False, debug=self._config.DEBUG)

            while not self.stopcashin.is_set():

                # ---- Example of interaction with events ---- #
                if validator.nv11: # If the model is an NV11, put every 100 note in the storage, and others in the stack(cashbox), but that's just for this example
                    (note, currency,event) = validator.get_last_event()
                    if note == 0 or currency == 0 or event == 0:
                        pass  # Operation that do not send money info, we don't do anything with it
                    else:
                        if note != 4 and event == Status.SSP_POLL_CREDIT:
                            validator.print_debug("NOT A 100 NOTE")
                            validator.nv11_stack_next_note()
                            validator.enable_validator()
                        elif note == 4 and event == Status.SSP_POLL_READ:
                            validator.print_debug("100 NOTE")
                            validator.set_route_storage(100)  # Route to storage
                            validator.do_actions()
                            validator.set_route_cashbox(50)  # Everything under or equal to 50 to cashbox ( NV11 )
                else:
                    print("Read on Channel " + str(poll[1][1]))
                time.sleep(0.5)
        #
        # k = eSSP.eSSP('/dev/ttyUSB0')
        # print(k.sync())
        # print(k.enable_higher_protocol())
        # print(k.set_inhibits(k.easy_inhibit([1, 1, 1, 1]), '0x00'))
        # print(k.enable())
        # #Publisher().subscribe(self.stoprun, "stoprun")
        # var = 1
        # i = 0
        # #self.stopflag = False
        #
        #
        # while not self.stopcashin.is_set():
        #     poll = k.poll()
        #
        #     if len(poll) > 1:
        #         if len(poll[1]) == 2:
        #             print(poll[1][0])
        #             if poll[1][0] == '0xef':
        #                 if poll[1][1] == 1 or poll[1][1] == 3:
        #                     while i < 2:
        #                         k.hold()
        #                         print("Hold " + str(i))
        #                         time.sleep(0.5)
        #                         i += 1
        #             if poll[1][0] == '0xef':
        #                 print("Read on Channel " + str(poll[1][1]))
        #             if poll[1][0] == '0xe6':
        #                 print("Fraud on Channel " + str(poll[1][1]))
        #
        #             if poll[1][0] == '0xee':
        #                 print("Credit on Channel " + str(poll[1][1]))
        #                 if poll[1][1] == 1:
        #                     self.cashin_update_label_text("CHF:10")
        #                     #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:10"), -1)
        #                 if poll[1][1] == 2:
        #                     self.cashin_update_label_text("CHF:20")
        #                     #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:20"), -1)
        #                 if poll[1][1] == 3:
        #                     self.cashin_update_label_text("CHF:50")
        #                     #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:50"), -1)
        #                 if poll[1][1] == 4:
        #                     self.cashin_update_label_text("CHF:100")
        #                     #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:100"), -1)
        #                 if poll[1][1] == 5:
        #                     self.cashin_update_label_text("CHF:200")
        #                     #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:200"), -1)
        #                 #if poll[1][1] == 6:
        #                 #    wx.CallAfter(self.SendInfo, "CHF:200")
        #                 #wx.CallAfter(self.SendInfo, k.unit_data())
        #             i = 0
        #
        #     time.sleep(0.5)
        self.stopcashin.clear()

        return

class ZmqThread(Thread):
    def __init__(self, app, config):
        super(ZmqThread, self).__init__()
        self._config = config
        self.app = app
        self.daemon = True

    def run(self):
        app = self.app
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect('tcp://localhost:{}'.format(self._config.ZMQ_PORT))
        zsock.setsockopt_string(zmq.SUBSCRIBE,'priceticker')

        while True:
            topic, msg = zsock.recv_multipart()
            if self._config.DEBUG:
                Logger.info('   Topic: %s, msg:%s' % (topic, msg))
            app.on_message(msg)


class AtmClientApp(App):
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
        self._config = config
        print(self._config)
        for k in config.NOTES_VALUES:
            self.cash_in[k] = 0

        super(AtmClientApp, self).__init__(**kwargs)

    def zmq_connect(self):
        self._zthread = ZmqThread(self, self._config)
        self._zthread.start()

    ###@mainthread
    def on_message(self, data):
        print(data)
        self.price = json.loads(data)

    ###@mainthread
    def change_language(self, lang):
        print("change language to %s" % lang)
        self.l = self.lang[lang]


    def start_cashin_thread(self):
        #threading.Thread(target=self.cashin_thread).start()
        self._cashinthread = CashInThread(self, self._config)
        self._cashinthread.start()

    def stop_cashin(self):
        print("set stop.cashin")
        self._cashinthread.stopcashin.set()

    def process_buy(self):
        print("process buy")
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.REQ)
        zsock.connect('tcp://localhost:5557')
        data = {'method': 'buy', 'amount': self.cashintotal, 'address': self.clientaddress}
        zsock.send_json(data)
        message = zsock.recv()

        self.root.cashin_reset_session()


    ###@mainthread
    def cashin_update_label_text(self, new_credit):
        print(new_credit)
        credit = new_credit.decode('utf-8')
        credit = credit.split(':')

        if credit[1] in self._config.NOTES_VALUES:
            note = credit[1]
            self.cash_in[note] += 1
            self.cashintotal += int(note)
            print("cashtotal", self.cashintotal)
            print("cash", self.cash_in)

    def build(self):
        self.zmq_connect()
        self.start_cashin_thread()

        self.lang = strictyaml.load(Path("lang.yaml").bytes().decode('utf8')).data
        self.LANGUAGES = [language for language in self.lang]
        # self.language = self.lang

        self.root = RootWidget(self._config)

        Logger.info('Frontend Started')

        self.root.root_manager.current = 'welcome'

        return self.root


if __name__ == '__main__':
    config = parse_args()
    AtmClientApp(config).run()
