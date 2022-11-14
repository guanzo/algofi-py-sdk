# This sample is provided for demonstration purposes only.
# It is not intended for production use.
# This example does not constitute trading advice.
import os
import base64
from dotenv import dotenv_values
from algosdk import mnemonic, account, encoding
from algofi.v1.client import AlgofiTestnetClient, AlgofiMainnetClient

from example_utils import print_staking_contract_state

### run setup.py before proceeding. make sure the .env file is set with mnemonic + storage_mnemonic.

# Hardcoding account keys is not a great practice. This is for demonstration purposes only.
# See the README & Docs for alternative signing methods.
my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")

# load user passphrase
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user["mnemonic"])
key = mnemonic.to_private_key(user["mnemonic"])

# get_staking_user_state

# IS_MAINNET
IS_MAINNET = False
client = (
    AlgofiMainnetClient(user_address=sender)
    if IS_MAINNET
    else AlgofiTestnetClient(user_address=sender)
)

# for mint to collateral txn
collateral_symbol = "ALGO"
borrow_symbol = "STBL"
staking_contract_name = "STBL"

# print initial state
print("~" * 100)
print("Initial state")
print("~" * 100)
print_staking_contract_state(client, staking_contract_name, sender)

print("~" * 100)
print("Processing mint_to_collateral transaction")
print("~" * 100)

# mint collateral
txn = client.prepare_mint_to_collateral_transactions(
    collateral_symbol, int(1 * 1e6), sender
)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

print("~" * 100)
print("Processing borrow transaction")
print("~" * 100)

# borrow stbl
txn = client.prepare_borrow_transactions(borrow_symbol, int(0.5 * 1e6), sender)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

print("~" * 100)
print("Processing staking transaction")
print("~" * 100)

# stake
txn = client.prepare_stake_transactions(staking_contract_name, int(0.5 * 1e6), sender)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

# print post stake state
print("~" * 100)
print("Post-staking state")
print("~" * 100)
print_staking_contract_state(client, staking_contract_name, sender)

print("~" * 100)
print("Processing unstaking transaction")
print("~" * 100)

# unstake
txn = client.prepare_unstake_transactions(staking_contract_name, int(0.5 * 1e6), sender)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

# print post unstake state
print("~" * 100)
print("Post-unstaking state")
print("~" * 100)
print_staking_contract_state(client, staking_contract_name, sender)
