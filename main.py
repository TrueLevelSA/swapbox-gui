__version__ = "1.3.0"

#import yaml

from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Kivy's install_twisted_rector MUST be called early on!
#from kivy.support import install_twisted_reactor
#install_twisted_reactor()


#from kivy.uix.camera import Camera
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty

from kivy.logger import Logger

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition

#for settings window
from kivy.uix.settings import SettingsWithSidebar

import time


from kivy.clock import Clock, mainthread
from functools import partial
import threading
import time
import pexpect
#for Note Validator
#import eSSP
from decimal import Decimal, ROUND_UP, ROUND_DOWN

import requests
import json

import os

import zmq
from threading import Thread



from path import Path
import strictyaml
import argument

# Get config file as required arguemnt and load
f = argument.Arguments()
f.always("config", help="Machine Config file name")
arguments, errors = f.parse()

if arguments.get("config") is not None:
    machine_config = strictyaml.load(Path("machine_config/%s.yaml" % arguments.get("config")).bytes().decode('utf8')).data
else:
    print("Config file must be specified")
    exit(0)

RELAY_METHOD = machine_config.get("relay_method")
NOTE_VALIDATOR_NV11 = machine_config.get("validator_nv11")
VALIDATOR_PORT = machine_config.get("validator_port")
USER = machine_config.get("machine_id")
USER_PASSWORD = machine_config.get("machine_secret")
SERVER_URL = machine_config.get("server_url")
SERVER_REALM = machine_config.get("server_realm")

# For pifacedigital relay
if os.uname()[4].startswith("arm"):
    if RELAY_METHOD == 'piface':
        import pifacedigitalio
    elif RELAY_METHOD == 'gpio':
        import RPi.GPIO as GPIO
        GPIO.cleanup()
else:
    RELAY_METHOD = None
    ZBAR_VIDEO_DEVICE = '/dev/video1'


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


