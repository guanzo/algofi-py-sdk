
from algosdk.future.transaction import ApplicationNoOpTxn, PaymentTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_sync_vault_transactions(sender, suggested_params, storage_account, manager_app_id, market_app_id, supported_market_app_ids, supported_oracle_app_ids):
    """Returns a :class:`TransactionGroup` object representing a sync vault transaction
    against the algofi protocol. After governance rewards are paid to the storage account
    this function can be used to sync the extra algos with your algo collateral so they
    can be counted toward your account and removed if desired.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the asset market application
    :type market_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :return: :class:`TransactionGroup` object representing a mint to collateral group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.SYNC_VAULT,
        sender=sender,
        suggested_params=suggested_params,
        manager_app_id=manager_app_id,
        supported_market_app_ids=supported_market_app_ids,
        supported_oracle_app_ids=supported_oracle_app_ids,
        storage_account=storage_account
    )
    txn0 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=manager_app_id,
        app_args=[manager_strings.sync_vault.encode()],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.sync_vault.encode()],
        foreign_apps=[manager_app_id],
        accounts=[storage_account]
    )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1])
    return txn_group