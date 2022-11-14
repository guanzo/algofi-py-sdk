from algosdk.future.transaction import ApplicationNoOpTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_burn_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    asset_id,
    bank_asset_id,
    manager_app_id,
    market_app_id,
    market_address,
    supported_market_app_ids,
    supported_oracle_app_ids,
):
    """Returns a :class:`TransactionGroup` object representing a burn group
    transaction against the algofi protocol. Sender burns bank assets by sending them
    to the account address of the market application for the bank asset which in turn
    converts them to their underlying asset and sends back.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of bank asset to burn
    :type amount: int
    :param asset_id: asset id of the bank asset's underlying asset
    :type asset_id: int
    :param bank_asset_id: id of the bank asset to burn
    :type bank_asset_id: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the market application for the bank asset
    :type market_app_id: int
    :param market_address: account address for the market application
    :type market_address: string
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :return: :class:`TransactionGroup` object representing a burn group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.BURN,
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
        app_args=[manager_strings.burn.encode()],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.burn.encode()],
        foreign_apps=[manager_app_id],
        foreign_assets=[asset_id],
        accounts=[storage_account],
    )
    txn2 = AssetTransferTxn(
        sender=sender,
        sp=suggested_params,
        receiver=market_address,
        amt=amount,
        index=bank_asset_id,
    )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1, txn2])
    return txn_group
