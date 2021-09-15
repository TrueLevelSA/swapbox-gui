# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def _get_input_price(input_amount: int, input_reserve: int, output_reserve: int) -> int:
    # input reserve, output reserve should be > 0 but the values are checked by my dude @noderpc
    input_amount = int(input_amount)
    input_reserve = int(input_reserve)
    output_reserve = int(output_reserve)
    input_amount_with_fee = input_amount * 997
    numerator = input_amount_with_fee * output_reserve
    denominator = (input_reserve * 1000) + input_amount_with_fee
    return numerator // denominator


def _get_output_price(output_amount: int, input_reserve: int, output_reserve: int) -> int:
    # input reserve, output reserve should be > 0 but the values are checked by my dude @noderpc
    output_amount = int(output_amount)
    input_reserve = int(input_reserve)
    output_reserve = int(output_reserve)
    numerator = input_reserve * output_amount * 1000
    denominator = (output_reserve - output_amount) * 997
    return numerator // denominator + 1


def get_buy_price(tokens_sold: int, token_reserve: int, eth_reserve: int) -> int:
    """ returns the amount of eth in weis that can be bought for tokens_sold"""
    return _get_input_price(tokens_sold, token_reserve, eth_reserve)


def get_sell_price(tokens_bought: int, eth_reserve: int, token_reserve: int) -> int:
    """ returns the amount of eth in weis needed to buy tokens_bought """
    return _get_output_price(tokens_bought, eth_reserve, token_reserve)
