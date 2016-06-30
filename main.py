__version__ = "1.2.0"

from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
#from kivy.uix.camera import Camera


# Kivy's install_twisted_rector MUST be called early on!
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

#for settings window
from kivy.uix.settings import SettingsWithSidebar

#from settingsjson import settings_json



import time
import random


from kivy.clock import Clock, mainthread
from functools import partial
import threading
import time
import pexpect
#for Note Validator
import eSSP
from decimal import Decimal, ROUND_UP, ROUND_DOWN

import requests
import json

#for fullscreen
#from kivy.core.window import Window
#Window.size = (800, 600)
#Window.fullscreen = False

from kivy.config import Config
Config.set('graphics', 'fullscreen', 'fake')
Config.set('kivy', 'exit_on_escape', 1)
Config.set('kivy', 'desktop', 1)

Config.write()

class MyComponent(ApplicationSession):

    """
    A simple WAMP app component run from the Kivy UI.
    """

    def onJoin(self, details):
        print("session ready", self.config.extra)

        # get the Kivy UI component this session was started from
        ui = self.config.extra['ui']
        ui.on_session(self)
        
        # subscribe to WAMP PubSub event and call the Kivy UI component when events are received
        self.subscribe(ui.root.update_ticker, u"CHF")
        self.subscribe(ui.root.update_sell_ticker, u"CHFSELL")

