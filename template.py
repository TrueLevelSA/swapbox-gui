from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty
import yaml

Window.size = (1380, 770)

class WelcomeScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class BuyScreen1(Screen):
    pass
        
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
    buy_screen1 = ObjectProperty(None)
    redeem_screen = ObjectProperty(None)
    buy_screen1 = ObjectProperty(None)
    buy_screen2 = ObjectProperty(None)
    buy_screen3 = ObjectProperty(None)
    sell_screen1 = ObjectProperty(None)
    sell_screen2 = ObjectProperty(None)
    sell_screen3 = ObjectProperty(None)
    confirmation_screen = ObjectProperty(None)


class templateApp(App):
    def build(self):
        self.lang = yaml.load(open("lang.yaml", "r"))
        self.LANGUAGES = [language for language in self.lang]
        self.l = self.LANGUAGES[0]
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
        m = Manager(transition=RiseInTransition())
        return m

    def change_language(self):
        pass

if __name__ == "__main__":
    templateApp().run()
