import re

import sha3

address_without_checksum = (re.compile('^[0-9a-f]{40}$'), re.compile('^[0-9A-F]{40}$'))
address_with_checksum = re.compile('^[0-9a-fA-F]{40}$')
hex_letters = 'abcdef'


def parse_ethereum_address(raw_address, quiet=False):
    if not raw_address:
        return _quietly_raise(ValueError('invalid address'), quiet)

    protocol, address = raw_address.split(':', 1) if ':' in raw_address else ('ethereum', raw_address)
    if not address:
        return _quietly_raise(ValueError('invalid address'), quiet)
    elif protocol.lower() != 'ethereum':
        return _quietly_raise(ValueError("invalid protocol: '{}'".format(protocol)), quiet)

    if not (address.startswith('0x') or address.startswith('0X')):
        return _quietly_raise(ValueError("missing 0x prefix"), quiet)

    address = address[2:]
    address_len = len(address)
    if address_len < 40:
        return _quietly_raise(ValueError('address is too short'), quiet)
    elif address_len > 40:
        return _quietly_raise(ValueError('address is too long'), quiet)

    if any(bool(pattern.match(address)) for pattern in address_without_checksum):
        return to_checksum(address)

    if not address_with_checksum.match(address):
        return _quietly_raise(ValueError('invalid address'), quiet)

    plain_address = address.lower().encode('ascii')
    address_hash = sha3.keccak_256(plain_address).hexdigest()
    for char, hash_value in zip(address, address_hash):
        if char in hex_letters:
            hash_number = int(hash_value, 16)
            if (hash_number > 7 and not char.isupper()) or (hash_number <= 7 and not char.islower()):
                return _quietly_raise(ValueError('invalid checksum'), quiet)

    return '0x{}'.format(address)


def to_checksum(address):
    address = address.lower()
    address_hash = sha3.keccak_256(address.encode('ascii')).hexdigest()
    formatted_address = []

    for char, hash_value in zip(address, address_hash):
        if char not in hex_letters:
            formatted_address.append(char)
        elif int(hash_value, 16) > 7:
            formatted_address.append(char.upper())
        else:
            formatted_address.append(char)

    return '0x{}'.format(''.join(formatted_address))


def _quietly_raise(error, quiet):
    if quiet:
        return None
    raise error
