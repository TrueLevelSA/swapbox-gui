from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, FallOutTransition
from kivy.properties import ObjectProperty
import strictyaml
from path import Path

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


class TemplateApp(App):
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
        m = Manager(transition=RiseInTransition())
        return m

    def change_language(self):
        pass

if __name__ == "__main__":
    TemplateApp().run()
