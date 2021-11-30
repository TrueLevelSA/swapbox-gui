from enum import Enum
from typing import Optional

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty

from src.components.boxlayout_bg import BoxLayoutBackground

Builder.load_string('''
<LabelStepTitle@Label>
    halign: "left"
    valign: "center"
    text_size: self.size
    font_size: 20

<LabelStepText@LabelStepTitle>
    bold: True

<StepsWidget>
    orientation: "horizontal"
    padding: (40, 40)
    size_hint_x: 0.3
    background_color: color_darker_black

    BoxLayout:
        orientation: "vertical"

        LabelStepTitle:
            text: "Action:"
        LabelStepTitle:
            text: "Network:"
        LabelStepTitle:
            text: "Currency:"
        LabelStepTitle:
            text: "Wallet:"
        LabelStepTitle:
            text: "Cash amount:"

    BoxLayout:
        orientation: "vertical"

        LabelStepText:
            id: action_name
            text: root._action
        LabelStepText:
            id: network
            text: root._network
        LabelStepText:
            id: currency
            text: root._currency
        LabelStepText:
            id: wallet
            text: root._wallet
        LabelStepText:
            id: cash_amount
            text: app.format_fiat_price(root._amount)
''')


class Action(Enum):
    BUY = 0
    SELL = 1


class Wallet(Enum):
    PAPER = 0
    HOT = 1


class TransactionOrder:
    """A transaction order representing what the user want to do.

    It is gradually built screen after screen, until when it's ready and will be sent to the connector.

    Attributes:
        action          The type of order, buy or sell.
        token           The token the user want to buy.
        backend         The backend of the token.
        to              To whom the token will be forwarded while/after the tx.
        amount_fiat     The amount of fiat the user cashed in.
        amount_crypto   The amount of crypto the user has received.
        wallet_type     The type of the wallet.
    """

    def __init__(self):
        self.action: Optional[Action] = None
        self.token: Optional[str] = ""
        self.backend: str = ""
        self.to: Optional[str] = None
        self.amount_fiat: Optional[int] = None
        self.amount_crypto: Optional[int] = None
        self.wallet_type: Optional[Wallet] = None


class StepsWidget(BoxLayoutBackground):
    _action = StringProperty("")
    _network = StringProperty("")
    _currency = StringProperty("")
    _wallet = StringProperty("")
    _amount = NumericProperty(0)

    def __init__(self, **kwargs):
        super(StepsWidget, self).__init__(**kwargs)

    def set_tx_order(self, tx_order: TransactionOrder):
        if tx_order.action is not None:
            self._action = tx_order.action.name

        if tx_order.backend is not None:
            self._network = tx_order.backend

        if tx_order.token is not None:
            self._currency = tx_order.token

        if tx_order.wallet_type is not None:
            self._wallet = tx_order.wallet_type

        if tx_order.amount_fiat is not None:
            self._amount = tx_order.amount_fiat
