__version__ = "1.3.0"


from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
# Kivy's install_twisted_rector MUST be called early on!
from kivy.support import install_twisted_reactor
install_twisted_reactor()


#from kivy.uix.camera import Camera
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty


from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from autobahn.wamp.types import CallOptions

from autobahn.wamp import auth

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition

#for settings window
from kivy.uix.settings import SettingsWithSidebar

#from settingsjson import settings_json



import time
import random


from kivy.clock import Clock###, mainthread
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

import crosstalk_client_settings
CROSSBAR_CLIENT_SETTER_TASKS = crosstalk_client_settings.CROSSBAR_CLIENT_SETTER_TASKS
CROSSBAR_CLIENT_WIDGET_GETTER_TASKS = crosstalk_client_settings.CROSSBAR_CLIENT_WIDGET_GETTER_TASKS
CROSSBAR_DOMAIN = crosstalk_client_settings.CROSSBAR_DOMAIN


PASSWORDS = {
    u'peter': u'secret1'
}
USER = "peter"

class WampComponent(ApplicationSession):

    """
    A simple WAMP app component run from the Kivy UI.
    """
    def onConnect(self):
      print("connected. joining realm {} as user {} ...".format(self.config.realm, USER))
      self.join(self.config.realm, [u"wampcra"], USER)

    def onChallenge(self, challenge):
        #print challenge
        if challenge.method == u"wampcra":
            if u'salt' in challenge.extra:
                print "deriving key"
                key = auth.derive_key(PASSWORDS[USER].encode('utf8'),
                                      challenge.extra['salt'].encode('utf8'),
                                      challenge.extra.get('iterations', 100),
                                      challenge.extra.get('keylen', 16))
                print key
            else:
                print "using password"
                key = PASSWORDS[USER].encode('utf8')
            signature = auth.compute_wcs(key, challenge.extra['challenge'].encode('utf8'))
            print signature.decode('ascii')
            return signature.decode('ascii')
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))

    def onJoin(self, details):
        print("session ready", self.config.extra)

        # get the Kivy UI component this session was started from
        ui = self.config.extra['ui']
        ui.on_session(self)
        
        # subscribe to WAMP PubSub event and call the Kivy UI component when events are received
        self.subscribe(ui.update_ticker, u"com.example.CHF")
        print("subscribe to CHF")
        #self.subscribe(ui.manager.update_sell_ticker, u"CHFSELL")


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


class MyScreenManager(ScreenManager):
    pass

    
    
# root_widget = Builder.load_string('''
# #:import SlideTransition kivy.uix.screenmanager.SlideTransition

# ''')

