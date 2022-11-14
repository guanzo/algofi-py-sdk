# This sample is provided for demonstration purposes only.
# It is not intended for production use.
# This example does not constitute trading advice.
import os
from dotenv import dotenv_values
from algosdk import mnemonic, account
from algofi.v1.asset import Asset
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

# NOTE: Get the live governance address at https://governance.algorand.foundation/api/periods/
# under "sign_up_address" for the relevant governance period
# Specify your vote according to the formats that are permissible in the Algorand Foundation Spec
# https://github.com/algorandfoundation/governance/blob/main/af-gov1-spec.md
# Get the idx, vote choices based on the relevant voting session from https://governance.algorand.foundation/api/periods/

address = sender
governance_address = ""
vote_note = b'af/gov1:j[6,"a","c"]'  # NOTE: an example, not to be used in live voting necessarily

vault_address = client.manager.get_storage_address(address)

print("~" * 100)
print(
    "Processing send_governance_vote_transaction transaction for vault address "
    + vault_address
)
print("~" * 100)

txn = client.prepare_send_governance_vote_transactions(
    governance_address, note=vote_note, address=address
)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

# After sending, check your vote at
# https://governance.algorand.foundation/api/periods/<governance-period-slug>/governors/<vault_address>
# to confirm successful vote in voting session

# print final state
print("~" * 100)
print("Final State")
print("Sent governance transaction with note: " + str(vote_note))
print("~" * 100)
