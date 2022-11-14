# This sample is provided for demonstration purposes only.
# It is not intended for production use.
# This example does not constitute trading advice.
import os
from dotenv import dotenv_values
from algosdk import mnemonic, account
from algofi.v1.client import AlgofiTestnetClient, AlgofiMainnetClient
from algofi.utils import (
    get_ordered_symbols,
    prepare_payment_transaction,
    get_new_account,
)

from example_utils import print_market_state, print_user_state

### run setup.py before proceeding. make sure the .env file is set with mnemonic + storage_mnemonic.

# Hardcoding account keys is not a great practice. This is for demonstration purposes only.
# See the README & Docs for alternative signing methods.
my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")

# load user passphrase
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user["mnemonic"])
key = mnemonic.to_private_key(user["mnemonic"])

# IS_MAINNET
IS_MAINNET = False
client = (
    AlgofiMainnetClient(user_address=sender)
    if IS_MAINNET
    else AlgofiTestnetClient(user_address=sender)
)

collateral_symbol = client.get_active_ordered_symbols()[0]
borrow_symbol = client.get_active_ordered_symbols()[1]

# ENTER THE ADDRESS AND STORAGE ADDRESS OF THE LIQUIDATABLE USER
target_address = ""
target_storage_address = ""

# ENTER THE AMOUNT OF BORROW ASSET TO LIQUIDATE
amount = int(100)

# print initial state
print("~" * 100)
print("Initial State")
print("~" * 100)
print_user_state(client, borrow_symbol, target_address)
print_user_state(client, collateral_symbol, target_address)
print_market_state(client.get_market(borrow_symbol))
print_market_state(client.get_market(collateral_symbol))

asset_balance = client.get_user_balance(
    client.get_market(borrow_symbol).get_asset().get_underlying_asset_id()
)
if asset_balance == 0:
    raise Exception("user has no balance of borrow asset " + symbol)

print("~" * 100)
print("Processing liquidate transaction")
print("~" * 100)
print(
    "Processing transaction for borrow asset = %s and collateral asset = %s"
    % (borrow_symbol, collateral_symbol)
)
txn = client.prepare_liquidate_transactions(
    target_storage_address, borrow_symbol, amount, collateral_symbol
)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

# print final state
print("~" * 100)
print("Final State")
print("~" * 100)
print_user_state(client, borrow_symbol, target_address)
print_user_state(client, collateral_symbol, target_address)
print_market_state(client.get_market(symbol))
print_user_state(client, symbol, sender)
