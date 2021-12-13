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
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from src_backends.config_tools import Config

Builder.load_string('''
<ButtonLanguage>
    canvas.before:
        Color:
            rgba: color_gray_5 if self._selected else color_off_black
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: color_off_white if self._selected else color_gray_3
        Line:
            width: 1
            rectangle: self.x, self.y, self.width, self.height
            cap: 'square'
            joint: 'miter'
''')


class ButtonLanguage(ToggleButtonBehavior, Image):
    _language = StringProperty(None)
    _selected = BooleanProperty(False)

    # There's always a selected language.
    allow_no_selection = False

    def __init__(self, language: str, selected=False, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/img/flags/' + language.lower() + '.png'
        self._language = language
        if selected:
            self.state = 'down'

    def on_state(self, widget, value):
        self._selected = value == 'down'

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

        # adds widget until there's 7 widgets in order to fit the 12col grid
        if len(languages) < 7:
            for i in range(7 - len(languages)):
                self.add_widget(Widget())
