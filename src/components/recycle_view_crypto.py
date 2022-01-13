from typing import Dict, List

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
        return super(TokenListItem, self).refresh_view_attrs(rv, index, data)

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
        self._backends: List[Backend] = []
        self._last_prices: Dict[str, float] = {}

    def populate(self, backends: List[Backend]):
        self._backends = backends
        self.data = []

        for backend in backends:
            for token in backend.tokens:
                self.data.append({
                    'symbol.text': token.symbol,
                    'name.text': token.name,
                    'price.text': "loading...",
                    'value': TokensRecycleView.ICONS_FOLDER.format(token.symbol.lower())
                })

    def update_prices(self, prices: Dict[str, float]):
        """
        Update token prices inside list view.

        :param prices: key is the token name, value is the price. It will try to match token name
        with existing rows, if it exists in the list, then the price is updated.
        """
        self._last_prices = prices
        for i, data in enumerate(self.data):
            token: str = data['symbol.text']
            if token in prices:
                self.data[i]["price.text"] = "{:4f} CHF".format(prices[token])
        self.refresh_from_data()

    def set_selected(self, index):
        self.selected = index

    def get_selected_token(self) -> tuple[str, float]:
        """Return currently selected token in list view."""
        selected_item = self.data[self.selected]
        token_name = selected_item['symbol.text']
        return token_name, self._last_prices[token_name]

    def deselect(self):
        self.layout_manager.deselect_node(self.selected)
