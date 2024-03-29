import json
import base64
from algosdk import encoding, logic
from algosdk.v2client.algod import AlgodClient
from ..utils import read_local_state, get_global_state, SCALE_FACTOR
from ..contract_strings import algofi_manager_strings as manager_strings
from ..contract_strings import algofi_market_strings as market_strings

class Manager:
    def __init__(self, algod_client: AlgodClient, manager_info):
        """Constructor method for manager object.

        :param algod_client: a :class:`AlgodClient` for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param manager_info: dictionary of manager information
        :type manager_info: dict
        """

        self.algod = algod_client

        self.manager_app_id = manager_info.get("manager_app_id")
        self.manager_address = logic.get_application_address(self.manager_app_id)
        
        # read market global state
        self.update_global_state()
    
    def update_global_state(self):
        """Method to fetch most recent manager global state.
        """
        manager_state = get_global_state(self.algod, self.manager_app_id)
        self.rewards_program_number = manager_state.get(manager_strings.n_rewards_programs, 0)
        self.rewards_amount = manager_state.get(manager_strings.rewards_amount, 0)
        self.rewards_per_second = manager_state.get(manager_strings.rewards_per_second, 0)
        self.rewards_asset_id = manager_state.get(manager_strings.rewards_asset_id, 0)
        self.rewards_secondary_ratio = manager_state.get(manager_strings.rewards_secondary_ratio, 0)
        self.rewards_secondary_asset_id = manager_state.get(manager_strings.rewards_secondary_asset_id, 0)
    
    # GETTERS
    
    def get_manager_app_id(self):
        """Return manager app id
        
        :return: manager app id
        :rtype: int
        """
        return self.manager_app_id

    def get_manager_address(self):
        """Return manager address
        
        :return: manager address
        :rtype: string
        """
        return self.manager_address

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

    # USER FUNCTIONS
    
    def get_storage_address(self, address):
        """Returns the storage address for the client user

        :param address: address to get info for
        :type address: string
        :return: storage account address for user
        :rtype: string
        """
        user_manager_state = read_local_state(self.algod, address, self.manager_app_id)
        raw_storage_address = user_manager_state.get(manager_strings.user_storage_address, None)
        if not raw_storage_address:
            raise Exception("No storage address found")
        return encoding.encode_address(base64.b64decode(raw_storage_address.strip()))
    
    def get_user_state(self, address):
        """Returns the market local state for address.

        :param address: address to get info for
        :type address: string
        :return: market local state for address
        :rtype: dict
        """
        result = {}
        storage_address = self.get_storage_address(address)
        user_state = read_local_state(self.algod, storage_address, self.manager_app_id)
        result["user_global_max_borrow_in_dollars"] = user_state.get(manager_strings.user_global_max_borrow_in_dollars, 0) 
        result["user_global_borrowed_in_dollars"] = user_state.get(manager_strings.user_global_borrowed_in_dollars, 0)
        return result