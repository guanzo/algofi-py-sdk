from algosdk.transaction import ApplicationNoOpTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup, int_to_bytes
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_remove_algos_from_vault_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    manager_app_id,
    market_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
):
    """Returns a :class:`TransactionGroup` object representing a remove algos from vault
    group transaction against the algofi protocol. Functionally equivalent to
    remove collateral + burn for the governance enabled algo vault. The sender
    requests to remove collateral from their storage account after which the application
    determines if the removal puts the sender's health ratio below 1. If not, the account sends
    back the user the amount of asset underlying their posted collateral.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of collateral to remove from the market
    :type amount: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the market application of the collateral
    :type market_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :return: :class:`TransactionGroup` object representing a remove collateral underlying group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.REMOVE_ALGOS_FROM_VAULT,
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
        app_args=[
            manager_strings.remove_collateral_underlying.encode(),
            int_to_bytes(amount),
        ],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.remove_collateral_underlying.encode()],
        foreign_apps=[manager_app_id],
        accounts=[storage_account],
    )
    txn_group = TransactionGroup(prefix_transactions + [txn0, txn1])
    return txn_group
