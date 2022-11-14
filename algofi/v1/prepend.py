from copy import deepcopy
from random import randint
from algosdk.future.transaction import ApplicationNoOpTxn
from ..utils import Transactions
from ..contract_strings import algofi_manager_strings as manager_strings

# AVM currently supports 9 dummy transactions to "buy" more ops
NUM_DUMMY_TXNS = 9
# mapping from integer to word
dummy_txn_num_to_word = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}


def get_init_txns(
    transaction_type,
    sender,
    suggested_params,
    manager_app_id,
    supported_market_app_ids,
    supported_oracle_app_ids,
    storage_account,
):
    """Returns a :class:`TransactionGroup` object representing the initial transactions
    executed by the algofi protocol during a standard group transaction. The transactions are
    (1) fetch market variables, (2) update prices, (3) update protocol data, and (4) degenerate ("dummy")
    transactions to increase the number of cost units allowed (currently each transactions affords 700
    additional cost units).

    :param transaction_type: a :class:`Transactions` enum representing the group transaction the init transactions are used for
    :type transaction_type: :class:`Transactions`
    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param supported_market_app_ids: list of supported market application ids
    :type supported_market_app_ids: list
    :param supported_oracle_app_ids: list of supported oracle application ids
    :type supported_oracle_app_ids: list
    :param storage_account: account address for the storage account
    :type storage_account: string
    :return: list of transactions representing the initial transactions
    :rtype: list
    """
    suggested_params_modified = deepcopy(suggested_params)
    # if inner transaction is required, increase fee to 2000 microalgos
    if transaction_type in [
        Transactions.MINT,
        Transactions.BURN,
        Transactions.REMOVE_COLLATERAL,
        Transactions.REMOVE_COLLATERAL_UNDERLYING,
        Transactions.BORROW,
        Transactions.REPAY_BORROW,
        Transactions.LIQUIDATE,
        Transactions.CLAIM_REWARDS,
        Transactions.SEND_GOVERNANCE_TXN,
        Transactions.SEND_KEYREG_ONLINE_TXN,
        Transactions.SEND_KEYREG_OFFLINE_TXN,
    ]:
        suggested_params_modified.fee = 2000
    elif transaction_type in [Transactions.REMOVE_ALGOS_FROM_VAULT]:
        suggested_params_modified.fee = 4000
    # refresh market variables on manager, update prices on manager and update protocol data + add dummy txns to "buy" cost units
    txn0 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=manager_app_id,
        app_args=[manager_strings.fetch_market_variables.encode()],
        foreign_apps=supported_market_app_ids,
        note=randint(0, 1000000).to_bytes(8, "big"),
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params_modified,
        index=manager_app_id,
        app_args=[manager_strings.update_prices.encode()],
        foreign_apps=supported_oracle_app_ids,
    )
    txn2 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=manager_app_id,
        app_args=[manager_strings.update_protocol_data.encode()],
        foreign_apps=supported_market_app_ids,
        accounts=[storage_account],
    )
    dummy_txns = []
    for i in range(1, NUM_DUMMY_TXNS + 1):
        "dummy_" + dummy_txn_num_to_word[i]
        txn = ApplicationNoOpTxn(
            sender=sender,
            sp=suggested_params,
            index=manager_app_id,
            app_args=[bytes("dummy_" + dummy_txn_num_to_word[i], "utf-8")],
            foreign_apps=supported_market_app_ids,
        )
        dummy_txns.append(txn)
    return [txn0, txn1, txn2] + dummy_txns