class VerifyScreen(Screen):
    def backward(self, express):
        if express:
            self.display.text = express[:-1]
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

    # START WIDGET GETTER TASKS STUFF #
    def add_cb_widget(
      self, kv_widget, kv_container, item_id, text_field, checked, **kwargs):
        ns = {}
        factoryimport = compile(
          'from kivy.factory import Factory', '<string>', 'exec')
        exec(factoryimport, ns)

        widgetfactory = compile(
          'widget = Factory.'+kv_widget+'()', '<string>', 'exec')
        exec(widgetfactory, ns)

        ns['widget'].id = str(item_id)
        widget = self.widget_properties(ns['widget'], **kwargs)
        if text_field != 'None':
            widget.text = kwargs[text_field]

        if checked:
            widget.is_checked = True
            self.current_address_id = int(item_id)
        addwidget = compile(
          'self.'+kv_container+'.add_widget(widget)', '<string>', 'exec')
        exec(addwidget, locals(), globals())

    def remove_all_cb_widgets(self, container):
        # self.pizzas_widget.clear_widgets()
        removewidget = compile(
          'self.'+container+'.clear_widgets()', '<string>', 'exec')
        exec(removewidget, locals())  # , globals()

    def widget_properties(self, widget, **kwargs):
        for key in kwargs:
            setattr(widget, key, kwargs[key])
        return widget

    def returnWidgetData(self, d, kv_widget, kv_container, text_field):
        print(d)
        r = json.loads(d)
        count = 0
        for item in r:
            self.add_cb_widget(
              kv_widget,
              kv_container,
              item.get("pk"),
              text_field,
              False,
              **item.get("fields")
              )
            count += 1
        return d


    stop = threading.Event()
    stop_scan = threading.Event()
    stopcashin = threading.Event()
    # current_ticker = Decimal(0)

    def start_sendcoins_thread(self):
        threading.Thread(target=self.sendcoins_thread).start()

    def sendcoins_thread(self):
        # Worker thread to call the backend when transaction complete to actually send the coins
        # unneeded now
        pass

    def start_qr_thread(self):
        threading.Thread(target=self.qr_thread).start()
    def qr_thread(self):
        # This is the code executing in the new thread.
        #
        # cmd = 'pifacedigitalio(Relay(0)Ligth_on)'
        if RELAY_METHOD == 'piface':
            pifacedigital = pifacedigitalio.PiFaceDigital()
            pifacedigital.output_pins[0].turn_on() # this command does the same thing..
            pifacedigital.leds[0].turn_on() # as this command
        elif RELAY_METHOD == 'gpio':
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(7, GPIO.OUT)
            GPIO.output(7, GPIO.HIGH)
            GPIO.output(7, GPIO.LOW)

        if os.uname()[4].startswith("arm"):
            cmd = '/home/pi/Prog/zbar-build/test/a.out'
        else:
            cmd = 'zbarcam --prescale=320x320 /dev/video0'

        execute = pexpect.spawn(cmd, [], 300)
        # qr_code = os.system(cmd)
        # print qr_code
        # self.qr_thread_update_label_text(qr_code)
        # # Note: infinite looooop

        while True:
            # if self.stop.is_set():
            #     print "cancel qr scan"
            #     execute.close(True)
            #     break
            # else:
            #     print "wtf"
            try:
                execute.expect('\n')
                # Get last line fron expect
                line = execute.before
                print(line)
                if os.uname()[4].startswith("arm"):
                    if line != "" and line != None and line.startswith("decoded QR-Code symbol"):
                        self.qr_thread_update_label_text(line[22:])
                        # wal.close()
                        print("found qr: %s" % line[22:])
                        execute.close(True)
                        if RELAY_METHOD == 'piface':
                            # pifacedigital(ligth_off)
                            pifacedigital.output_pins[0].turn_off()  # this command does the same thing..
                            pifacedigital.leds[0].turn_off()  # as this command
                        elif RELAY_METHOD == 'gpio':
                            GPIO.output(7, GPIO.HIGH)
                        break
                else:
                    if line != "" and line != None and line.startswith("QR-Code:"):
                        self.qr_thread_update_label_text(line[8:])
                        execute.close(True)
                        if RELAY_METHOD == 'piface':
                            # pifacedigital(ligth_off)
                            pifacedigital.output_pins[0].turn_off()  # this command does the same thing..
                            pifacedigital.leds[0].turn_off()  # as this command
                        elif RELAY_METHOD == 'gpio':
                            GPIO.output(7, GPIO.HIGH)
                        break
            except pexpect.EOF:
                # Ok maybe not a complete infinite loooop but you get what i mean
                break
            except pexpect.TIMEOUT:
                print("timeout")
                break
        return
    ###@mainthread
    def qr_thread_update_label_text(self, new_text):
        label = self.root_manager.get_screen('buy').ids["'to_address'"]
        text = str(new_text)
        print("the text")
        print(text)
        text = text.replace('\"', '').strip()
        print(text)
        address = text.split(":")
        if address[0] == "bitcoin":
            label.text = address[1].rstrip()
            print(address[1])
            self.root_manager.current = 'buy'
            self.start_cashin_thread()

            #send call to backend with currency and customer crypto address
            print("CHECK THIS YO")
            print(self.current_btm_process_id)
            self.call_create_initial_buy_order_task(self.current_btm_process_id, address[1].rstrip(), address[0])
        else:
            label.text = "Invalid QR Code"

    def stop_scanning(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        print("set self.stop.set")
        self.stop_scan.set()

    def start_cashin_thread(self):
        threading.Thread(target=self.cashin_thread).start()
    def cashin_thread(self):
        """Run Worker Thread."""
        k = eSSP.eSSP('/dev/ttyUSB0')
        print(k.sync())
        print(k.enable_higher_protocol())
        print(k.set_inhibits(k.easy_inhibit([1, 1, 1, 1]), '0x00'))
        print(k.enable())
        #Publisher().subscribe(self.stoprun, "stoprun")
        var = 1
        i = 0
        #self.stopflag = False


        while not self.stopcashin.is_set():
            poll = k.poll()

            if len(poll) > 1:
                if len(poll[1]) == 2:
                    print(poll[1][0])
                    if poll[1][0] == '0xef':
                        if poll[1][1] == 1 or poll[1][1] == 3:
                            while i < 2:
                                k.hold()
                                print("Hold " + str(i))
                                time.sleep(0.5)
                                i += 1
                    if poll[1][0] == '0xef':
                        print("Read on Channel " + str(poll[1][1]))
                    if poll[1][0] == '0xe6':
                        print("Fraud on Channel " + str(poll[1][1]))

                    if poll[1][0] == '0xee':
                        print("Credit on Channel " + str(poll[1][1]))
                        if poll[1][1] == 1:
                            self.cashin_update_label_text("CHF:10")
                            #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:10"), -1)
                        if poll[1][1] == 2:
                            self.cashin_update_label_text("CHF:20")
                            #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:20"), -1)
                        if poll[1][1] == 3:
                            self.cashin_update_label_text("CHF:50")
                            #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:50"), -1)
                        if poll[1][1] == 4:
                            self.cashin_update_label_text("CHF:100")
                            #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:100"), -1)
                        if poll[1][1] == 5:
                            self.cashin_update_label_text("CHF:200")
                            #Clock.schedule_once(partial(self.cashin_update_label_text, "CHF:200"), -1)
                        #if poll[1][1] == 6:
                        #    wx.CallAfter(self.SendInfo, "CHF:200")
                        #wx.CallAfter(self.SendInfo, k.unit_data())
                    i = 0

            time.sleep(0.5)
        self.stop.clear()
        self.stop_scan.clear()
        self.stopcashin.clear()
        #process the transaction

        #get the total, hacky for now
        total_quote_label = self.root.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1])
        if newtotal > 0:
            #and the addy
            address_label = self.root.get_screen('buy').ids["'to_address'"]

            headers = {'Authorization': 'ApiKey firstmachine:GUWH8Fh4q2byrwashcrnwas0vnsufwby8VBEAUSV', 'Accept': 'application/json', 'Content-Type': 'application/json'}
            payload = {'amount': str(newtotal), 'currency': 'CHF', 'reference':'', 'status':'RCVE', 'order':{'comment':""}, 'withdraw_address':{'address':address_label.text}}

            r = requests.post("https://secure.atm4coin.com/api/v1/input_transaction/", headers=headers, data=json.dumps(payload))
            print(r.text)

            #reset the labels
            label = self.root.get_screen('buy').ids["'cashin10'"]
            label.text = 'x'+str(0)
            label = self.root.get_screen('buy').ids["'cashin20'"]
            label.text = 'x'+str(0)
            label = self.root.get_screen('buy').ids["'cashin50'"]
            label.text = 'x'+str(0)
            label = self.root.get_screen('buy').ids["'cashin100'"]
            label.text = 'x'+str(0)
            label = self.root.get_screen('buy').ids["'cashin200'"]
            label.text = 'x'+str(0)

            total_quote_label = self.root.get_screen('buy').ids["'total_quote'"]
            total_quote_label.text = '[font=MyriadPro-Bold.otf][b]'+str(0)+' Fr. = '+str(0)+' BTC[/b][/font]'

        return
    #@mainthread
    def cashin_update_label_text(self, new_credit):
        credit = str(new_credit)
        cr = credit.split(":")
        total_quote_label = self.root_manager.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1]) + int(cr[1])
        newtotalquote = Decimal(newtotal) / Decimal(self.current_ticker)
        newtotalquote_rounded = newtotalquote.quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
        total_quote_label.text = '[font=MyriadPro-Bold.otf][b]'+str(newtotal)+' Fr. = '+str(newtotalquote_rounded)+' BTC[/b][/font]'

        amount_sending_finished_label = self.root_manager.get_screen('buyfinish').ids["'amount_sending_finished'"]
        amount_sending_finished_label.text = 'WE ARE SENDING YOUR '+str(newtotalquote_rounded)+' BITCOINS'

        if cr[1] == "10":
            #self.channel1_count += 1
            label = self.root_manager.get_screen('buy').ids["'cashin10'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)

            #totallabel = self.get_screen('buy').ids["'total_quote'"]
            #totallabel.text = '[font=MyriadPro-Bold.otf][b]0 Fr. = 0 BTC[/b][/font]'
        if cr[1] == "20":
            #self.channel2_count += 1
            label = self.root_manager.get_screen('buy').ids["'cashin20'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "50":
            #self.channel3_count += 1
            label = self.root_manager.get_screen('buy').ids["'cashin50'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "100":
            #self.channel4_count += 1
            label = self.root_manager.get_screen('buy').ids["'cashin100'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "200":
            #self.channel5_count += 1
            label = self.root_manager.get_screen('buy').ids["'cashin200'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)

    ###@mainthread
    def generate_thread_update_label_text(self, new_text):
        label = self.get_screen('generate').ids["'generate_status'"]
        text = str(new_text)
        print("the text")
        print(text)
        label.text = text

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(new_text)
        qr.make(fit=True)
        img = self.get_screen('generate').ids["'generate_qr'"]
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
        self.get_screen('generate').ids["'generate_qr'"].source = os.path.join('tmp', 'qr.png')


    def stop_scanning(self):
        print("set self.stop.set")
        self.stop_scan.set()
    def stop_cashin(self):
        print("set stop.cashin")
        self.stopcashin.set()



# def mainthread(func):
#     def delayed_func(*args):
#         def callback_func(dt):
#             func(*args)
#         Clock.schedule_once(callback_func, 0)
#     return delayed_func

port = '5556'

class ZmqThread(Thread):
    def __init__(self, app):
        super(ZmqThread, self).__init__()
        self.app = app
        self.daemon = True

    def run(self):
        app = self.app
        zctx = zmq.Context()
        zsock = zctx.socket(zmq.SUB)
        zsock.connect('tcp://localhost:{}'.format(port))
        zsock.setsockopt(zmq.SUBSCRIBE,'priceticker')


        while True:
            topic, msg = zsock.recv_multipart()
            Logger.info('   Topic: %s, msg:%s' % (topic, msg))

            app.on_message(msg)


class AtmClientApp(App):
    # def stop_scan(self):
    #     # The Kivy event loop is about to stop, set a stop signal;
    #     # otherwise the app window will close, but the Python process will
    #     # keep running until all secondary threads exit.
    #     self.root.stop_scan.set()

    price = ObjectProperty({'buy_price': 0, 'sell_price': 0})
    l = ObjectProperty(strictyaml.load("lang.yaml").data['English'])

    def zmq_connect(self):
        self._zthread = ZmqThread(self)
        self._zthread.start()

    @mainthread
    def on_message(self, data):
        print(data)
        self.price = json.loads(data)

    @mainthread
    def change_language(self, lang):
        print("change language to %s" % lang)
        self.l = self.lang[lang]
        print(self.l)

    def build(self):
        self.zmq_connect()


        self.lang = strictyaml.load("lang.yaml").data
        #self.lang = yaml.load(open("lang.yaml", "r"))
        self.LANGUAGES = [language for language in self.lang]
        print(self.LANGUAGES)
        # self.language = self.lang

        self.root = RootWidget()

        # eg
        self.transactions = {
            'id':
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


        Logger.info('Frontend Started')

        self.root.root_manager.current = 'welcome'

        return self.root


if __name__ == '__main__':
    AtmClientApp().run()
