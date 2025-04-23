"""
This file contains classes for making cached calls to EZ Office API endpoints.
The parent class EzoCache contains basic caching functionality.
Child classes extend EzoCache and add endpoint specific methods.
"""

from pprint import pprint
import pickle

import ezoff
from .exceptions import *
from .data_model import *


class EzoCache:
    """Parent class for caching EZ Office API data."""

    def __init__(self, debug: bool = False, use_saved: bool = False):
        self.cache: Dict[int, BaseModel] = {}
        # Mappings of identification number to id.
        self.cache_id_nums: Dict[str, int] = {}
        self._debug = debug
        self._use_saved = use_saved
        self._pickle_file_name: str = None
        self._api_call_single = None
        self._api_call_multi = None
        self._data_model: BaseModel = None
        self._not_found_exception: Exception = None

    def get_cache_entry(self, entry_id: int, force_api: bool = False) -> BaseModel:
        """
        Returns BaseModel object representing the entry identified by entry_id.
        Subsequent calls referencing the same entry_id will be retrieved from
        the local cache instead of making further calls to the EZO API.
        Args:
            entry_id (int): ID of entry to return.
            force_api (bool): Get data from API even when cached copy exists.
        Raises:
            self._not_found_exception: Raised when entry_id is not found.
        Returns:
            BaseModel: Pydantic object.
        """
        if force_api or entry_id not in self.cache:
            try:
                self.cache[entry_id] = self._api_call_single(asset_id=entry_id)
                return self.cache[entry_id]

            except self._not_found_exception as e:
                raise self._not_found_exception(
                    f"Asset ID {entry_id} not found. {str(e)}"
                )

        return self.cache[entry_id]

    def clear(self):
        """Clears EZO cached data."""
        self.cache = {}

    def download(self, filter: dict = None) -> None:
        """
        Downloads EZO data into local cache.
        New data is appended to or overwrites locally cached data.
        Args:
            filter (dict, optional): Body/payload filter data for limiting results. See EZ Office API v2 for filter schema.
        """
        print("Downloading from EZ Office.")

        if filter:
            print(f"Using filter: {filter}")

        # Use saved pickle or save a pickle when running in debug mode.
        if self._debug:
            if self._use_saved:
                with open(self._pickle_file_name, "rb") as f:
                    cache = pickle.load(f)

            else:
                cache = self._api_call_multi(filter=filter)
                with open(self._pickle_file_name, "wb") as f:
                    pickle.dump(cache, f)

        # Call EZO API if not running in debug mode.
        else:
            cache = self._api_call_multi(filter=filter)

        print(f"Returned {len(cache)} results.")
        self.cache = {**self.cache, **cache}


class AssetCache(EzoCache):
    def __init__(self, debug=False, use_saved=False):
        super().__init__(debug, use_saved)
        self.cache: Dict[int, AssetV2] = {}
        self._pickle_file_name = "ezo_asset_cache.pkl"
        self._api_call_single = ezoff.get_asset_v2_pd
        self._api_call_multi = ezoff.get_assets_v2_pd
        self._data_model = AssetV2
        self._not_found_exception = AssetNotFound

    def asset(self, asset_id: int, force_api: bool = False):
        return self.get_cache_entry(entry_id=asset_id, force_api=force_api)

    @property
    def assets(self) -> AssetV2:
        return self.cache


class LocationCache(EzoCache):
    def __init__(self, debug=False, use_saved=False):
        super().__init__(debug, use_saved)
        self.cache: Dict[int, LocationV2] = {}
        self._pickle_file_name = "ezo_location_cache.pkl"
        self._api_call_single = ezoff.get_location_v2_pd
        self._api_call_multi = ezoff.get_loctions_v2_pd
        self._data_model = LocationV2
        self._not_found_exception = LocationNotFound

    def location(self, location_id: int, force_api: bool = False):
        return self.get_cache_entry(entry_id=location_id, force_api=force_api)

    @property
    def locations(self) -> Dict[int, LocationV2]:
        return self.cache


class MemberCache(EzoCache):
    def __init__(self, debug=False, use_saved=False):
        super().__init__(debug, use_saved)
        self.cache: Dict[int, MemberV2] = {}
        self._pickle_file_name = "ezo_member_cache.pkl"
        self._api_call_single = ezoff.get_member_v2_pd
        self._api_call_multi = ezoff.get_members_v2_pd
        self._data_model = MemberV2
        self._not_found_exception = MemberNotFound

    def member(self, member_id: int, force_api: bool = False):
        return self.get_cache_entry(entry_id=member_id, force_api=force_api)

    @property
    def members(self) -> Dict[int, MemberV2]:
        return self.cache


class WorkOrderCache(EzoCache):
    def __init__(self, debug=False, use_saved=False):
        super().__init__(debug, use_saved)
        self.cache: Dict[int, WorkOrderV2] = {}
        self._pickle_file_name = "ezo_workorder_cache.pkl"
        self._api_call_single = ezoff.get_work_order_v2_pd
        self._api_call_multi = ezoff.get_work_orders_v2_pd
        self._data_model = WorkOrderV2
        self._not_found_exception = WorkOrderNotFound

    def work_order(self, work_order_id: int, force_api: bool = False):
        return self.get_cache_entry(entry_id=work_order_id, force_api=force_api)

    @property
    def work_orders(self) -> Dict[int, WorkOrderV2]:
        return self.cache
