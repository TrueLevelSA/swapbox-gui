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
from pydantic import BaseModel


class Fees(BaseModel):
    network: int
    operator: int
    liquidity_provider: int

    @property
    def total(self):
        return self.network + self.operator + self.liquidity_provider

    def percent_network(self, total: int):
        return self._percent(self.network, total)

    def percent_operator(self, total: int):
        return self._percent(self.operator, total)

    def percent_lp(self, total: int):
        return self._percent(self.liquidity_provider, total)

    def percent_total(self, total: int):
        return self._percent(self.total, total)

    @staticmethod
    def _percent(fee: int, total: int):
        return fee / total * 100.0


class Transaction(BaseModel):
    """
    Attributes:
        decimals        The decimals of bought token
        amount_bought   Confirmed bought amount after tx success
        fees            total amount of paid fees
        tx_url          The transaction URL, the gui will generate a QR Code for
                        it. It can be empty if the network doesn't have a block
                        explorer.
    """
    decimals: int
    amount_bought: int
    url: str
    fees: Fees
