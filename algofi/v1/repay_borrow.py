from algosdk.transaction import ApplicationNoOpTxn, PaymentTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_repay_borrow_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    manager_app_id,
    market_app_id,
    market_address,
    supported_market_app_ids,
    supported_oracle_app_ids,
    asset_id=None,
):
    """Returns a :class:`TransactionGroup` object representing a repay borrow
    group transaction against the algofi protocol. The sender repays assets to the
    market of the borrow asset after which the market application decreases the
    outstanding borrow amount for the sender.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of borrow asset to repay
    :type amount: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the market application of the borrow asset
    :type market_app_id: int
    :param market_address: account address for the market application
    :type market_address: string
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :param asset_id: asset id of the borrow asset, defaults to None (algo)
    :type asset_id: int, optional
    :return: :class:`TransactionGroup` object representing a remove collateral group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.REPAY_BORROW,
        sender=sender,
        suggested_params=suggested_params,
        manager_app_id=manager_app_id,
        supported_market_app_ids=supported_market_app_ids,
        supported_oracle_app_ids=supported_oracle_app_ids,
        storage_account=storage_account,
    )
    txn0 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=manager_app_id,
        app_args=[manager_strings.repay_borrow.encode()],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.repay_borrow.encode()],
        foreign_apps=[manager_app_id],
        foreign_assets=[asset_id] if asset_id else [],
        accounts=[storage_account],
    )
    if asset_id:
        txn2 = AssetTransferTxn(
            sender=sender,
            sp=suggested_params,
            receiver=market_address,
            amt=amount,
            index=asset_id,
        )
    else:
        txn2 = PaymentTxn(
            sender=sender, sp=suggested_params, receiver=market_address, amt=amount
        )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1, txn2])
    return txn_group
