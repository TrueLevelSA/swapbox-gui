from typing import Mapping, Tuple

from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior

from src_backends.config_tools import Backend


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
            rv.set_selected(index)


class TokensRecycleView(RecycleView):
    ICONS_FOLDER = "assets/img/currency_icons/{}.png"

    def __init__(self, **kwargs):
        super(TokensRecycleView, self).__init__(**kwargs)
        self.selected = -1
        self._backends = [Backend]

    def populate(self, backends: [Backend]):
        self._backends = backends
        self.data = []

        for backend in backends:
            for token in backend.tokens:
                self.data.append({
                    'name.text': token.name,
                    'price.text': "CHF " + str(0.01),
                    'network.text': backend.type,
                    'value': TokensRecycleView.ICONS_FOLDER.format(token.name.lower())
                })

    def update_prices(self, prices):
        for i, data in enumerate(self.data):
            token: str = data['name.text']
            if token in prices:
                self.data[i]["price.text"] = "{:4f} CHF".format(prices[token]['price'])
        self.refresh_from_data()

    def set_selected(self, index):
        self.selected = index

    def get_selected_token(self) -> Tuple[str, str]:
        selected_item = self.data[self.selected]
        token_name = selected_item['name.text']
        token_backend = selected_item['network.text']
        return token_name, token_backend
