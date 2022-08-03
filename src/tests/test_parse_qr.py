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

import pytest

from src.qr.scanner.util import parse_ethereum_address

VALID_ADDRESSES = (
    '0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24',
    '0x1820a4b7618bde71dce8cdc73aab6c95905fad24',
    '0X1820A4B7618BDE71DCE8CDC73AAB6C95905FAD24',
    'ethereum:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24',
    'ethereum:0x1820a4b7618bde71dce8cdc73aab6c95905fad24',
    'ethereum:0X1820A4B7618BDE71DCE8CDC73AAB6C95905FAD24',
    'ETHEREUM:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24',
    'ETHEREUM:0x1820a4b7618bde71dce8cdc73aab6c95905fad24',
    'ETHEREUM:0X1820A4B7618BDE71DCE8CDC73AAB6C95905FAD24',
)

VALID_PARSED_ADDRESS = '0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24'

INVALID_ADDRESSES = (
    (None, 'invalid address'),
    ('', 'invalid address'),
    ('ethereum', 'missing 0x prefix'),
    ('0xethereum', 'address is too short'),
    ('0xcrapcrapcrapcrapcrapcrapcrapcrapcrapcrap', 'invalid address'),
    ('ethereum:', 'invalid address'),
    ('ethereum:0x', 'address is too short'),
    ('0x', 'address is too short'),
    (':0x', "invalid protocol: ''"),
    ('1820a4B7618BdE71Dce8cdc73aAB6C95905faD242', 'missing 0x prefix'),
    ('0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD2', 'address is too short'),
    ('0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD242', 'address is too long'),
    ('0x1820a4B7618BdE71Dce8cdc73aAB6C95905fad24', 'invalid checksum'),
    ('ethereum:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD2', 'address is too short'),
    ('ethereum:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD242', 'address is too long'),
    ('ethereum:0x1820a4B7618BdE71Dce8cdc73aAB6C95905fad24', 'invalid checksum'),
    ('ethereum::0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24', 'missing 0x prefix'),
    ('ETHEREUM:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD2', 'address is too short'),
    ('ETHEREUM:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD242', 'address is too long'),
    ('ETHEREUM:0x1820a4B7618BdE71Dce8cdc73aAB6C95905fad24', 'invalid checksum'),
    ('crap:0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24', "invalid protocol: 'crap'"),
)


@pytest.mark.parametrize('raw_address,expected_address',
                         tuple((raw_address, VALID_PARSED_ADDRESS) for raw_address in VALID_ADDRESSES))
def test_parse_valid_address(raw_address, expected_address):
    assert parse_ethereum_address(raw_address, quiet=False) == expected_address


@pytest.mark.parametrize('raw_address,expected_error', INVALID_ADDRESSES)
def test_parse_invalid_address(raw_address, expected_error):
    with pytest.raises(ValueError) as excinfo:
        parse_ethereum_address(raw_address, quiet=False)

    assert expected_error == str(excinfo.value)


@pytest.mark.parametrize('raw_address', tuple(invalid_address for (invalid_address, _) in INVALID_ADDRESSES))
def test_parse_invalid_address_quiet(raw_address):
    assert parse_ethereum_address(raw_address, quiet=True) is None
