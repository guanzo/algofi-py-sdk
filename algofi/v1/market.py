import json
import base64
from algosdk import encoding, logic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from ..utils import (
    read_local_state,
    read_global_state,
    get_global_state_field,
    SCALE_FACTOR,
    PARAMETER_SCALE_FACTOR,
)
from ..contract_strings import algofi_manager_strings as manager_strings
from ..contract_strings import algofi_market_strings as market_strings
from .asset import Asset


class Market:
    def __init__(
        self,
        indexer_client: IndexerClient,
        historical_indexer_client: IndexerClient,
        market_app_id,
    ):
        """Constructor method for the market object.

        :param indexer_client: a :class:`IndexerClient` for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` for interacting with the network
        :type historical_indexer_client: :class:`IndexerClient`
        :param market_app_id: market app id
        :type market_app_id: int
        """

        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client

        self.market_app_id = market_app_id
        self.market_address = logic.get_application_address(self.market_app_id)
        self.created_at_round = self.indexer.applications(self.market_app_id)[
            "application"
        ].get("created-at-round")

        # read market global state
        self.update_global_state()

    def update_global_state(self, block=None):
        """Method to fetch most recent market global state.

        :param block: block at which to get historical data
        :type block: int, optional
        """
        indexer_client = self.historical_indexer if block else self.indexer
        market_state = read_global_state(
            indexer_client, self.market_app_id, block=block
        )
        # market constants
        self.market_counter = market_state[market_strings.manager_market_counter_var]

        # market asset info
        self.underlying_asset_id = market_state.get(market_strings.asset_id, None)
        self.bank_asset_id = market_state.get(market_strings.bank_asset_id, None)

        # market parameters
        self.oracle_app_id = market_state.get(market_strings.oracle_app_id, None)
        self.oracle_price_field = market_state.get(
            market_strings.oracle_price_field, None
        )
        self.oracle_price_scale_factor = market_state.get(
            market_strings.oracle_price_scale_factor, None
        )
        self.collateral_factor = market_state.get(
            market_strings.collateral_factor, None
        )
        self.liquidation_incentive = market_state.get(
            market_strings.liquidation_incentive, None
        )
        self.reserve_factor = market_state.get(market_strings.reserve_factor, None)
        self.base_interest_rate = market_state.get(
            market_strings.base_interest_rate, None
        )
        self.slope_1 = market_state.get(market_strings.slope_1, None)
        self.slope_2 = market_state.get(market_strings.slope_2, None)
        self.utilization_optimal = market_state.get(
            market_strings.utilization_optimal, None
        )
        self.market_supply_cap_in_dollars = market_state.get(
            market_strings.market_supply_cap_in_dollars, None
        )
        self.market_borrow_cap_in_dollars = market_state.get(
            market_strings.market_borrow_cap_in_dollars, None
        )

        # balance info
        self.active_collateral = market_state.get(market_strings.active_collateral, 0)
        self.bank_circulation = market_state.get(market_strings.bank_circulation, 0)
        self.bank_to_underlying_exchange = market_state.get(
            market_strings.bank_to_underlying_exchange, 0
        )
        self.underlying_borrowed = market_state.get(
            market_strings.underlying_borrowed, 0
        )
        self.outstanding_borrow_shares = market_state.get(
            market_strings.outstanding_borrow_shares, 0
        )
        self.underlying_cash = market_state.get(market_strings.underlying_cash, 0)
        self.underlying_reserves = market_state.get(
            market_strings.underlying_reserves, 0
        )
        self.total_borrow_interest_rate = market_state.get(
            market_strings.total_borrow_interest_rate, 0
        )

        self.asset = (
            Asset(
                self.indexer,
                self.historical_indexer,
                self.underlying_asset_id,
                self.bank_asset_id,
                self.oracle_app_id,
                self.oracle_price_field,
                self.oracle_price_scale_factor,
            )
            if self.underlying_asset_id
            else None
        )

    # GETTERS

    def get_market_app_id(self):
        """Returns the app id for this market

        :return: market app id
        :rtype: int
        """
        return self.market_app_id

    def get_market_address(self):
        """Returns the address for this market

        :return: market address
        :rtype: string
        """
        return self.market_address

    def get_market_counter(self):
        """Returns the market counter for this market

        :return: market counter
        :rtype: int
        """
        return self.market_counter

    def get_asset(self):
        """Returns asset object for this market

        :return: asset
        :rtype: :class:`Asset`
        """
        return self.asset

    def get_active_collateral(self, block=None):
        """Returns active_collateral for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: active_collateral
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.active_collateral,
                block=block,
            )
        else:
            return self.active_collateral

    def get_bank_circulation(self, block=None):
        """Returns bank_circulation for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: bank_circulation
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.bank_circulation,
                block=block,
            )
        else:
            return self.bank_circulation

    def get_bank_to_underlying_exchange(self, block=None):
        """Returns bank_to_underlying_exchange for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: bank_to_underlying_exchange
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.bank_to_underlying_exchange,
                block=block,
            )
        else:
            return self.bank_to_underlying_exchange

    def get_underlying_borrowed(self, block=None):
        """Returns underlying_borrowed for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: underlying_borrowed
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.underlying_borrowed,
                block=block,
            )
        else:
            return self.underlying_borrowed

    def get_outstanding_borrow_shares(self, block=None):
        """Returns outstanding_borrow_shares for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: outstanding_borrow_shares
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.outstanding_borrow_shares,
                block=block,
            )
        else:
            return self.outstanding_borrow_shares

    def get_underlying_cash(self, block=None):
        """Returns underlying_cash for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: underlying_cash
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.underlying_cash,
                block=block,
            )
        else:
            return self.underlying_cash

    def get_underlying_reserves(self, block=None):
        """Returns underlying_reserves for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: underlying_reserves
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.underlying_reserves,
                block=block,
            )
        else:
            return self.underlying_reserves

    def get_underlying_supplied(self, block=None):
        """Returns underlying supplied = underlying_cash + underlying_borrowed - underlying_reserves for this market.
        The mainnet STBL market was seeded with 1tn STBL, so this must be subtracted from the calculation.

        :param block: block at which to get historical data
        :type block: int, optional
        :return: underlying supplied
        :rtype: int
        """

        underlying_supplied = 0
        if self.market_app_id == 465814278:
            underlying_supplied += -int(1e18)
        if block:
            data = read_global_state(
                self.historical_indexer, self.market_app_id, block=block
            )
            underlying_supplied += (
                data[market_strings.underlying_cash]
                + data[market_strings.underlying_borrowed]
                + data[market_strings.underlying_reserves]
            )
        else:
            underlying_supplied += (
                self.underlying_cash
                + self.underlying_borrowed
                - self.underlying_reserves
            )
        return underlying_supplied

    def get_total_borrow_interest_rate(self, block=None):
        """Returns total_borrow_interest_rate for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: total_borrow_interest_rate
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.total_borrow_interest_rate,
                block=block,
            )
        else:
            return self.total_borrow_interest_rate

    def get_collateral_factor(self, block=None):
        """Returns collateral_factor for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: collateral_factor
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.collateral_factor,
                block=block,
            )
        else:
            return self.collateral_factor

    def get_liquidation_incentive(self, block=None):
        """Returns liquidation_incentive for this market

        :param block: block at which to get historical data
        :type block: int, optional
        :return: liquidation_incentive
        :rtype: int
        """
        if block:
            return get_global_state_field(
                self.historical_indexer,
                self.market_app_id,
                market_strings.liquidation_incentive,
                block=block,
            )
        else:
            return self.liquidation_incentive

    # USER FUNCTIONS

    def get_storage_state(self, storage_address, block=None):
        """Returns the market local state for address.

        :param storage_address: storage_address to get info for
        :type storage_address: string
        :param block: block at which to get historical data
        :type block: int, optional
        :return: market local state for address
        :rtype: dict
        """
        result = {}
        asset = self.get_asset()
        indexer_client = self.historical_indexer if block else self.indexer

        # load user local state
        user_state = read_local_state(
            indexer_client, storage_address, self.market_app_id, block=block
        )

        # load global state variables
        if block:
            self.update_global_state(block=block)

        result["active_collateral_bank"] = user_state.get(
            market_strings.user_active_collateral, 0
        )
        result["active_collateral_underlying"] = int(
            result["active_collateral_bank"]
            * self.bank_to_underlying_exchange
            / SCALE_FACTOR
        )
        result["active_collateral_usd"] = asset.to_usd(
            result["active_collateral_underlying"]
        )
        result["active_collateral_max_borrow_usd"] = (
            result["active_collateral_usd"]
            * self.collateral_factor
            / PARAMETER_SCALE_FACTOR
        )
        result["borrow_shares"] = user_state.get(market_strings.user_borrow_shares, 0)
        result["borrow_underlying"] = (
            int(
                self.underlying_borrowed
                * result["borrow_shares"]
                / self.outstanding_borrow_shares
            )
            if self.outstanding_borrow_shares > 0
            else 0
        )
        result["borrow_usd"] = asset.to_usd(result["borrow_underlying"])

        return result
