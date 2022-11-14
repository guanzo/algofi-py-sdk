import time
from dotenv import dotenv_values, set_key
import os

from algosdk import mnemonic, account
from algofi.v1.client import AlgofiTestnetClient, AlgofiMainnetClient
from algofi.utils import get_new_account
from algofi.v1.optin import prepare_asset_optin_transactions

my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")

# IS_MAINNET?
IS_MAINNET = False

# load user passphrase
user = dotenv_values(ENV_PATH)

# Hardcoding account keys is not a great practice. This is for demonstration purposes only.
# See the README & Docs for alternative signing methods.
for passphrase in ["mnemonic"]:
    sender = mnemonic.to_public_key(user[passphrase])
    print("setting up for " + sender)
    key = mnemonic.to_private_key(user[passphrase])

    client = (
        AlgofiMainnetClient(user_address=sender)
        if IS_MAINNET
        else AlgofiTestnetClient(user_address=sender)
    )

    # Opting primary account into the available assets
    assets = client.get_active_asset_ids() + client.get_active_bank_asset_ids()
    for i in range(len(assets)):
        asset_id = assets[i]
        if asset_id != 1 and not client.is_opted_into_asset(asset_id, sender):
            print("Opting into asa: ", asset_id)
            txn = prepare_asset_optin_transactions(
                asset_id, sender, client.get_default_params()
            )
            txn.sign_with_private_key(sender, key)
            txn.submit(client.algod, wait=False if (i != (len(assets) - 1)) else True)

    # generate storage account
    storage_key, storage_account, storage_passphrase = get_new_account()

    # opt into lending protocol
    print("Opting in to protocol")
    txn = client.prepare_optin_transactions(storage_account, sender)
    txn.sign_with_private_keys(
        [key]
        + [storage_key] * len(client.get_max_atomic_opt_in_market_app_ids())
        + [key, storage_key]
    )
    txn.submit(client.algod, wait=True)
