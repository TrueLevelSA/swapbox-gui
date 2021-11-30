from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label


class ButtonBase(Button):
    def __init__(self, **kwargs):
        super(ButtonBase, self).__init__(**kwargs)
        self.background_normal = ''
        self.font_size = 25
        self.halign = "center"
        self.markup = True
        self.text = self.text.upper()

    # def on_press(self):
    #     super(ButtonBaseA, self).on_press()
    #     self.text = self.text.upper()
