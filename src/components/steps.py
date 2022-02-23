#  Swap-box
#  Copyright (c) 2022 TrueLevel SA
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum
from typing import Optional

from kivy.app import App
from kivy.lang import Builder

from src.components.boxlayout_bg import BoxLayoutBackground
from src.components.label_sb import LabelSB
from src_backends.config_tools import Token

Builder.load_string('''
<IconStep@Image>
    disabled: True
    color: color_off_white
    disabled_color: color_gray_3

<StepLabel@LabelLeft>
    disabled: True
    color: color_off_white
    disabled_color: color_gray_3

<StepsWidgetBuy>
    padding: (30, 30)
    background_color: color_darker_black
    BoxLayout:
        orientation: "vertical"
        spacing: 10

        LabelLeft:
            size_hint_y: 0.1
            text_id: 'your_selection'

        BoxLayout:
            orientation: "horizontal"

            BoxLayout:
                orientation: "vertical"
                size_hint_x: 0.4

                IconStep:
                    id: ico_action
                    source: "assets/img/action.png"
                IconStep:
                    id: ico_network
                    source: "assets/img/network.png"
                IconStep:
                    id: ico_currency
                    source: "assets/img/currency.png"
                IconStep:
                    id: ico_wallet
                    source: "assets/img/wallet.png"
                IconStep:
                    id: ico_amount
                    source: "assets/img/cash.png"

            BoxLayout:
                orientation: "vertical"

                StepLabel:
                    id: label_action
                StepLabel:
                    id: label_network
                    text_id: "step_network" if self.disabled else ""
                StepLabel:
                    id: label_currency
                    text_id: "step_currency" if self.disabled else ""
                StepLabel:
                    id: label_wallet
                    text_id: "step_wallet" if self.disabled else ""
                StepLabel:
                    id: label_amount
                    text_id: "step_amount" if self.disabled else ""

<StepsWidgetSell>
    padding: (30, 30)
    background_color: color_darker_black
    BoxLayout:
        orientation: "vertical"
        spacing: 10

        LabelLeft:
            size_hint_y: 0.1
            text_id: 'your_selection'

        BoxLayout:
            orientation: "horizontal"

            BoxLayout:
                orientation: "vertical"
                size_hint_x: 0.4

                IconStep:
                    id: ico_action
                    source: "assets/img/action.png"
                IconStep:
                    id: ico_amount
                    source: "assets/img/cash.png"
                IconStep:
                    id: ico_network
                    source: "assets/img/network.png"
                IconStep:
                    id: ico_currency
                    source: "assets/img/currency.png"
                IconStep:
                    id: ico_wallet
                    source: "assets/img/wallet.png"

            BoxLayout:
                orientation: "vertical"

                StepLabel:
                    id: label_action
                StepLabel:
                    id: label_amount
                    text_id: "step_amount" if self.disabled else ""
                StepLabel:
                    id: label_network
                    text_id: "step_network" if self.disabled else ""
                StepLabel:
                    id: label_currency
                    text_id: "step_currency" if self.disabled else ""
                StepLabel:
                    id: label_wallet
                    text_id: "step_wallet" if self.disabled else ""
''')


class Action(Enum):
    BUY = 0
    SELL = 1


class Wallet(Enum):
    PAPER = 0
    HOT = 1


class TransactionOrder:
    """A transaction order representing what the user want to do.

    It is gradually built screen after screen, until when it's ready and will be
    sent to the connector.

    Attributes:
        action:         The type of order, buy or sell.
        token:          The token the user want to buy.
        network:        The network the token is on.
        to:             To whom the token will be forwarded while/after the tx.
        amount_fiat:    The amount of fiat the user cashed in.
        amount_crypto:  The amount of crypto the user has received.
        wallet_type:    The type of the wallet.
    """

    def __init__(
            self,
            action=None,
            token=None,
            network=None,
            to=None,
            amount_fiat=None,
            amount_crypto=None,
            wallet_type=None,
    ):
        self.action: Optional[Action] = action
        self.token: Optional[Token] = token
        self.network: Optional[str] = network
        self.to: Optional[str] = to
        self.amount_fiat: Optional[int] = amount_fiat
        self.amount_crypto: Optional[int] = amount_crypto
        self.wallet_type: Optional[Wallet] = wallet_type


class StepsWidgetBase(BoxLayoutBackground):

    def __init__(self, **kwargs):
        super(StepsWidgetBase, self).__init__(**kwargs)
        self._app = App.get_running_app()

    def set_tx_order(self, tx_order: TransactionOrder):
        if tx_order.action is not None:
            self.ids.ico_action.disabled = False
            l: LabelSB = self.ids.label_action
            l.disabled = False

            if tx_order.action == Action.BUY:
                l.text_id = "step_action_deposit"
            elif tx_order.action == Action.SELL:
                l.text_id = "step_action_withdraw"

        if tx_order.network is not None:
            self.ids.ico_network.disabled = False
            l: LabelSB = self.ids.label_network
            l.disabled = False
            l.text = tx_order.network

        if tx_order.token is not None:
            self.ids.ico_currency.disabled = False
            l: LabelSB = self.ids.label_currency
            l.disabled = False
            l.text = tx_order.token.symbol

        if tx_order.wallet_type is not None:
            self.ids.ico_wallet.disabled = False
            l: LabelSB = self.ids.label_wallet
            l.disabled = False
            l.text = tx_order.wallet_type

        if tx_order.amount_fiat is not None and tx_order.amount_fiat > 0:
            self.ids.ico_amount.disabled = False
            l: LabelSB = self.ids.label_amount
            l.disabled = False
            l.text = self._app.format_fiat_price(tx_order.amount_fiat)


class StepsWidgetBuy(StepsWidgetBase):
    pass


class StepsWidgetSell(StepsWidgetBase):
    pass
