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
from kivy.graphics import Color, Line
from kivy.properties import StringProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from src_backends.config_tools import Config


class ButtonLanguage(ToggleButtonBehavior, Image):
    _language = StringProperty(None)

    # There's always a selected language.
    allow_no_selection = False

    def __init__(self, language: str, selected=False, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/img/flags/medium/' + language + '.png'
        self._language = language

        if selected:
            # TODO: set first selected
            pass

    def on_state(self, widget, value):
        self._draw_border(value == 'down')

    def _draw_border(self, selected: bool):
        if selected:
            with self.canvas.before:
                Color(1.0, 1.0, 1.0, 1.0)
                Line(width=2, rectangle=(self.x, self.y, self.width, self.height))
        else:
            self.canvas.before.clear()

    def on_press(self):
        App.get_running_app().change_language(self._language)


class LanguageBar(BoxLayout):

    def __init__(self, **kwargs):
        super(LanguageBar, self).__init__(**kwargs)
        self.create_languages_buttons()

    def create_languages_buttons(self):
        config: Config = App.get_running_app().get_config()

        # has to match the array in lang_template.yaml
        languages = ['EN', 'DE', 'FR', 'IT', 'PT', 'ES']
        for lang in languages:
            selected = lang == config.default_lang
            self.add_widget(ButtonLanguage(lang, selected, group='lang'))
