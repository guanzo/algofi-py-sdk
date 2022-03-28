# This sample is provided for demonstration purposes only.
# It is not intended for production use.
# This example does not constitute trading advice.
import os
import base64
from dotenv import dotenv_values
from algosdk import mnemonic, account, encoding
from algofi.v1.client import AlgofiTestnetClient, AlgofiMainnetClient
from algofi.utils import get_ordered_symbols, prepare_payment_transaction, get_new_account
from example_utils import print_market_state, print_user_state

### run setup.py before proceeding. make sure the .env file is set with mnemonic + storage_mnemonic.

# Hardcoding account keys is not a great practice. This is for demonstration purposes only.
# See the README & Docs for alternative signing methods.
my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")

# load user passphrase
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user['mnemonic'])
key =  mnemonic.to_private_key(user['mnemonic'])

# IS_MAINNET
IS_MAINNET = False
client = AlgofiMainnetClient(user_address=sender) if IS_MAINNET else AlgofiTestnetClient(user_address=sender)

print("~"*100)
print("Processing send_keyreg_transaction transaction")
print("~"*100)

# NOTE: input participation information for storage account
vote_pk = "zQ1+0ixcwkei0pAGUJDVR0W2xyMwjnfi8GJ+0YtcL4A="
selection_pk = "vAtgaY8PH2YkXRREfjYUYc9xe5iKR18ozQmSTyjj2/E="
state_proof_pk = "K6kJDPM1TWiiYWPYVTZTPpo2nNRLMkHJKlUpmmXpoOCshU1ItrvdetTcbTz78FXTwJFSdRos7+IzuJr+IJlc/Q=="
vote_pk = base64.b64decode(vote_pk)
selection_pk = base64.b64decode(selection_pk)
state_proof_pk = base64.b64decode(state_proof_pk)
vote_first = 20367767
vote_last = 23367767
vote_key_dilution = 10000

txn = client.prepare_send_keyreg_transactions(vote_pk, selection_pk, state_proof_pk, vote_first, vote_last, vote_key_dilution, sender)
txn.sign_with_private_key(sender, key)
txn.submit(client.algod, wait=True)

# print final state
print("~"*100)
print("Final State")
print("~"*100)