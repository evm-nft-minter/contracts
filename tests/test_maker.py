import time, pytest
from math import floor
from brownie import accounts, Maker, Collection, exceptions, Wei
from eth_account import Account
from web3 import Web3
from scripts.helpers import create_voucher


def test_can_make_collection():
    owner = accounts[0]
    owner_initial_balance = owner.balance()
    collection_owner = accounts[1]
    voucher_signer = Account.create()
    fee = Web3.toWei(1, "ether")
    timestamp = floor(time.time())
    collection_name = "test"
    collection_symbol = "TEST"
    token_id = 1
    token_uri = "https://test"

    maker = Maker.deploy(voucher_signer.address, {"from": owner})

    voucher = create_voucher(voucher_signer, maker.address, fee, timestamp)

    maker.make(
        [fee, timestamp, voucher],
        collection_name,
        collection_symbol,
        token_id,
        token_uri,
        {"from": collection_owner, "value": fee},
    )

    assert maker.collectionCount(collection_owner) == 1
    assert owner.balance() == (owner_initial_balance + fee)

    collection = Collection.at(maker.collection(collection_owner, 0))

    assert collection.name() == collection_name
    assert collection.symbol() == collection_symbol
    assert collection.owner() == collection_owner
    assert collection.balanceOf(collection_owner) == 1
    assert collection.tokenURI(token_id) == token_uri


def test_fail_if_voucher_signer_is_wrong():
    owner = accounts[0]
    collection_owner = accounts[1]
    voucher_signer = Account.create()
    wrong_voucher_signer = Account.create()
    fee = Web3.toWei(1, "ether")
    six_minutes = 6 * 60
    timestamp = floor(time.time() - six_minutes)
    collection_name = "test"
    collection_symbol = "TEST"
    token_id = 1
    token_uri = "https://test"

    maker = Maker.deploy(voucher_signer.address, {"from": owner})

    voucher = create_voucher(
        wrong_voucher_signer, maker.address, fee, timestamp,
    )

    with pytest.raises(
        exceptions.VirtualMachineError, match="Signature invalid or unauthorized"
    ):
        maker.make(
            [fee, timestamp, voucher],
            collection_name,
            collection_symbol,
            token_id,
            token_uri,
            {"from": collection_owner, "value": fee},
        )


def test_fail_if_amount_is_wrong():
    owner = accounts[0]
    collection_owner = accounts[1]
    voucher_signer = Account.create()
    fee = Web3.toWei(1, "ether")
    wrong_making_cost = Web3.toWei(0.5, "ether")
    timestamp = floor(time.time())
    collection_name = "test"
    collection_symbol = "TEST"
    token_id = 1
    token_uri = "https://test"

    maker = Maker.deploy(voucher_signer.address, {"from": owner})

    voucher = create_voucher(voucher_signer, maker.address, fee, timestamp)

    with pytest.raises(
        exceptions.VirtualMachineError, match="Amount sent is not correct"
    ):
        maker.make(
            [fee, timestamp, voucher],
            collection_name,
            collection_symbol,
            token_id,
            token_uri,
            {"from": collection_owner, "value": wrong_making_cost},
        )


def test_fail_if_voucher_is_expired():
    owner = accounts[0]
    collection_owner = accounts[1]
    voucher_signer = Account.create()
    fee = Web3.toWei(1, "ether")
    timestamp = floor(time.time() - 6 * 60)
    collection_name = "test"
    collection_symbol = "TEST"
    token_id = 1
    token_uri = "https://test"

    maker = Maker.deploy(voucher_signer.address, {"from": owner})

    voucher = create_voucher(voucher_signer, maker.address, fee, timestamp)

    with pytest.raises(exceptions.VirtualMachineError, match="Voucher is expired"):
        maker.make(
            [fee, timestamp, voucher],
            collection_name,
            collection_symbol,
            token_id,
            token_uri,
            {"from": collection_owner, "value": fee},
        )
