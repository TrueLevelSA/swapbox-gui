from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from src.screens.main import FullScreenPopup, LayoutPopup


class ButtonLanguage(Button):
    _language = StringProperty(None)

    def __init__(self, language, callback=None, **kwargs):
        self._language = language
        self._callback = callback
        # self.text = language
        self.background_down = 'assets/img/flags/medium/' + language + '.png'
        self.background_normal = self.background_down
        super().__init__(**kwargs)

    def on_press(self):
        App.get_running_app().change_language(self._language)
        if self._callback is not None:
            self._callback()


class LanguageBar(BoxLayout):
    spacing = 10

    def __init__(self, **kwargs):
        super(LanguageBar, self).__init__(**kwargs)
        self.add_widgets()

    def add_widgets(self, *args, **kwargs):
        # has to match the array in lang_template.yaml
        languages = ['EN', 'DE', 'FR', 'IT', 'PT', 'ES']
        for l in languages:
            self.add_widget(ButtonLanguage(l))
        # self.add_widget(wid)


class LanguagePopup(FullScreenPopup):
    def __init__(self):
        super().__init__()
        # has to match the array in lang_template.yaml
        languages = ['EN', 'DE', 'FR', 'PT']
        wid = LayoutPopup()
        for l in languages:
            wid.add_widget(ButtonLanguage(l, self._close))
        self.add_widget(wid)

    def _close(self):
        self.dismiss()
        App.get_running_app().after_popup()
