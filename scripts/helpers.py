from brownie import chain
from eth_account import Account
from eip712.messages import EIP712Message

VOUCHER_DOMAIN_NAME = "Making Voucher"
VOUCHER_DOMAIN_VERSION = "1"

def create_voucher(signer: Account, verifying_contract, value, timestamp):
    class Voucher(EIP712Message):
        _name_: "string" = VOUCHER_DOMAIN_NAME
        _version_: "string" = VOUCHER_DOMAIN_VERSION
        _chainId_: "uint256" = chain.id
        _verifyingContract_: "address" = verifying_contract
        value: "uint256"
        timestamp: "uint256"

    voucher = Voucher(value, timestamp)

    signedMessage = Account.sign_message(voucher.signable_message, signer.key)

    return signedMessage.signature