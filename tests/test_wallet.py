import re

import pytest

from pycoin.wallet import WalletManager
from pycoin.wallet.wallet import Wallet, InvalidPasswordError, \
    InvalidOperationError


@pytest.fixture
def locked_wallet():
    return Wallet(
        pub_key='44d276aee002bd9fe4cb9bffb6c105'
                '4d572d9c0d63e69b006ce062cc5f3eb544',
        priv_key='952a2678521354fcb58fd42a0a8d19f6b18f80d1e670a6d0254c523'
                 'eba7f83fe6913b42d1b78b791b525626744c57b0a37e16b1cbec805d'
                 'fffc5843c22ef58c071be2bc40e55f6743af9dd07c9372ad7a819cac'
                 '0c62006f5c6cb7c955e0f563318525aff2918c8f4',
        locked=True
    )


@pytest.fixture
def unlocked_wallet():
    wallet = WalletManager.create_wallet('password')
    wallet.unlock('password')
    return wallet


def test_wallet_manager_create_wallet():
    wallet = WalletManager.create_wallet('password')
    assert wallet.verify_key is not None
    assert wallet.sign_key is not None
    assert isinstance(wallet.verify_key, str)
    assert isinstance(wallet.sign_key, str)
    assert re.match(r'^[0-9a-f]{64}$', wallet.verify_key)
    assert re.match(r'^[0-9a-f]{208}$', wallet.sign_key)


def test_wallet_sign(locked_wallet):
    data = b'hello there'
    wallet = locked_wallet
    wallet.unlock('password')
    signed = wallet.sign(data)
    wallet.verify(signed)


def test_wallet_locked(locked_wallet):
    wallet = locked_wallet
    assert wallet.locked
    with pytest.raises(InvalidOperationError):
        # cannot lock twice
        wallet.lock('password')
    with pytest.raises(InvalidOperationError):
        # cannot sign wit locked wallet
        wallet.sign(b'data')
    # can verify signed data
    wallet.verify('cb63d85865128ed5601e2a4cb28092fcc64600f61a05730eff12'
                  '22b168ed42060d4fc8bcb4c8313eaafc70f682600d2fd55cda89f'
                  'a7b6593ef91a1d9b479370168656c6c6f207468657265')
    with pytest.raises(InvalidPasswordError):
        # unlock wrong password
        wallet.unlock('bad_password')


def test_wallet_unlocked(unlocked_wallet):
    wallet = unlocked_wallet
    assert not wallet.locked
    with pytest.raises(InvalidOperationError):
        # cannot unlock twice
        wallet.unlock('password')
    with pytest.raises(InvalidOperationError):
        # to not leak the private key
        wallet.to_dict()


def test_wallet_mnemonic_seed_restore():
    old_wallet = WalletManager.create_wallet('password')
    seed = old_wallet.mnemonic_seed
    assert seed is not None
    # Woops we lost the wallet. Now we have to restore it, together with
    # the password
    restored = WalletManager.create_from_mnemonic_and_password(seed, 'password')
    assert restored.locked is True
    # We unlock the wallet so that we need to compare the private keys
    old_wallet.unlock('password')
    restored.unlock('password')
    assert restored.mnemonic_seed == seed
    assert restored.sign_key == old_wallet.sign_key
    assert restored.verify_key == old_wallet.verify_key


def test_wallet_mnemonic_seed_restore_different_password():
    old_wallet = WalletManager.create_wallet('first_password')
    seed = old_wallet.mnemonic_seed
    assert seed is not None
    restored = WalletManager.create_from_mnemonic_and_password(
        seed, 'second_password')
    old_wallet.unlock('first_password')
    restored.unlock('second_password')
    assert restored.sign_key == old_wallet.sign_key
    assert restored.verify_key == old_wallet.verify_key
