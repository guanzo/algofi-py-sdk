from algosdk.transaction import ApplicationNoOpTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup, int_to_bytes
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_send_keyreg_online_transactions(
    sender,
    suggested_params,
    storage_account,
    vote_pk,
    selection_pk,
    state_proof_pk,
    vote_first,
    vote_last,
    vote_key_dilution,
    manager_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
):
    """Returns a :class:`TransactionGroup` object representing a send keyreg
    transaction group transaction against the algofi protocol. The sender instructs
    the algo vault to register itself online to participate in Algorand's consensus.
    NOTE: The storage account address must be registered with a participation node
    in order for the account to participate in consensus. It is unsafe to register
    an account online without registering it with a participation node. See
    https://developer.algorand.org/docs/run-a-node/participate/generate_keys

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param vote_pk: vote key
    :type vote_pk: bytes
    :param selection_pk: selection key
    :type selection_pk: bytes
    :param state_proof_pk: state proof key
    :type state_proof_pk: bytes
    :param vote_first: first round to vote in consensus
    :type vote_first: int
    :param vote_last: last round to vote in consensus
    :type vote_last: int
    :param vote_key_dilution: vote key dilution
    :type vote_key_dilution: int
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
        transaction_type=Transactions.SEND_KEYREG_ONLINE_TXN,
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
            manager_strings.send_keyreg_txn.encode(),
            vote_pk,
            selection_pk,
            state_proof_pk,
            int_to_bytes(vote_first),
            int_to_bytes(vote_last),
            int_to_bytes(vote_key_dilution),
        ],
        accounts=[storage_account],
    )

    txn_group = TransactionGroup(prefix_transactions + [txn0])
    return txn_group
