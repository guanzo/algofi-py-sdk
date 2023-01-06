from algosdk.transaction import ApplicationNoOpTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup, int_to_bytes
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_borrow_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    asset_id,
    manager_app_id,
    market_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
):
    """Returns a :class:`TransactionGroup` object representing an borrow group
    transaction against the algofi protocol. Protocol sends requested borrow asset
    to the sender account provided sufficient collateral has been posted

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of asset to borrow
    :type amount: int
    :param asset_id: asset id of the asset to be borrowed
    :type asset_id: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the market application for the borrow asset
    :type market_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :return: :class:`TransactionGroup` object representing a borrow group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.BORROW,
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
        app_args=[manager_strings.borrow.encode(), int_to_bytes(amount)],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.borrow.encode()],
        foreign_apps=[manager_app_id],
        foreign_assets=[asset_id],
        accounts=[storage_account],
    )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1])
    return txn_group
