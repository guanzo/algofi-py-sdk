from algosdk.future.transaction import ApplicationNoOpTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup, int_to_bytes
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_claim_rewards_transactions(
    sender,
    suggested_params,
    storage_account,
    manager_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
    foreign_assets,
):
    """Returns a :class:`TransactionGroup` object representing a claim rewards
    underlying group transaction against the algofi protocol. The sender requests
    to claim rewards from the manager acount. If not, the account sends
    back the user the amount of asset underlying their posted collateral.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :param foreign_assets: list of rewards assets in the staking contract
    :type foreign_assets: list
    :return: :class:`TransactionGroup` object representing a claim rewards transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.CLAIM_REWARDS,
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
        app_args=[manager_strings.claim_rewards.encode()],
        accounts=[storage_account],
        foreign_assets=foreign_assets,
    )

    txn_group = TransactionGroup(prefix_transactions + [txn0])
    return txn_group
