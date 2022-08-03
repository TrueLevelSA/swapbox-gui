from typing import Dict, List

from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior

from src.config import Token


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


class TokenPrice:
    def __init__(self, token: Token, price: float):
        self.token = token
        self.price = price


class TokensRecycleView(RecycleView):
    ICONS_FOLDER = "assets/img/currency_icons/{}.png"

    def __init__(self, **kwargs):
        super(TokensRecycleView, self).__init__(**kwargs)
        self.selected = -1
        # list of token,price tuples
        self.tps: List[TokenPrice] = []

    def populate(self, tokens: List[Token]):
        self.data = []

        for i in range(len(tokens)):
            token = tokens[i]
            self.tps.insert(i, TokenPrice(token, 0.0))
            self.data.insert(i, {
                'symbol.text': token.symbol,
                'name.text': token.name,
                'price.text_id': "loading",
                'value': TokensRecycleView.ICONS_FOLDER.format(token.symbol.lower())
            })

    def update_prices(self, prices: Dict[str, float]):
        """
        Update token prices inside list view.

        :param prices: key is the token name, value is the price. It will try to match token name
        with existing rows, if it exists in the list, then the price is updated.
        """
        # update data model prices
        for i, (tp, data) in enumerate(zip(self.tps, self.data)):
            data["price.translate"] = False

            if tp.token.symbol in prices.keys():
                tp.price = prices[tp.token.symbol]
                data["price.text"] = "{:4f} CHF".format(tp.price)

        self.refresh_from_data()

    def set_selected(self, index):
        self.selected = index

    def get_selected_token(self) -> TokenPrice:
        """Return currently selected token in list view."""
        return self.tps[self.selected]

    def deselect(self):
        self.layout_manager.deselect_node(self.selected)