class ColorDownButton(Button):
    """
    Button with a possibility to change the color on on_press (similar to background_down in normal Button widget)
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

class ColourScreen(Screen):
    colour = ListProperty([1., 0., 0., 1.])

class MyScreenManager(ScreenManager):

    stop = threading.Event()
    stop_scan = threading.Event()
    current_ticker = Decimal(0)
    
    def start_sendcoins_thread(self):
        threading.Thread(target=self.sendcoins_thread).start()
    def sendcoins_thread(self):
        # Worker thread to call the backend when transaction complete to actually send the coins
        pass
    def start_qr_thread(self):
        threading.Thread(target=self.qr_thread).start()
    def qr_thread(self):
        # This is the code executing in the new thread.
        #cmd = 'zbarcam --prescale=320x320 /dev/video0'
        cmd = '/home/pi/Prog/zbar-build/test/a.out'
        execute = pexpect.spawn(cmd, [], 300)
        #qr_code = os.system(cmd)
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
                print line
                print "contains qr: "
                print line.startswith("QR-Code:")
                if line != "" and line != None and line.startswith("decoded QR-Code symbol"):
                #if line != "" and line != None and line.startswith("QR-Code:"):
                    self.qr_thread_update_label_text(line[22:])
                    #wal.close()
                    execute.close(True)
                    break
            except pexpect.EOF:
                # Ok maybe not a complete infinite loooop but you get what i mean
                break
            except pexpect.TIMEOUT:
                print "timeout"
                break
        return
    @mainthread
    def qr_thread_update_label_text(self, new_text):
        label = self.get_screen('buy').ids["'to_address'"]
        text = str(new_text)
        print "the text"
        print text
        text = text.replace('\"','')
        address = text.split(":")
        if address[0] == "bitcoin":
            label.text = address[1].rstrip()
            print address[1]
            self.current = 'buy'
            self.start_cashin_thread()
        else:
            label.text = "Invalid QR Code"         
    
    def stop_scanning(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        print "set self.stop.set"
        self.stop.set()

    def start_cashin_thread(self):
        threading.Thread(target=self.cashin_thread).start()
    def cashin_thread(self):
        """Run Worker Thread."""
        k = eSSP.eSSP('/dev/ttyUSB0')
        print k.sync()
        print k.enable_higher_protocol()
        print k.set_inhibits(k.easy_inhibit([1, 1, 1, 1]), '0x00')
        print k.enable()
        #Publisher().subscribe(self.stoprun, "stoprun")
        var = 1
        i = 0
        #self.stopflag = False
        

        while not self.stop.is_set():
            poll = k.poll()
            
            if len(poll) > 1:
                if len(poll[1]) == 2:
                    print poll[1][0]
                    if poll[1][0] == '0xef':
                        if poll[1][1] == 1 or poll[1][1] == 3:
                            while i < 2:
                                k.hold()
                                print "Hold " + str(i)
                                time.sleep(0.5)
                                i += 1
                    if poll[1][0] == '0xef':
                        print "Read on Channel " + str(poll[1][1])
                    if poll[1][0] == '0xe6':
                        print "Fraud on Channel " + str(poll[1][1])
                                            
                    if poll[1][0] == '0xee':
                        print "Credit on Channel " + str(poll[1][1])
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
        #process the transaction

        #get the total, hacky for now
        total_quote_label = self.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1])
        if newtotal > 0:
            #and the addy
            address_label = self.get_screen('buy').ids["'to_address'"]

            headers = {'Authorization': 'ApiKey firstmachine:GUWH8Fh4q2byrwashcrnwas0vnsufwby8VBEAUSV', 'Accept': 'application/json', 'Content-Type': 'application/json'}
            payload = {'amount': str(newtotal), 'currency': 'CHF', 'reference':'', 'status':'RCVE', 'order':{'comment':""}, 'withdraw_address':{'address':address_label.text}}
            
            r = requests.post("https://secure.atm4coin.com/api/v1/input_transaction/", headers=headers, data=json.dumps(payload))
            print r.text

            #reset the labels
            label = self.get_screen('buy').ids["'cashin10'"]
            label.text = 'x'+str(0)
            label = self.get_screen('buy').ids["'cashin20'"]
            label.text = 'x'+str(0)
            label = self.get_screen('buy').ids["'cashin50'"]
            label.text = 'x'+str(0)
            label = self.get_screen('buy').ids["'cashin100'"]
            label.text = 'x'+str(0)
            label = self.get_screen('buy').ids["'cashin200'"]
            label.text = 'x'+str(0)

            total_quote_label = self.get_screen('buy').ids["'total_quote'"]
            total_quote_label.text = '[font=MyriadPro-Bold.otf][b]'+str(0)+' Fr. = '+str(0)+' BTC[/b][/font]'

        return   
    #@mainthread
    def cashin_update_label_text(self, new_credit):
        credit = str(new_credit)
        cr = credit.split(":")
        total_quote_label = self.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1]) + int(cr[1])
        newtotalquote = Decimal(newtotal) / Decimal(self.current_ticker)
        newtotalquote_rounded = newtotalquote.quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
        total_quote_label.text = '[font=MyriadPro-Bold.otf][b]'+str(newtotal)+' Fr. = '+str(newtotalquote_rounded)+' BTC[/b][/font]'

        amount_sending_finished_label = self.get_screen('buyfinish').ids["'amount_sending_finished'"]
        amount_sending_finished_label.text = 'WE ARE SENDING YOUR '+str(newtotalquote_rounded)+' BITCOINS'

        if cr[1] == "10":
            #self.channel1_count += 1
            label = self.get_screen('buy').ids["'cashin10'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)

            #totallabel = self.get_screen('buy').ids["'total_quote'"]
            #totallabel.text = '[font=MyriadPro-Bold.otf][b]0 Fr. = 0 BTC[/b][/font]'
        if cr[1] == "20":
            #self.channel2_count += 1
            label = self.get_screen('buy').ids["'cashin20'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "50":
            #self.channel3_count += 1
            label = self.get_screen('buy').ids["'cashin50'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "100":
            #self.channel4_count += 1
            label = self.get_screen('buy').ids["'cashin100'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "200":
            #self.channel5_count += 1
            label = self.get_screen('buy').ids["'cashin200'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
             
    def new_colour_screen(self):
        name = str(time.time())
        s = ColourScreen(name=name,
                         colour=[random.random() for _ in range(3)] + [1])
        self.add_widget(s)
        self.current = name
    def update_ticker(self, msg, hacky_fix=None):
        """
        Called from WAMP app component when message was received in a PubSub event.
        """
        label = self.get_screen('welcome').ids["'ticker_label'"]
        label.text = '[b]FOR '+msg+' Fr.[/b]'
        btc_buy_label = self.get_screen('welcome').ids["'btc_buy'"]
        btc_buy_label.text = msg
        btc_buyfinish_label = self.get_screen('buy').ids["'buyfinishbtcprice'"]
        btc_buyfinish_label.text = '[font=MyriadPro-Bold.otf][b]1 BTC = '+msg+' BTC[/b][/font]'
        self.current_ticker = Decimal(msg)
    def update_sell_ticker(self, msg, hacky_fix=None):
        """
        Called from WAMP app component when message was received in a PubSub event.
        """
        btc_sell_label = self.get_screen('welcome').ids["'btc_sell'"]
        btc_sell_label.text = msg

root_widget = Builder.load_string('''
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
MyScreenManager:
    transition: SlideTransition()
    WelcomeScreen:
    VerifyScreen:
    ScanWalletScreen:
    BuyScreen:
    BuyFinishScreen:
    SellSelectScreen:


<WelcomeScreen>:
    id: 'welcome_screen'
    name: 'welcome'
    Image:
        source: 'bg2.png'
        allow_stretch: False
        keep_ratio: False
        size_hint: 1, 1
    GridLayout:
        cols:2
        padding: 5
        spacing: 2
        GridLayout:
            cols: 1
            width: 180
            spacing: 10
            size_hint: .2,1
            #Label:
            #    text: 'Language'
            #    font_size: 20
            #    height: 0.25
            #    color: 0,0,0,1
            Button:
                background_normal:'flags/large/EN.png'
                background_down:'flags/large/EN.png'
            Button:
                background_normal:'flags/large/FR.png'
                background_down:'flags/large/FR.png'
            Button:
                background_normal:'flags/large/DE.png'
                background_down:'flags/large/DE.png'
            Button:
                background_normal:'flags/large/IT.png'
                background_down:'flags/large/IT.png'
            Button:
                background_normal:'flags/large/ES.png'
                background_down:'flags/large/ES.png'
            Button:
                background_normal:'flags/large/PT.png'
                background_down:'flags/large/PT.png'
        BoxLayout:
            orientation: 'vertical'
            padding: 40
            spacing: 10,0
            height: 10,0
            Label:
                text: '[b][font=MyriadPro-Bold.otf]1 BITCOIN[/font][/b]'
                markup: True
                halign: 'left'
                text_size: self.size
                size_hint: (1, None)
                color: 1,1,1,1
                font_size: 70
            Label:
                id: 'ticker_label'
                text: '[b]FOR 0 Fr.[/b]'
                markup: True
                halign: 'left'
                text_size: self.size
                size_hint: (1, None)
                height: 70
                color: 1,1,1,1
                font_size: 70
            #pricing/ticker grid
            GridLayout:
                cols: 3
                spacing: 10,0
                Label:
                    text: '[b]Currency[/b]'
                    markup: True
                    font_size: 40
                    color: 0,0,0,1
                    background_color: 0,0,0,0
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 0.4
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: '[b]We Sell[/b]'
                    markup: True
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.4
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: '[b]We Buy[/b]'
                    markup: True
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.4
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: 'BTC'
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    id: 'btc_buy'
                    text: '0.00'
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    id: 'btc_sell'
                    text: '0.00'
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos
                Label:
                    text: ''
                    font_size: 40
                    color: 0,0,0,1
                    canvas.before:
                        Color:
                            rgba: 1,1,1,0.2
                        Rectangle:
                            size: self.size
                            pos: self.pos


            BoxLayout:
                height: 100
                spacing: 10
                padding: 0,10
                size_hint: (1, None)
                ColorDownButton:
                    text: 'SEND'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    #on_release: app.root.current = 'verify'
                ColorDownButton:
                    text: 'BITCOIN'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    on_release: app.root.current = 'scanwallet'; app.root.start_qr_thread()
                ColorDownButton: 
                    text: 'CASH'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    #on_release: app.open_settings()
                    #on_release: app.root.current = 'sellselect'

# <VerifyScreen>:
#     name: 'verify'
#     Image:
#         source: 'bg2.png'
#         allow_stretch: True
#         keep_ratio: False
#     BoxLayout:
#         orientation: 'vertical'
#         padding: 20
#         spacing: 5
#         background_color: 1,0,0,0
#         # Label:
#         #     text: 'Please enter your phone number'
#         #     font_size: 30
#         #     size_hint: 1,0.4
#         #     color: 0.5,0.5,0.5,1
#         TextInput:
#             id: input
#             hint_text: 'Please enter your phone number'
#             size_hint: 1, None
#             readonly: True
#             multiline: False
#             font_size: 30
#             border: 1,1,1,1

#         GridLayout:
#             rows: 4
#             cols: 3
#             spacing: 10
#             padding: 150, 10
#             ColorDownButton:
#                     text: '1'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '2'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '3'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '4'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '5'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '6'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '7'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '8'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '9'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: 'C'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '0'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#             ColorDownButton:
#                     text: '+'
#                     color: 1,1,1,0
#                     background_color: 0,0,0,0
#                     background_color_normal: 0,0,0,0
#                     background_color_down: 0,0,0,0
#                     font_size: 26
#                     on_press: input.text += self.text
#         BoxLayout:
#             height: 100
#             size_hint: (1, None)
#             Button:
#                 text: 'Go Back'
#                 font_size: 30
#                 on_release: app.root.current = 'welcome'
#             Button:
#                 text: 'Continue'
#                 font_size: 30
#                 on_release: app.root.current = 'scanwallet'

<ScanWalletScreen>:
    name: 'scanwallet'
    Image:
        source: 'bg2.png'
        allow_stretch: True
        keep_ratio: False
        size_hint: 1, 1
    GridLayout:
        cols:2
        padding: 5
        spacing: 2
        GridLayout:
            cols: 1
            width: 180
            spacing: 10
            size_hint: .2,1
            #Label:
            #    text: 'Language'
            #    font_size: 20
            #    height: 0.25
            #    color: 0,0,0,1
            Button:
                background_normal:'flags/large/EN.png'
                background_down:'flags/large/EN.png'
            Button:
                background_normal:'flags/large/FR.png'
                background_down:'flags/large/FR.png'
            Button:
                background_normal:'flags/large/DE.png'
                background_down:'flags/large/DE.png'
            Button:
                background_normal:'flags/large/IT.png'
                background_down:'flags/large/IT.png'
            Button:
                background_normal:'flags/large/ES.png'
                background_down:'flags/large/ES.png'
            Button:
                background_normal:'flags/large/PT.png'
                background_down:'flags/large/PT.png'
        BoxLayout:
            orientation: 'vertical'
            padding: 10,0
            spacing: 10,0
            Label:
                text: '[b][font=MyriadPro-Bold.otf]WALLET SCAN[/font][/b]'
                markup: True
                halign: 'left'
                text_size: self.size
                size_hint: (1, None)
                color: 1,1,1,1
                font_size: 70
            Label:
                text: '[font=MyriadPro-Bold.otf][b]Please present your QR code[/b][/font]'
                halign: 'left'
                valign: 'top'
                height: 50
                line_height: 0.5
                markup: True
                size_hint: (1, None)
                color: 0,0,0,1
                font_size: 50
                text_size: self.size
                
            #pricing/ticker grid

            GridLayout:
                cols: 2
                Label:
                    text: 'please wait, camera loading ..'
                    width: 20
                    size_hint: (20, 50)
                    canvas:
                        Color:
                            rgba: 0, 0, 0, 0.4
                        Rectangle:
                            size: self.size
                            pos: self.pos
                
                Image:
                    source: 'phoneqr.png'
                    size_hint: (10, 10)
                    width: 10
                    height: 10
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 0.4
                        Rectangle:
                            size: self.size
                            pos: self.pos
            
            BoxLayout:
                height: 100
                spacing: 10
                padding: 10
                size_hint: (1, None)
                Label:
                    text: ''
                Label:
                    text: ''
                Label:
                    text: ''
                # ColorDownButton:
                #     text: 'CANCEL'
                #     color: 1,1,1,0
                #     background_color: 0,0,0,0
                #     background_olor_normal: 0,0,0,0
                #     background_color_down: 0,0,0,0
                #     font_size: 30
                # ColorDownButton:
                #     text: 'SCAN'
                #     color: 1,1,1,0
                #     background_color_normal: 0,0,0,0
                #     background_color_down: 0,0,0,0
                #     font_size: 30
                #     #on_release: app.root.current = 'buy'
                # ColorDownButton: 
                #     text: 'CANCEL'
                #     color: 1,1,1,0
                #     background_color_normal: 0,0,0,0
                #     background_color_down: 0,0,0,0
                #     font_size: 30
                #     #on_release: app.root.current = 'welcome'; app.root.stop_scanning()


<BuyScreen>:
    name: 'buy'
    Image:
        source: 'bg2.png'
        allow_stretch: True
        keep_ratio: False
        size_hint: 1, 1
    GridLayout:
        cols:2
        padding: 5
        spacing: 2
        GridLayout:
            cols: 1
            width: 180
            spacing: 10
            size_hint: .2,1
            #Label:
            #    text: 'Language'
            #    font_size: 20
            #    height: 0.25
            #    color: 0,0,0,1
            Button:
                background_normal:'flags/large/EN.png'
                background_down:'flags/large/EN.png'
            Button:
                background_normal:'flags/large/FR.png'
                background_down:'flags/large/FR.png'
            Button:
                background_normal:'flags/large/DE.png'
                background_down:'flags/large/DE.png'
            Button:
                background_normal:'flags/large/IT.png'
                background_down:'flags/large/IT.png'
            Button:
                background_normal:'flags/large/ES.png'
                background_down:'flags/large/ES.png'
            Button:
                background_normal:'flags/large/PT.png'
                background_down:'flags/large/PT.png'
        BoxLayout:
            orientation: 'vertical'
            padding: 10,0
            spacing: 10,0
            height: 10
            Label:
                text: '[b][font=MyriadPro-Bold.otf]INSERT CASH[/font][/b]'
                markup: True
                halign: 'left'
                text_size: self.size
                size_hint: (1, None)
                color: 1,1,1,1
                font_size: 70
            Label:
                text: '[font=MyriadPro-Bold.otf][b]Insert fiat crap in machine[/b][/font]'
                halign: 'left'
                valign: 'top'
                markup: True
                size_hint: (1, None)
                height: 50
                color: 0,0,0,1
                font_size: 50
                text_size: self.size
            Label:
                id: 'total_quote'
                text: '[font=MyriadPro-Bold.otf][b]0 Fr. = 0 BTC[/b][/font]'
                halign: 'left'
                valign: 'top'
                markup: True
                size_hint: (1, None)
                height: 60
                color: 1,1,1,1
                font_size: 60
                text_size: self.size

            BoxLayout:
                orientation: 'vertical'
                spacing: 0,0
                canvas.before:
                    Color:
                        rgba: 1,1,1,0.2
                    Rectangle:
                        size: self.size
                        pos: self.pos
                Label:
                    text: '[font=MyriadPro-Bold.otf][b]FIAT MONEY "BANQUE NATIONALE SUISSE"[/b][/font]'
                    halign: 'left'
                    valign: 'top'
                    markup: True
                    size_hint: (1, None)
                    font_size: 26
                    color: 0,0,0,1
                BoxLayout:
                    spacing: 10,0
                    padding: 50,0
                    GridLayout:
                        cols: 2
                        spacing: 10,0
                        size_hint: .3,1
                        Label:
                            text: '10'
                            font_size: 30
                            color: 1,1,1,1
                        Label:
                            id: 'cashin10'
                            text: 'x0'
                            font_size: 30
                            color: 1,1,1,1
                            halign: 'left'
                            canvas.before:
                                Color:
                                    rgba: 0, 0, 0, 0.2
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                        Label:
                            text: '20'
                            font_size: 30
                            color: 1,1,1,1
                        Label:
                            id: 'cashin20'
                            text: 'x0'
                            font_size: 30
                            color: 1,1,1,1
                            canvas.before:
                                Color:
                                    rgba: 0, 0, 0, 0.2
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                        Label:
                            text: '50'
                            font_size: 30
                            color: 1,1,1,1
                        Label:
                            id: 'cashin50'
                            text: 'x0'
                            font_size: 30
                            color: 1,1,1,1
                            canvas.before:
                                Color:
                                    rgba: 0, 0, 0, 0.2
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                        Label:
                            text: '100'
                            font_size: 30
                            color: 1,1,1,1
                        Label:
                            id: 'cashin100'
                            text: 'x0'
                            font_size: 30
                            color: 1,1,1,1
                            canvas.before:
                                Color:
                                    rgba: 0, 0, 0, 0.2
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                        Label:
                            text: '200'
                            font_size: 30
                            color: 1,1,1,1
                        Label:
                            id: 'cashin200'
                            text: 'x0'
                            font_size: 30
                            color: 1,1,1,1
                            canvas.before:
                                Color:
                                    rgba: 0, 0, 0, 0.2
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            id: 'buyfinishbtcprice'
                            text: '[font=MyriadPro-Bold.otf][b]1 BTC = 235 BTC[/b][/font]'
                            markup: True
                            halign: 'right'
                            font_size: 40
                            text_size: self.size
                            color: 1,1,1,1
                            
                        Label:
                            text: '[font=MyriadPro-Bold.otf][b]Limite 500 Fr.[/b][/font]'
                            markup: True
                            halign: 'right'
                            font_size: 40
                            text_size: self.size
                            color: 1,1,1,1
                    
                Label:
                    padding: 0,0 
                    spacing: 0
                    id: 'to_address'
                    text: 'N/A'
                    font_size: 26
                    color: 1,1,1,1

            BoxLayout:
                height: 100
                spacing: 10
                padding: 10
                size_hint: (1, None)
                ColorDownButton:
                    text: 'CANCEL'
                    color: 1,1,1,0
                    background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0
                    background_color_down: 0,0,0,0
                    font_size: 30
                ColorDownButton:
                    text: 'SCAN'
                    color: 1,1,1,0
                    background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0
                    background_color_down: 0,0,0
                    font_size: 30
                ColorDownButton: 
                    text: 'FINISH'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    on_release: app.root.current = 'buyfinish'; app.root.stop.set()

<BuyFinishScreen>:
    name: 'buyfinish'
    Image:
        source: 'bg2.png'
        allow_stretch: True
        keep_ratio: False
        size_hint: 1, 1
    GridLayout:
        cols:2
        padding: 5
        spacing: 2
        GridLayout:
            cols: 1
            width: 180
            spacing: 10
            size_hint: .2,1
            #Label:
            #    text: 'Language'
            #    font_size: 20
            #    height: 0.25
            #    color: 0,0,0,1
            Button:
                background_normal:'flags/large/EN.png'
                background_down:'flags/large/EN.png'
            Button:
                background_normal:'flags/large/FR.png'
                background_down:'flags/large/FR.png'
            Button:
                background_normal:'flags/large/DE.png'
                background_down:'flags/large/DE.png'
            Button:
                background_normal:'flags/large/IT.png'
                background_down:'flags/large/IT.png'
            Button:
                background_normal:'flags/large/ES.png'
                background_down:'flags/large/ES.png'
            Button:
                background_normal:'flags/large/PT.png'
                background_down:'flags/large/PT.png'
        BoxLayout:
            orientation: 'vertical'
            padding: 40
            spacing: 10
            height: 10
            Label:
                text: '[b][font=MyriadPro-Bold.otf]CONFIRMATION[/font][/b]'
                markup: True
                halign: 'left'
                text_size: self.size
                size_hint: (1, None)
                color: 1,1,1,1
                font_size: 70
            Label:
                text: '[font=MyriadPro-Bold.otf][b]Thank You[/b][/font]'
                halign: 'left'
                valign: 'top'
                markup: True
                size_hint: (1, None)
                color: 0,0,0,1
                font_size: 50
                text_size: self.size
            #confirmation box 
            BoxLayout:
                id: 'amount_sending_finished'
                orientation: 'vertical'
                size_hint: (1, None)
                Label:
                    text: 'WE ARE SENDING YOUR BITCOINS'
                    color: 0,0,0,1
            BoxLayout:
                height: 100
                spacing: 10
                size_hint: (1, None)
                ColorDownButton:
                    text: 'CANCEL'
                    color: 1,1,1,0
                    background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0
                    background_color_down: 0,0,0,0
                    font_size: 30
                ColorDownButton:
                    text: 'SCAN'
                    color: 1,1,1,0
                    background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0
                    background_color_down: 0,0,0,0
                    font_size: 30
                ColorDownButton: 
                    text: 'CLOSE'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    on_release: app.root.current = 'welcome'

<SellSelectScreen>:
    name: 'sellselect'
    Image:
        source: 'bg2.png'
        allow_stretch: True
        keep_ratio: False
        size_hint: 1, 1
    GridLayout:
        cols:2
        padding: 5
        spacing: 2
        GridLayout:
            cols: 1
            width: 180
            spacing: 10
            size_hint: .2,1
            #Label:
            #    text: 'Language'
            #    font_size: 20
            #    height: 0.25
            #    color: 0,0,0,1
            Button:
                background_normal:'flags/large/EN.png'
                background_down:'flags/large/EN.png'
            Button:
                background_normal:'flags/large/FR.png'
                background_down:'flags/large/FR.png'
            Button:
                background_normal:'flags/large/DE.png'
                background_down:'flags/large/DE.png'
            Button:
                background_normal:'flags/large/IT.png'
                background_down:'flags/large/IT.png'
            Button:
                background_normal:'flags/large/ES.png'
                background_down:'flags/large/ES.png'
            Button:
                background_normal:'flags/large/PT.png'
                background_down:'flags/large/PT.png'
        BoxLayout:
            orientation: 'vertical'
            padding: 10,0
            spacing: 10,0
            height: 10
            Label:
                text: '[font=MyriadPro-Bold.otf][b]BUY FIAT MONEY[/b][/font]'
                halign: 'left'
                valign: 'top'
                markup: True
                size_hint: (1, None)
                height: 50
                color: 0,0,0,1
                font_size: 50
                text_size: self.size
            Label:
                text: '[font=MyriadPro-Bold.otf][b]220 Fr. = 0.91245678 BTC[/b][/font]'
                halign: 'left'
                valign: 'top'
                markup: True
                size_hint: (1, None)
                height: 60
                color: 1,1,1,1
                font_size: 60
                text_size: self.size

            BoxLayout:
                orientation: 'vertical'
                spacing: 10,0
                canvas.before:
                    Color:
                        rgba: 1,1,1,0.2
                    Rectangle:
                        size: self.size
                        pos: self.pos
                BoxLayout:
                    spacing: 10,0
                    padding: 20
                    GridLayout:
                        cols: 3
                        spacing: 10
                        #size_hint: .3,1
                        ColorDownButton:
                            text: '20 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        ColorDownButton:
                            text: '200 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        Label:
                            markup: True
                            text: '[color=ffffff]1 BTC[/color] [color=1c6434]235CHF[/color]'
                            font_size: 35
                        ColorDownButton:
                            text: '20 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        ColorDownButton:
                            text: '200 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        Label:
                            markup: True
                            text: '[color=ffffff]Limit[/color]  [color=c11d24]500CHF[/color]'
                            font_size: 35
                        ColorDownButton:
                            text: '50 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        ColorDownButton:
                            text: '400 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        Label:
                            text:''
                        ColorDownButton:
                            text: '100 Fr.'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
                        ColorDownButton:
                            text: 'OTHER'
                            color: 1,1,1,1
                            background_color_normal: 0,0,0,0.4
                            background_color_down: 0,0,0,0.6
                            font_size: 30
                            on_release: app.root.current = 'verify'
            BoxLayout:
                height: 100
                spacing: 10
                padding: 10
                size_hint: (1, None)
                ColorDownButton:
                    text: 'CANCEL'
                    color: 1,1,1,1
                    #background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                ColorDownButton:
                    text: 'SCAN'
                    color: 1,1,1,0
                    background_color: 0,0,0,0
                    background_color_normal: 0,0,0,0
                    background_color_down: 0,0,0
                    font_size: 30
                ColorDownButton: 
                    text: 'FINISH'
                    color: 1,1,1,1
                    background_color_normal: 0,0,0,0.4
                    background_color_down: 0,0,0,0.6
                    font_size: 30
                    on_release: app.root.current = 'buyfinish'


#<BuyScreen>:
#    name: 'buy'
#    Image:
#        source: 'bg2.png'
#        allow_stretch: True
#        keep_ratio: False
#    BoxLayout:
#        orientation: 'vertical'
#        Label:
#            text: 'Please insert fiat crap!'
#            font_size: 30
#        BoxLayout:
#            height: 100
#            size_hint: (1, None)
#            Button:
#                text: 'Go Back'
#                font_size: 30
#                on_release: app.root.current = 'welcome'
#            Button:
#                text: 'Continue'
#                font_size: 30
#                on_release: app.root.new_colour_screen()

<ColourScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'colour {:.2},{:.2},{:.2} screen'.format(*root.colour[:3])
            font_size: 30
        Widget:
            canvas:
                Color:
                    rgba: root.colour
                Ellipse:
                    pos: self.pos
                    size: self.size
        BoxLayout:
            Button:
                text: 'goto first screen'
                font_size: 30
                on_release: app.root.current = 'welcome'
            Button:
                text: 'get random colour screen'
                font_size: 30
                on_release: app.root.new_colour_screen()
''')

class ScreenManagerApp(App):
    def stop_scan(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop_scan.set()
    def build(self):
        # WAMP session
        self.session = None

        # run our WAMP application component    #188.226.230.145
        runner = ApplicationRunner(url = u"ws://188.226.236.79:8080/ws", realm = u"realm1", extra = dict(ui=self))
        runner.run(MyComponent, start_reactor=False)

        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        setting = self.config.get('example', 'boolexample')
        root = root_widget
        return root_widget
        #return Interface()
    def on_session(self, session):
        """
        Called from WAMP session when attached to router.
        """
        self.print_message("WAMP session connected!")
        self.session = session


    # def send_message(self, *args):
    #     """
    #     Called from UI when user has entered text and pressed RETURN.
    #     """
    #     msg = self.textbox.text
    #     if msg and self.session:
    #         self.session.publish(u"com.example.kivy", str(self.textbox.text))
    #         self.textbox.text = ""

    def print_message(self, msg, test=None):
        print msg + "\n"
        #print test
    

    def build_config(self, config):
        config.setdefaults('example', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'pathexample': '/some/path'})

    #def build_settings(self, settings):
    #    settings.add_json_panel('Panel Name',
    #                            self.config,
    #                            data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        print config, section, key, value


ScreenManagerApp().run()
