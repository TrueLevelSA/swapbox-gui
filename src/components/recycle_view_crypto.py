from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior, RecycleKVIDsDataViewBehavior

from src_backends.config_tools import Token


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behaviour to the view. """


class TokenListItem(RecycleKVIDsDataViewBehavior, BoxLayout):
    """ Add selection support to the Label """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(TokenListItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(TokenListItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class TokensRecycleView(RecycleView):
    ICONS_FOLDER = "assets/img/currency_icons/{}.png"

    def __init__(self, **kwargs):
        super(TokensRecycleView, self).__init__(**kwargs)

    def populate(self, backends):
        self.data = []

        for backend in backends:
            for token in backend.tokens:
                self.data.append({
                    'name.text': token.name,
                    'price.text': "CHF " + str(0.01),
                    'network.text': backend.type,
                    'value': TokensRecycleView.ICONS_FOLDER.format(token.name.lower())
                })

