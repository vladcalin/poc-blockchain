import functools
import random

import pytest

from pycoin.wallet.mnemonic import mnemonic_generate_sequence


def test_mnemonic_generate(monkeypatch):
    monkeypatch.setattr('random.SystemRandom',
                        functools.partial(random.Random, x=3))
    items = mnemonic_generate_sequence(10)
    assert items == ['keep', 'drift', 'runway', 'verify', 'canoe', 'allow',
                     'usual', 'luggage', 'jewel', 'giraffe']
    items = mnemonic_generate_sequence(5)
    assert items == ['keep', 'drift', 'runway', 'verify', 'canoe']
    with pytest.raises(ValueError):
        mnemonic_generate_sequence(-1)
