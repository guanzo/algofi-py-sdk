from algosdk.transaction import ApplicationNoOpTxn, PaymentTxn, AssetTransferTxn
from .prepend import get_init_txns
from ..utils import Transactions, TransactionGroup
from ..contract_strings import algofi_manager_strings as manager_strings


def prepare_mint_transactions(
    sender,
    suggested_params,
    storage_account,
    amount,
    bank_asset_id,
    manager_app_id,
    market_app_id,
    market_address,
    supported_market_app_ids,
    supported_oracle_app_ids,
    asset_id=None,
):
    """Returns a :class:`TransactionGroup` object representing a mint group
    transaction against the algofi protocol. bAssets are not automatically
    posted to collateral as in `prepare_mint_to_collateral_transactions`.
    Sender sends assets to the account of the asset market application which
    then sends an amount of market bank assets to the user.

    :param sender: account address for the sender
    :type sender: string
    :param suggested_params: suggested transaction params
    :type suggested_params: :class:`algosdk.transaction.SuggestedParams` object
    :param storage_account: storage account address for sender
    :type storage_account: string
    :param amount: amount of asset to supply for minting bank assets
    :type amount: int
    :param bank_asset_id: asset id of the bank asset to be minted
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
    :param asset_id: asset id of the asset being supplied, defaults to None (algo)
    :type asset_id: int, optional
    :return: :class:`TransactionGroup` object representing a mint group transaction
    :rtype: :class:`TransactionGroup`
    """
    prefix_transactions = get_init_txns(
        transaction_type=Transactions.MINT,
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
        app_args=[manager_strings.mint.encode()],
    )
    txn1 = ApplicationNoOpTxn(
        sender=sender,
        sp=suggested_params,
        index=market_app_id,
        app_args=[manager_strings.mint.encode()],
        foreign_apps=[manager_app_id],
        foreign_assets=[bank_asset_id],
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
