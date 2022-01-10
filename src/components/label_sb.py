from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.label import Label


class LabelSB(Label):
    """
    Label base for the whole swapbox project.

    Use this as a base for every label, it sets the style and make itself i18n-able.
    For dynamic translations to work, you must set the `text_id` property
    """
    text_id = StringProperty("")
    text_params = ListProperty()

    def __init__(self, **kwargs):
        super(LabelSB, self).__init__(**kwargs)

        # adds label ref to main app. it will call update_text when selected language is updated
        App.get_running_app().add_label_cool(self)

        self.bind(text_id=self.update_text)
        self.bind(text_params=self.update_text)

    def update_text(self, *args):
        if self.text_id != "":
            text: str = App.get_running_app().get_string(self.text_id)

            # attempts to format if there are some given text params
            if len(self.text_params) > 0:
                text = text.format(*self.text_params)

            self.text = text
