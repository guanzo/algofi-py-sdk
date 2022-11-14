from algosdk.future.transaction import ApplicationNoOpTxn, PaymentTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup
from ..contract_strings import algofi_manager_strings as manager_strings
from copy import deepcopy


def prepare_liquidate_transactions(
    sender,
    suggested_params,
    storage_account,
    liquidatee_storage_account,
    amount,
    manager_app_id,
    borrow_market_app_id,
    borrow_market_address,
    collateral_market_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
    collateral_bank_asset_id,
    borrow_asset_id=None,
    liquidate_update_fee=1000,
):
    """Returns a :class:`TransactionGroup` object representing a liquidate group
    transaction against the algofi protocol. The sender (liquidator) repays up to
    50% of the liquidatee's outstanding borrow and takes collateral of the liquidatee
    at a premium defined by the market. The liquidator first sends borrow assets to the
    account address of the borrow market. Then, the account of the collateral market is authorized
    to credit the liquidator with a greater value of the liquidatee's collateral. The liquidator can
    then remove collateral to underlying to convert the collateral to assets.
    NOTE: seizing vALGO collateral returns ALGOs not bAssets. all other markets return bAssets.

    :param sender: account address for the sender (liquidator)
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender (liquidator)
    :type storage_account: string
    :param liquidatee_storage_account: storage account address for liquidatee
    :type liquidatee_storage_account: string
    :param amount: amount of borrow the liquidator repays
    :type amount: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param borrow_market_app_id: id of the borrow market application
    :type borrow_market_app_id: int
    :param borrow_market_address: account address of the borrow market
    :type borrow_market_address: int
    :param collateral_market_app_id: id of the collateral market application
    :type collateral_market_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :param collateral_bank_asset_id: id of the collateral bank asset
    :type: int
    :param borrow_asset_id: id of the borrow asset, defaults to None (algo)
    :type borrow_asset_id: int, optional
    :return: :class:`TransactionGroup` object representing a liquidate group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.LIQUIDATE,
        sender=sender,
        suggested_params=suggested_params,
        manager_app_id=manager_app_id,
        supported_market_app_ids=supported_market_app_ids,
        supported_oracle_app_ids=supported_oracle_app_ids,
        storage_account=liquidatee_storage_account,
    )
    txn0 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=manager_app_id,
        app_args=[manager_strings.liquidate.encode()],
        foreign_apps=supported_market_app_ids,
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=borrow_market_app_id,
        app_args=[manager_strings.liquidate.encode()],
        foreign_apps=[manager_app_id, collateral_market_app_id],
        accounts=[liquidatee_storage_account],
    )
    if borrow_asset_id:
        txn2 = AssetTransferTxn(
            sender=sender,
            sp=suggested_params,
            receiver=borrow_market_address,
            amt=amount,
            index=borrow_asset_id,
        )
    else:
        txn2 = PaymentTxn(
            sender=sender,
            sp=suggested_params,
            receiver=borrow_market_address,
            amt=amount,
        )
    collateral_params = deepcopy(suggested_params)
    collateral_params.fee = liquidate_update_fee
    txn3 = ApplicationNoOpTxn(
        sender=sender,
        sp=collateral_params,
        index=collateral_market_app_id,
        app_args=[manager_strings.liquidate.encode()],
        foreign_apps=[manager_app_id, borrow_market_app_id],
        foreign_assets=[collateral_bank_asset_id],
        accounts=[liquidatee_storage_account, storage_account],
    )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1, txn2, txn3])
    return txn_group
