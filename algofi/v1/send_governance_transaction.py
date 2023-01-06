from algosdk.transaction import ApplicationNoOpTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup, int_to_bytes
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_send_governance_transactions(
    sender,
    suggested_params,
    storage_account,
    governance_address,
    note,
    manager_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
):
    """Returns a :class:`TransactionGroup` object representing a send governance
    transaction group transaction against the algofi protocol. The sender either (1) instructs
    the algo vault to opt into governance or (2) vote on governance issues by sending
    a zero value payment inner transaction to the governance address with the commitment
    or vote specified in the notes field. For commitment, the user can optionally
    specify a beneficiary - an account that receives the rewards payout at the conclusion
    of governance.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param governance_address: address to send the governance commitment / vote zero value payment txn to
    :type governance_address: string
    :param note: note encoding the governance commitment json
    :type note: string
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :return: :class:`TransactionGroup` object representing a claim rewards transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.SEND_GOVERNANCE_TXN,
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
        app_args=[manager_strings.send_governance_txn.encode()],
        accounts=[storage_account, governance_address],
        note=note,
    )

    txn_group = TransactionGroup(prefix_transactions + [txn0])
    return txn_group
