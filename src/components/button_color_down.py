from kivy.properties import ListProperty
from kivy.uix.button import Button


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