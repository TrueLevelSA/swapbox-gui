from kivy.uix.button import Button

from src.components.label_sb import LabelSB


class ButtonSB(Button, LabelSB):
    """
    Button base for the whole swapbox project.

    Use this as a base for every button, it sets the style and make itself i18n-able.
    For dynamic translations to work, you must set the `text_id` property
    """


class ButtonBase(ButtonSB):
    pass


class ButtonLight(ButtonBase):
    pass


class ButtonDark(ButtonBase):
    pass
