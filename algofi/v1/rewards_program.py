import json
import base64
import time
from algosdk import encoding, logic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from ..utils import (
    read_local_state,
    read_global_state,
    SCALE_FACTOR,
    REWARDS_SCALE_FACTOR,
    PARAMETER_SCALE_FACTOR,
)
from ..contract_strings import algofi_manager_strings as manager_strings
from ..contract_strings import algofi_market_strings as market_strings


class RewardsProgram:
    def __init__(
        self,
        indexer_client: IndexerClient,
        historical_indexer_client: IndexerClient,
        manager_state,
    ):
        """Constructor method for manager object.

        :param indexer_client: a :class:`IndexerClient` for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` for interacting with the network
        :type historical_indexer_client: :class:`IndexerClient`
        :param manager_state: dictionary of manager global state
        :type manager_state: dict
        """

        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client

        self.latest_rewards_time = manager_state.get(
            manager_strings.latest_rewards_time, 0
        )
        self.rewards_program_number = manager_state.get(
            manager_strings.n_rewards_programs, 0
        )
        self.rewards_amount = manager_state.get(manager_strings.rewards_amount, 0)
        self.rewards_per_second = manager_state.get(
            manager_strings.rewards_per_second, 0
        )
        self.rewards_asset_id = manager_state.get(manager_strings.rewards_asset_id, 0)
        self.rewards_secondary_ratio = manager_state.get(
            manager_strings.rewards_secondary_ratio, 0
        )
        self.rewards_secondary_asset_id = manager_state.get(
            manager_strings.rewards_secondary_asset_id, 0
        )
        self.rewards_bitmap = manager_state.get(manager_strings.rewards_bitmap, 0)
        self.rewards_dist_by_market = manager_state.get(
            manager_strings.rewards_dist_by_market, 0
        )

    # GETTERS

    def get_rewards_asset_ids(self):
        """Return a list of current rewards assets

        :return: rewards asset list
        :rtype: list
        """
        result = []
        if self.rewards_asset_id > 1:
            result.append(self.rewards_asset_id)
        if self.rewards_secondary_asset_id > 1:
            result.append(self.rewards_secondary_asset_id)
        return result

    def get_latest_rewards_time(self):
        """Return latest rewards time

        :return: latest rewards time
        :rtype: int
        """
        return self.latest_rewards_time

    def get_rewards_program_number(self):
        """Return rewards program number

        :return: rewards program number
        :rtype: int
        """
        return self.rewards_program_number

    def get_rewards_amount(self):
        """Return rewards amount

        :return: rewards amount
        :rtype: int
        """
        return self.rewards_amount

    def get_rewards_per_second(self):
        """Return rewards per second

        :return: rewards per second
        :rtype: int
        """
        return self.rewards_per_second

    def get_rewards_asset_id(self):
        """Return rewards asset id

        :return: rewards asset id
        :rtype: int
        """
        return self.rewards_asset_id

    def get_rewards_secondary_ratio(self):
        """Return rewards secondary ratio

        :return: rewards secondary ratio
        :rtype: int
        """
        return self.rewards_secondary_ratio

    def get_rewards_secondary_asset_id(self):
        """Return rewards secondary asset id

        :return: rewards secondary asset id
        :rtype: int
        """
        return self.rewards_secondary_asset_id

    # USER FUNCTIONS

    def get_storage_unrealized_rewards(self, storage_address, manager, markets):
        """Return the projected claimable rewards for a given storage_address.
        Ordering of markets must be as seen in contracts.json.

        :param storage_address:
        :type storage_address: string
        :param manager: a :class:`Manager` object representing the manger application
        :type manager: :class:`Manager`
        :param markets: list of markets to get unrealized rewards for
        :type markets: list
        :return: tuple of primary and secondary unrealized rewards
        :rtype: (int, int)
        """
        # get raw user state
        manager_state = read_global_state(self.indexer, manager.get_manager_app_id())
        manager_storage_state = read_local_state(
            self.indexer, storage_address, manager.get_manager_app_id()
        )
        on_current_program = (
            self.get_rewards_program_number()
            == manager_storage_state.get(manager_strings.user_rewards_program_number, 0)
        )
        total_unrealized_rewards = (
            manager_storage_state.get(manager_strings.user_pending_rewards, 0)
            if on_current_program
            else 0
        )
        total_secondary_unrealized_rewards = (
            manager_storage_state.get(manager_strings.user_secondary_pending_rewards, 0)
            if on_current_program
            else 0
        )
        rewards_bitmap = list(
            map(
                lambda x: True if x == "1" else False,
                bin(self.rewards_bitmap)[::-1][:-2],
            )
        )
        rewards_dist_by_market = bin(self.rewards_dist_by_market)[::-1][:-2]

        # loop through to get the weighted tvl
        market_tvl = {}
        market_weighted_tvl_usd = {}
        total_weighted_tvl_usd = 0
        for i in range(len(markets)):
            market = markets[i]
            is_in_rewards = rewards_bitmap[i]
            if is_in_rewards:
                rewards_dist_param = int(rewards_dist_by_market[4 * i : 4 * (i + 1)], 2)
                market_underlying_tvl = market.get_underlying_borrowed() + (
                    market.get_active_collateral()
                    * market.get_bank_to_underlying_exchange()
                    / SCALE_FACTOR
                )
                market_tvl[market] = market_underlying_tvl
                market_underlying_weighted_tvl_usd = market.get_asset().to_usd(
                    market_underlying_tvl
                )
                market_weighted_tvl_usd[market] = market_underlying_weighted_tvl_usd
                total_weighted_tvl_usd += market_underlying_weighted_tvl_usd
            else:
                market_tvl[market] = 0
                market_weighted_tvl_usd[market] = 0
                total_weighted_tvl_usd += 0

        # calculate the projected rewards for the next coefficient
        time_elapsed = int(time.time()) - self.get_latest_rewards_time()
        rewards_issued = (
            time_elapsed * self.get_rewards_per_second()
            if self.get_rewards_amount() > 0
            else 0
        )

        for market in markets:
            # get coefficients
            market_counter_prefix = (
                market.get_market_counter().to_bytes(8, byteorder="big").decode("utf-8")
            )
            coefficient = manager_state.get(
                market_counter_prefix
                + manager_strings.counter_indexed_rewards_coefficient,
                0,
            )
            user_coefficient = (
                manager_storage_state.get(
                    market_counter_prefix
                    + manager_strings.counter_to_user_rewards_coefficient_initial
                )
                if on_current_program
                else 0
            )

            rewards_distributed_to_market = (
                rewards_issued * market_weighted_tvl_usd[market]
            ) / total_weighted_tvl_usd
            projected_coefficient = coefficient + int(
                (rewards_distributed_to_market * REWARDS_SCALE_FACTOR)
                / (market_tvl[market])
            )

            market_storage_state = market.get_storage_state(storage_address)
            user_tvl = (
                market_storage_state["active_collateral_underlying"]
                + market_storage_state["borrow_underlying"]
            )
            unrealized_rewards = int(
                (projected_coefficient - user_coefficient)
                * user_tvl
                / REWARDS_SCALE_FACTOR
            )
            secondary_unrealized_rewards = int(
                unrealized_rewards
                * self.get_rewards_secondary_ratio()
                / PARAMETER_SCALE_FACTOR
            )

            total_unrealized_rewards += unrealized_rewards
            total_secondary_unrealized_rewards += secondary_unrealized_rewards
        return total_unrealized_rewards, total_secondary_unrealized_rewards
