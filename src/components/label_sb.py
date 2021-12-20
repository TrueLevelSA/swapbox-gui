from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.label import Label


class LabelSB(Label):
    """
    Label base for the whole swapbox project.

    Use this as a base for every label, it sets the style and make itself i18n-able.
    For dynamic translations to work, you must set the `text_id` property
    """
    text_id = StringProperty("")

    def __init__(self, **kwargs):
        super(LabelSB, self).__init__(**kwargs)

        # adds label ref to main app. it will call update_text when selected language is updated
        App.get_running_app().add_label_cool(self)

    def on_text_id(self, instance, value):
        self.update_text()

    def update_text(self):
        if self.text_id != "":
            self.text = App.get_running_app().get_string(self.text_id)
