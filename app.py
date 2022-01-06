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

import json
from threading import Lock
from typing import List, Dict

import strictyaml
from kivy.app import App
from kivy.config import Config as KivyConfig
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import RiseInTransition, ScreenManager
from path import Path
from pydantic import ValidationError

from src.components.label_sb import LabelSB
from src.screens.main import ScreenWelcome, ScreenMain
from src.types.pricefeed import PricefeedMessage, PriceFeedSubscriber
from src_backends.config_tools import Config
from src_backends.config_tools import parse_args as parse_args
from src_backends.custom_threads.zmq_subscriber import ZMQSubscriber
from template.overlay import OverlayNotSync


def set_kivy_log_level(debug: bool):
    if debug:
        KivyConfig.set('kivy', 'log_level', 'debug')
    else:
        KivyConfig.set('kivy', 'log_level', 'warning')
    KivyConfig.write()


def set_window(fullscreen: bool):
    Window.size = (1280, 720)
    if fullscreen:
        Window.fullscreen = True
        Window.show_cursor = False


class Manager(ScreenManager):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self._welcome_screen = ScreenWelcome(name='welcome')
        self._main_screen = ScreenMain(config, name='main')
        self.add_widget(self._welcome_screen)
        self.add_widget(self._main_screen)

    def set_content_screen(self, screen_id):
        self._main_screen.set_current_screen(screen_id)


def _retrieve_lang(path: str) -> Dict[str, Dict[str, str]]:
    """
    Load and parses language file...
    :param path: path of the language file
    :return: language dict
    """
    languages_yaml = strictyaml.load(Path(path).bytes().decode('utf8')).data
    return {k: dict(v) for k, v in languages_yaml.items()}


