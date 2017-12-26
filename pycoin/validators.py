import re

ADDRESS_REGEX = re.compile(r'[\w\d_-]{35}\.py')


def is_valid_address(address):
    return ADDRESS_REGEX.match(address) is not None