class RootWidget(FloatLayout):
    '''This the class representing your root widget.
       By default it is inherited from ScreenManager,
       you can use any other layout/widget depending on your usage.
    '''
    root_manager = ObjectProperty()
    current_btm_process_id = NumericProperty()

    def validate_phonenumber(self, cli):
      if len(cli) > 6:
        z = phonenumbers.parse(cli, None)
        try:
          r = phonenumbers.is_valid_number(z)
          return r
        except:
          return False

    #@inlineCallbacks
    def on_session(self, session):
        """
        Called from WAMP session when attached to Crossbar router.
        """
        self.print_message("WAMP session connected!")
        
        self.session = session

        self.root_manager.current = 'welcome'

    def print_message(self, msg, test=None):
        print msg + "\n"


    ### START SETTER TASKS STUFF ###

    def returnData(self, d, result_global_var):
      if result_global_var != 'None':
        setattr(self, result_global_var, int(d))
        print d
      return d
    #ns = {}
    #returnfunc = compile('def returnData(d):    return d', '<string>', 'exec')
    callopts = compile('from autobahn.wamp.types import CallOptions', '<string>', 'exec')
    #exec returnfunc in ns
    exec callopts in locals()
    for st in CROSSBAR_CLIENT_SETTER_TASKS:
      code = compile(st.get('cb_rpc')+' = lambda self, *args: self.session.call("'+'.'.join([CROSSBAR_DOMAIN,st.get('cb_rpc')])+'", *args, options=CallOptions(disclose_me = True)).addCallback(self.returnData, "'+st.get('result_global_var')+'")', '<string>', 'exec')
      exec code in locals()
      
    ### END SETTER TASKS STUFF ###

    ### START WIDGET GETTER TASKS STUFF ###
    def add_cb_widget(self, kv_widget, kv_container, item_id, text_field, **kwargs):
      ns = {}
      factoryimport = compile('from kivy.factory import Factory', '<string>', 'exec')
      exec factoryimport in ns
      widgetfactory = compile('widget = Factory.'+kv_widget+'()', '<string>', 'exec')
      exec widgetfactory in ns
      ns['widget'].id = str(item_id)
      widget = self.widget_properties(ns['widget'], **kwargs)
      if text_field != 'None':
        widget.text = kwargs[text_field]
      print "addming widget to " + kv_container
      addwidget = compile('self.'+kv_container+'.add_widget(widget)', '<string>', 'exec')
      exec addwidget in locals(), globals()
      
    def remove_all_cb_widgets(self, container):
        #self.pizzas_widget.clear_widgets()
        removewidget = compile('self.'+container+'.clear_widgets()', '<string>', 'exec')
        exec removewidget in locals()#, globals()
      
    def widget_properties(self, widget, **kwargs):
      for key in kwargs:
        setattr(widget, key, kwargs[key])
      return widget

    def returnWidgetData(self, d, kv_widget, kv_container, text_field):
      print "WIDGET DATA"
      print d
      r = json.loads(d)
      for item in r:
        self.add_cb_widget(kv_widget, kv_container, item.get("pk"), text_field, **item.get("fields"))
      return d

    for wgt in CROSSBAR_CLIENT_WIDGET_GETTER_TASKS:
      #nsp = {'pizzas_container': pizzas_container}
      
      nsp={}
      ic = compile('from autobahn.wamp.types import CallOptions', '<string>', 'exec')
      code = compile(wgt.get('cb_rpc')+' = lambda self, *args: self.session.call("'+'.'.join([CROSSBAR_DOMAIN,wgt.get('cb_rpc')])+'", *args, options=CallOptions(disclose_me = True)).addCallback(self.returnWidgetData, "'+wgt.get('kivy_widget')+'", "'+wgt.get('kivy_widget_container')+'", "'+wgt.get('txt_field')+'")', '<string>', 'exec')
      exec ic in nsp
      exec code in nsp#locals()
      vars()[wgt.get('cb_rpc')] = nsp[wgt.get('cb_rpc')]
    
    ### END WIDGET GETTER TASKS STUFF ###

    # @inlineCallbacks
    # def start_btm_process(self):
    
    #   ## call a procedure we are allowed to call (so this should succeed)
    #   ##
    #   #try:
    #   if self.session: 
    #       res = yield self.session.call(u'com.example.call_start_btm_process_task', "BUY")
    #       print("call result: {}".format(res))
    #       #except Exception as e:
    #       #   print("call error: {}".format(e))
    # stop = threading.Event()
    # stop_scan = threading.Event()
    # current_ticker = Decimal(0)
    
    def start_sendcoins_thread(self):
        threading.Thread(target=self.sendcoins_thread).start()
    def sendcoins_thread(self):
        # Worker thread to call the backend when transaction complete to actually send the coins
        #unneeded now
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
                print line.startswith("decoded QR-Code symbol")
                if line != "" and line != None and line.startswith("decoded QR-Code symbol"):
                #if line != "" and line != None and line.startswith("QR-Code:"):
                    print "runnning update label thread"
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
    ###@mainthread
    def qr_thread_update_label_text(self, new_text):
        label = self.root_manager.get_screen('buy').ids["'to_address'"]
        text = str(new_text)
        print "the text"
        print text
        text = text.replace('\"','').strip()
        print text
        address = text.split(":")
        if address[0] == "bitcoin":
            label.text = address[1].rstrip()
            print address[1]
            self.root_manager.current = 'buy'
            self.start_cashin_thread()

            #send call to backend with currency and customer crypto address
            print "CHECK THIS YO"
            print self.current_btm_process_id
            self.call_create_initial_buy_order_task(self.current_btm_process_id, address[1].rstrip(), address[0])
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
        total_quote_label = self.root.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1])
        if newtotal > 0:
            #and the addy
            address_label = self.root.get_screen('buy').ids["'to_address'"]

            headers = {'Authorization': 'ApiKey firstmachine:GUWH8Fh4q2byrwashcrnwas0vnsufwby8VBEAUSV', 'Accept': 'application/json', 'Content-Type': 'application/json'}
            payload = {'amount': str(newtotal), 'currency': 'CHF', 'reference':'', 'status':'RCVE', 'order':{'comment':""}, 'withdraw_address':{'address':address_label.text}}
            
            r = requests.post("https://secure.atm4coin.com/api/v1/input_transaction/", headers=headers, data=json.dumps(payload))
            print r.text

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
        total_quote_label = self.root.get_screen('buy').ids["'total_quote'"]
        gettotal = total_quote_label.text.split(" ")
        newtotal = int(gettotal[0].split("[b]")[1]) + int(cr[1])
        newtotalquote = Decimal(newtotal) / Decimal(self.current_ticker)
        newtotalquote_rounded = newtotalquote.quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
        total_quote_label.text = '[font=MyriadPro-Bold.otf][b]'+str(newtotal)+' Fr. = '+str(newtotalquote_rounded)+' BTC[/b][/font]'

        amount_sending_finished_label = self.root.get_screen('buyfinish').ids["'amount_sending_finished'"]
        amount_sending_finished_label.text = 'WE ARE SENDING YOUR '+str(newtotalquote_rounded)+' BITCOINS'

        if cr[1] == "10":
            #self.channel1_count += 1
            label = self.root.get_screen('buy').ids["'cashin10'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)

            #totallabel = self.get_screen('buy').ids["'total_quote'"]
            #totallabel.text = '[font=MyriadPro-Bold.otf][b]0 Fr. = 0 BTC[/b][/font]'
        if cr[1] == "20":
            #self.channel2_count += 1
            label = self.root.get_screen('buy').ids["'cashin20'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "50":
            #self.channel3_count += 1
            label = self.root.get_screen('buy').ids["'cashin50'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "100":
            #self.channel4_count += 1
            label = self.root.get_screen('buy').ids["'cashin100'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
        if cr[1] == "200":
            #self.channel5_count += 1
            label = self.root.get_screen('buy').ids["'cashin200'"]
            qty = label.text[1:]
            qty_new = int(qty) + 1
            label.text = 'x'+str(qty_new)
             

    def update_ticker(self, msg, hacky_fix=None):
        """
        Called from WAMP app component when message was received in a PubSub event.
        """
        label = self.root.get_screen('welcome').ids["'ticker_label'"]
        label.text = '[b]FOR '+msg+' Fr.[/b]'
        btc_buy_label = self.root.get_screen('welcome').ids["'btc_buy'"]
        btc_buy_label.text = msg
        btc_buyfinish_label = self.root.get_screen('buy').ids["'buyfinishbtcprice'"]
        btc_buyfinish_label.text = '[font=MyriadPro-Bold.otf][b]1 BTC = '+msg+' BTC[/b][/font]'
        self.current_ticker = Decimal(msg)
    def update_sell_ticker(self, msg, hacky_fix=None):
        """
        Called from WAMP app component when message was received in a PubSub event.
        """
        btc_sell_label = self.root.get_screen('welcome').ids["'btc_sell'"]
        btc_sell_label.text = msg

        return

    ###@mainthread
    def generate_thread_update_label_text(self, new_text):
        label = self.get_screen('generate').ids["'generate_status'"]
        text = str(new_text)
        print "the text"
        print text
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
        print imgn
        print dir(imgn)
        #data = io.BytesIO(open("image.png", "rb").read())
        print "before coreimage"
        #imgo = CoreImage(imgn)
        print "after coreimage"
        #print imgo
        print dir(img)
        #img.canvas.clear()
        img_tmp_file = open(os.path.join('tmp', 'qr.png'), 'wb')
        imgn.save(img_tmp_file, 'PNG')
        img_tmp_file.close()
        self.get_screen('generate').ids["'generate_qr'"].source = os.path.join('tmp', 'qr.png')
        
    
    def stop_scanning(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        print "set self.stop.set"
        self.stop.set()
    
    

class AtmClientApp(App):
    # def stop_scan(self):
    #     # The Kivy event loop is about to stop, set a stop signal;
    #     # otherwise the app window will close, but the Python process will
    #     # keep running until all secondary threads exit.
    #     self.root.stop_scan.set()
    def build(self):
        # WAMP session

        self.root = RootWidget()
      
        #Clock.schedule_once(self.start_wamp_component, 1)
        self.start_wamp_component()


        return self.root 
        #return RootWidget()

    def start_wamp_component(self, t=None):
        """
        Create a WAMP session and start the WAMP component
        """
        self.session = None
        
        # adapt to fit the Crossbar.io instance you're using
        url, realm = u"ws://localhost:8080/ws", u"realm1"

        # Create our WAMP application component
        runner = ApplicationRunner(url=url,
                                   realm=realm,
                                   extra=dict(ui=self.root))

        # Start our WAMP application component without starting the reactor because
        # that was already started by kivy
        runner.run(WampComponent, start_reactor=False)


if __name__ == '__main__':
    AtmClientApp().run()


    # def send_message(self, *args):
    #     """
    #     Called from UI when user has entered text and pressed RETURN.
    #     """
    #     msg = self.textbox.text
    #     if msg and self.session:
    #         self.session.publish(u"com.example.kivy", str(self.textbox.text))
    #         self.textbox.text = ""

    # def print_message(self, msg, test=None):
    #     print msg + "\n"
    #     #print test
    

    # def build_config(self, config):
    #     config.setdefaults('example', {
    #         'boolexample': True,
    #         'numericexample': 10,
    #         'optionsexample': 'option2',
    #         'stringexample': 'some_string',
    #         'pathexample': '/some/path'})

    # #def build_settings(self, settings):
    # #    settings.add_json_panel('Panel Name',
    # #                            self.config,
    # #                            data=settings_json)

    # def on_config_change(self, config, section,
    #                      key, value):
    #     print config, section, key, value
