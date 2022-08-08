import json
import base64
from algosdk import encoding, logic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from ..utils import read_local_state, read_global_state, SCALE_FACTOR
from ..contract_strings import algofi_manager_strings as manager_strings
from ..contract_strings import algofi_market_strings as market_strings
from .asset import Asset
from .manager import Manager
from .market import Market

class StakingContract:
    def __init__(self, indexer_client: IndexerClient, historical_indexer_client: IndexerClient, staking_contract_info):
        """Constructor method for the generic client.

        :param indexer_client: a :class:`IndexerClient` for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` for interacting with the network
        :type historical_indexer_client: :class:`IndexerClient`
        :param staking_contract_info: dictionary of staking contract information
        :type staking_contract_info: dict
        """

        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client

        self.manager = Manager(self.indexer, self.historical_indexer, staking_contract_info.get("managerAppId"))
        self.market = Market(self.indexer, self.historical_indexer, staking_contract_info.get("marketAppId"))
        
        # read manager and market global state
        self.update_global_state()
    
    def update_global_state(self, block=None):
        """Method to fetch most recent staking contract global state

        :param block: block at which to get historical data
        :type block: int, optional
        """
        indexer_client = self.historical_indexer if block else self.indexer
        self.get_manager().update_global_state(block=block)
        self.get_market().update_global_state(block=block)

    # GETTERS
    
    def get_manager(self):
        """Return staking contract manager
        
        :return: manager
        :rtype: :class:`Manager`
        """
        return self.manager
        
    def get_market(self):
        """Return staking contract market
        
        :return: market
        :rtype: :class:`Market`
        """
        return self.market

    def get_asset(self):
        """Returns asset object for this market

        :return: asset
        :rtype: :class:`Asset`
        """
        return self.get_market().get_asset()
    
    def get_manager_app_id(self):
        """Return manager app id
        
        :return: manager app id
        :rtype: int
        """
        return self.get_manager().get_manager_app_id()
    
    def get_manager_address(self):
        """Return manager address
        
        :return: manager address
        :rtype: string
        """
        return self.get_manager().get_manager_address()
    
    def get_market_app_id(self):
        """Returns the market app id

        :return: market app id
        :rtype: int
        """
        return self.get_market().get_market_app_id()
    
    def get_market_address(self):
        """Returns the market address
        
        :return: market address
        :rtype: string
        """
        return self.get_market().get_market_address()

    def get_oracle_app_id(self):
        """Returns the oracle app id
        
        :return: oracle app id
        :rtype: int
        """
        return self.get_market().get_asset().get_oracle_app_id()

    def get_staked(self):
        """Return staked amount
        
        :return: staked
        :rtype: int
        """
        return self.get_market().get_active_collateral()

    def get_rewards_program(self):
        """Return a list of current rewards program
        
        :return: rewards program
        :rtype: :class:`RewardsProgram`
        """
        return self.get_manager().get_rewards_program()

    # USER FUNCTIONS

    def get_storage_address(self, address):
        """Returns the staking contract storage address for the given address or None if it does not exist.

        :param address: address to get info for
        :type address: string
        :return: storage account address for user
        :rtype: string
        """
        return self.get_manager().get_storage_address(address)
    
    def get_user_state(self, address):
        """Returns the staking contract local state for address.

        :param address: address to get info for
        :type address: string
        :return: staking contract local state for address
        :rtype: dict
        """
        storage_address = self.get_storage_address(address)
        if not storage_address:
            raise Exception("no storage address found")
        return self.get_storage_state(storage_address)
    
    def get_storage_state(self, storage_address):
        """Returns the staking contract local state for storage_address.

        :param storage_address: storage address to get info for
        :type storage_address: string
        :return: staking contract local state for address
        :rtype: dict
        """
        result = {}
        unrealized_rewards, secondary_unrealized_rewards = self.get_manager().get_storage_unrealized_rewards(storage_address, [self.get_market()])
        result["unrealized_rewards"] = unrealized_rewards
        result["secondary_unrealized_rewards"] = secondary_unrealized_rewards
    
        user_market_state = self.get_market().get_storage_state(storage_address)
        result["staked_bank"] = user_market_state["active_collateral_bank"]
        result["staked_underlying"] = user_market_state["active_collateral_underlying"]
        
        return result