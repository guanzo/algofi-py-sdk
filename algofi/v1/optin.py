from algosdk import logic
from algosdk.transaction import (
    ApplicationOptInTxn,
    AssetOptInTxn,
    ApplicationNoOpTxn,
    PaymentTxn,
)
from ..contract_strings import algofi_manager_strings as manager_strings
from ..utils import TransactionGroup, randint

OPT_IN_MIN_BALANCE = 3.5695


def prepare_manager_app_optin_transactions(
    manager_app_id,
    max_atomic_opt_in_market_app_ids,
    sender,
    storage_address,
    suggested_params,
):
    """Returns a :class:`TransactionGroup` object representing a manager opt in
    group transaction. The sender and storage account opt in to the manager application
    and the storage account is rekeyed to the manager account address, rendering it
    unable to be transacted against by the sender and therefore immutable.

    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param max_atomic_opt_in_market_app_ids: max opt in market app ids
    :type max_atomic_opt_in_market_app_ids: list
    :param sender: account address for the sender
    :type sender: string
    :param storage_address: address of the storage account
    :type storage_address: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :return: :class:`TransactionGroup` object representing a manager opt in group transaction
    :rtype: :class:`TransactionGroup`
    """
    txn_payment = PaymentTxn(
        sender=sender,
        sp=suggested_params,
        receiver=storage_address,
        amt=int(OPT_IN_MIN_BALANCE * 1e6),
    )
    market_opt_in_txns = []
    for market_app_id in max_atomic_opt_in_market_app_ids:
        txn = ApplicationOptInTxn(
            sender=storage_address, sp=suggested_params, index=market_app_id
        )
        market_opt_in_txns.append(txn)
    txn_user_opt_in_manager = ApplicationOptInTxn(
        sender=sender, sp=suggested_params, index=manager_app_id
    )
    app_address = logic.get_application_address(manager_app_id)
    txn_storage_opt_in_manager = ApplicationOptInTxn(
        sender=storage_address,
        sp=suggested_params,
        index=manager_app_id,
        rekey_to=app_address,
    )
    txn_group = TransactionGroup(
        [txn_payment]
        + market_opt_in_txns
        + [txn_user_opt_in_manager, txn_storage_opt_in_manager]
    )
    return txn_group


def prepare_market_app_optin_transactions(market_app_id, sender, suggested_params):
    """Returns a :class:`TransactionGroup` object representing a market opt in
    group transaction.

    :param market_app_id: id of the market application
    :type market_app_id: int
    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :return: :class:`TransactionGroup` object representing a market opt in group transaction
    :rtype: :class:`TransactionGroup`
    """
    txn = ApplicationOptInTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        note=randint(0, 1000000).to_bytes(8, "big"),
    )
    txn_group = TransactionGroup([txn])
    return txn_group


def prepare_asset_optin_transactions(asset_id, sender, suggested_params):
    """Returns a :class:`TransactionGroup` object representing an asset opt in
    group transaction.

    :param asset_id: id of the asset to opt into
    :type asset_id: int
    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :return: :class:`TransactionGroup` object representing an asset opt in group transaction
    :rtype: :class:`TransactionGroup`
    """
    txn = AssetOptInTxn(
        sender=sender,
        sp=suggested_params,
        index=asset_id,
    )
    txn_group = TransactionGroup([txn])
    return txn_group
