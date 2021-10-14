# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager

from src.screens.buy import ScreenBuyScan, ScreenBuyInsert, ScreenBuyFinal
from src.screens.sell import ScreenSell1, ScreenSell2, ScreenSell3
from src.screens.setup import ScreenSetup1, ScreenSetup2, ScreenSetup3


class Manager(ScreenManager):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._welcome_screen = ScreenWelcome(name='welcome')
        self._main_screen = ScreenMain(config, name='main')
        self.add_widget(self._welcome_screen)
        self.add_widget(self._main_screen)

    def set_content_screen(self, screen_id):
        self._main_screen.set_current_screen(screen_id)


class ScreenWelcome(Screen):
    def on_leave(self):
        # if we are not connected by the time we leave the welcome screen
        # then we show a popup
        app = App.get_running_app()
        if not app._first_status_message_received:
            App.get_running_app()._create_popup()


class ScreenMain(Screen):

    def __init__(self, config, **kwargs):
        self.config = config
        super().__init__(**kwargs)
        sm = self.ids.sm_content
        sm.add_widget(ScreenMenu(name='menu'))
        sm.add_widget(ScreenSettings(name='settings'))
        sm.add_widget(ScreenRedeem(name='redeem'))
        sm.add_widget(ScreenBuyScan(config, name='scan_screen'))
        sm.add_widget(ScreenBuyInsert(config, name='insert_screen'))
        sm.add_widget(ScreenBuyFinal(name='final_buy_screen'))
        sm.add_widget(ScreenSell1(config, name='sell1'))
        sm.add_widget(ScreenSell2(config, name='sell2'))
        sm.add_widget(ScreenSell3(name='sell3'))
        sm.add_widget(ScreenConfirmation(name='confirmation'))
        sm.add_widget(ScreenLoading(name='loading_screen'))
        sm.add_widget(ScreenSetup1(name='setup_1'))
        sm.add_widget(ScreenSetup2(name='setup_2'))
        sm.add_widget(ScreenSetup3(name='setup_3'))

        self._sm = sm

    def set_current_screen(self, screen_id):
        self._sm.transition.direction = "down"
        self._sm.current = screen_id


class LayoutPopup(BoxLayout):
    pass


class ScreenMenu(Screen):
    pass


class FullScreenPopup(ModalView):
    pass


class SyncPopup(FullScreenPopup):
    pass


class ScreenSettings(Screen):
    pass


class ScreenRedeem(Screen):
    pass


class ScreenLoading(Screen):
    pass


class ScreenConfirmation(Screen):
    pass