class TemplateApp(App):
    """True if the node communicates a synchronized status"""
    _node_in_sync = False

    """Selected language as an kivy's Observable"""
    _selected_language = StringProperty('EN')
    _stablecoin_reserve = NumericProperty(-1e18)
    _eth_reserve = NumericProperty(-1e18)
    kv_directory = 'template'

    def __init__(self, config: Config):
        super().__init__()

        LabelBase.register(name='SpaceGrotesk', fn_regular='assets/fonts/SpaceGrotesk-Regular.ttf')

        self._labels: List[LabelSB] = []
        self._config = config

        # Thread for node(s) status updates
        self._thread_status = ZMQSubscriber(
            self._update_message_status,
            config.zmq.status,
            ZMQSubscriber.TOPIC_STATUS
        )

        # Thread for currency prices updates
        self._thread_pricefeed = ZMQSubscriber(
            self._update_prices,
            config.zmq.pricefeed,
            ZMQSubscriber.TOPIC_PRICEFEED
        )

        # Subscribers of pricefeed price updates
        self._subscribers_prices: List[PriceFeedSubscriber] = []

        # Physical fiat currency supported by the banknote validator
        self._machine_currency = config.note_machine.currency

        self._manager = None
        self._languages = _retrieve_lang('lang_template.yaml')
        self._popup_sync = OverlayNotSync()
        self._overlay_lock = Lock()

        self._popup_count = 0

    def build(self):
        # Get a language
        self._selected_language = next(iter(self._languages))

        # Must be called after setting _selected_language
        self._manager = Manager(self._config, transition=RiseInTransition())

        # Start threads
        self._thread_status.start()
        self._thread_pricefeed.start()

        return self._manager

    def change_language(self, selected_language):
        """
        Change the current language.

        :param selected_language: Which language to select
        """
        self._selected_language = selected_language

        for label in self._labels:
            label.update_text()

    def add_label_cool(self, label: LabelSB):
        self._labels.append(label)

    def get_config(self) -> Config:
        """Get app config"""
        return self._config

    def get_string(self, str_id: str):
        """
        Get a specific string by ID, using the current language.

        :param str_id: id of the requested string
        """
        return self._languages[self._selected_language][str_id]

    def format_fiat_price(self, value: int, decimals: int = 0) -> str:
        """
        Return a formatted price with given value and swapbox currency.
        :param value: The price as a human-readable value
        :param decimals: The amount of decimals you want to show
        :return: The formatted price
        """
        # TODO: handle prefixed AND suffixed price format ($ 10 and 10 EUR).
        currency = self._machine_currency

        if currency == "EUR":
            currency = "€"

        return f"{currency} {value:.{decimals}f}"

    @staticmethod
    def format_crypto_price(value: int, token_name: str, decimals: int = 0) -> str:
        """
        Return a formatted price with given value and a curre
        :param value: The price as a human-readable value
        :param token_name: The token name
        :param decimals: The amount of decimals you want to show
        :return: The formatted price
        """
        return f"{value:.{decimals}f} {token_name}"

    @staticmethod
    def format_small_address(address: str) -> str:
        return f"{address[0:9]}...{address[-8:-1]}"

    def subscribe_prices(self, callback: PriceFeedSubscriber):
        """
        Subscribe to prices update

        :param callback: called each time a price update happens.
        """
        self._subscribers_prices.append(callback)

    def unsubscribe_prices(self, callback: PriceFeedSubscriber):
        """
        Unsubscribe from prices update

        :param callback: the one callback who should stop being called.
        """
        try:
            self._subscribers_prices.remove(callback)
        except ValueError as e:
            print("already unsubscribed price", e)

    def _update_prices(self, message: str):
        """
        Parses message back from pricefeed raw message and update internal self._prices.

        You can subscribe to it via the subscribe_prices method.

        :argument message raw message from pricefeed
        """
        try:
            self._prices = PricefeedMessage(**json.loads(message)).prices
        except ValidationError as e:
            print(e.json())

        for callback in self._subscribers_prices:
            callback(self._prices)

    def _update_message_status(self, message):
        """
        Called when there's a message from the node
        :param message: node's data
        """
        msg_json = json.loads(message)
        self._node_in_sync = msg_json["blockchain"]["is_in_sync"]
        self.toggle_sync_popup()

    def is_node_in_sync(self) -> bool:
        """
        Return true if the node is connected and in sync.
        :return: A boolean representing the state of the node.
        """
        return self._node_in_sync

    def toggle_sync_popup(self):
        """
        Show -not sync- popup if not synced.
        :return:
        """
        # show
        if self._node_in_sync:
            self._popup_sync.dismiss()
        else:
            # self._popup_sync = OverlayNotSync()
            self._popup_sync.open()

    def on_stop(self):
        self._config.NODE_RPC.stop()

    # this method is ugly but we play with the raspicam overlay and have no choice
    def before_popup(self):
        """ used to cleanup the overlay in case a popup is opened while in scanning mode
        this method must be called before a popup is opened"""
        driver = self._config.QR_SCANNER
        # this will raise an error when the driver has no _overlay_auto_on attribute
        # aka we're not on raspberry pi + raspicam
        try:
            _ = driver._overlay_auto_on
        except:
            return
        with self._overlay_lock:
            self._popup_count += 1
            if driver._overlay_auto_on and self._popup_count == 1:
                driver._hide_overlay()

    # this method is ugly but we play with the raspicam overlay and have no choice
    def after_popup(self):
        """ used to show the overlay in case a popup is closed while in scanning mode
        this method must be called after a popup is closed"""
        driver = self._config.QR_SCANNER
        # this will raise an error when the driver has no _overlay_auto_on attribute
        # aka we're not on raspberry pi + raspicam
        try:
            _ = driver._overlay_auto_on
        except:
            return

        with self._overlay_lock:
            self._popup_count -= 1
            if driver._overlay_auto_on and self._popup_count == 0:
                driver._show_overlay()


def main():
    args = parse_args()
    config = Config(args.config)

    set_kivy_log_level(config.debug)
    set_window(config.is_fullscreen)

    app = TemplateApp(config)
    app.run()


if __name__ == '__main__':
    main()
