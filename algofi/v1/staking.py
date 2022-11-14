from copy import deepcopy
from algosdk import logic
from algosdk.future.transaction import (
    ApplicationOptInTxn,
    AssetOptInTxn,
    ApplicationNoOpTxn,
    PaymentTxn,
    AssetTransferTxn,
)
from ..contract_strings import algofi_manager_strings as manager_strings
from .prepend import get_init_txns
from ..utils import TransactionGroup, Transactions, randint, int_to_bytes

OPT_IN_MIN_BALANCE = 0.65


def prepare_staking_contract_optin_transactions(
    manager_app_id, market_app_id, sender, storage_address, suggested_params
):
    """Returns a :class:`TransactionGroup` object representing a staking contract opt in
    group transaction. The sender and storage account opt in to the staking application
    and the storage account is rekeyed to the manager account address, rendering it
    unable to be transacted against by the sender and therefore immutable.

    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of market application
    :type market_app_id: int
    :param sender: account address for the sender
    :type sender: string
    :param storage_address: address of the storage account
    :type storage_address: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :return: :class:`TransactionGroup` object representing a manager opt in group transaction
    :rtype: :class:`TransactionGroup`
    """
    txn_payment = PaymentTxn(
        sender=sender,
        sp=suggested_params,
        receiver=storage_address,
        amt=int(OPT_IN_MIN_BALANCE * 1e6),
    )
    txn_market = ApplicationOptInTxn(
        sender=storage_address, sp=suggested_params, index=market_app_id
    )
    txn_user_opt_in_manager = ApplicationOptInTxn(
        sender=sender, sp=suggested_params, index=manager_app_id
    )
    app_address = logic.get_application_address(manager_app_id)
    txn_storage_opt_in_manager = ApplicationOptInTxn(
        sender=storage_address,
        sp=suggested_params,
        index=manager_app_id,
        rekey_to=app_address,
    )
    txn_group = TransactionGroup(
        [txn_payment, txn_market, txn_user_opt_in_manager, txn_storage_opt_in_manager]
    )
    return txn_group


def prepare_stake_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    manager_app_id,
    market_app_id,
    market_address,
    oracle_app_id,
    asset_id=None,
):
    """Returns a :class:`TransactionGroup` object representing a stake
    transaction against the algofi protocol. The sender sends assets to the
    staking account and is credited with a stake.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of asset to supply for minting collateral
    :type amount: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the asset market application
    :type market_app_id: int
    :param market_address: account address for the market application
    :type market_address: string
    :param oracle_app_id: id of the asset market application
    :type oracle_app_id: int
    :param asset_id: asset id of the asset being supplied, defaults to None (algo)
    :type asset_id: int, optional
    :return: :class:`TransactionGroup` object representing a mint to collateral group transaction
    :rtype: :class:`TransactionGroup`
    """
    supported_oracle_app_ids = [oracle_app_id]
    supported_market_app_ids = [market_app_id]
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.MINT_TO_COLLATERAL,
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
        app_args=[manager_strings.mint_to_collateral.encode()],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.mint_to_collateral.encode()],
        foreign_apps=[manager_app_id],
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


def prepare_unstake_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    manager_app_id,
    market_app_id,
    oracle_app_id,
    asset_id=None,
):
    """Returns a :class:`TransactionGroup` object representing a remove stake
    group transaction against the algofi protocol. The sender requests to remove stake
    from a stake acount and if successful, the stake is removed.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.future.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of collateral to remove from the market
    :type amount: int
    :param asset_id: asset id of the asset underlying the collateral
    :type asset_id: int
    :param manager_app_id: id of the manager application
    :type manager_app_id: int
    :param market_app_id: id of the market application of the collateral
    :type market_app_id: int
    :param oracle_app_id: id of the oracle application of the collateral
    :type oracle_app_id: int
    :return: :class:`TransactionGroup` object representing a remove collateral underlying group transaction
    :rtype: :class:`TransactionGroup`
    """
    supported_market_app_ids = [market_app_id]
    supported_oracle_app_ids = [oracle_app_id]
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.REMOVE_COLLATERAL_UNDERLYING,
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
    if asset_id:
        txn1 = ApplicationNoOpTxn(
            sender=sender,
            sp=suggested_params,
            index=market_app_id,
            app_args=[manager_strings.remove_collateral_underlying.encode()],
            foreign_apps=[manager_app_id],
            foreign_assets=[asset_id],
            accounts=[storage_account],
        )
    else:
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


def prepare_claim_staking_rewards_transactions(
    sender,
    suggested_params,
    storage_account,
    manager_app_id,
    market_app_id,
    oracle_app_id,
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
    :param market_app_id: id of the market application of the collateral
    :type market_app_id: int
    :param oracle_app_id: id of the oracle application
    :type oracle_app_id: int
    :param foreign_assets: list of rewards assets in the staking contract
    :type foreign_assets: list
    :return: :class:`TransactionGroup` object representing a claim rewards transaction
    :rtype: :class:`TransactionGroup`
    """
    supported_market_app_ids = [market_app_id]
    supported_oracle_app_ids = [oracle_app_id]
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.CLAIM_REWARDS,
        sender=sender,
        suggested_params=suggested_params,
        manager_app_id=manager_app_id,
        supported_market_app_ids=supported_market_app_ids,
        supported_oracle_app_ids=supported_oracle_app_ids,
        storage_account=storage_account,
    )

    suggested_params_modified = deepcopy(suggested_params)
    suggested_params_modified.fee = 3000

    txn0 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params_modified,
        index=manager_app_id,
        app_args=[manager_strings.claim_rewards.encode()],
        accounts=[storage_account],
        foreign_assets=foreign_assets,
    )

    txn_group = TransactionGroup(prefix_transactions + [txn0])
    return txn_group
