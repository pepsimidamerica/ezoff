"""
Covers everything related to inventory assets.
"""

import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Inventory

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def inventory_create(inv_asset_num: int, order: dict) -> Inventory | None:
    """
    Creates an inventory item
    """
    pass


@_basic_retry
@Decorators.check_env_vars
def inventory_return(inv_asset_num: int) -> Inventory | None:
    """
    Get details for an inventory item.
    """
    pass


@Decorators.check_env_vars
def inventories_return() -> list[Inventory]:
    """
    Returns all inventory items.
    """
    pass


@Decorators.check_env_vars
def inventory_add_stock(inventory_id: int):
    """
    Adds stock to inventory item.
    """
    pass


@Decorators.check_env_vars
def inventory_remove_stock(inventory_id: int):
    """
    Removes stock of inventory item.
    """
    pass


@Decorators.check_env_vars
def inventory_transfer_stock(inventory_id: int):
    """
    Transfers inventory item amount from one location to another.
    """
    pass


@Decorators.check_env_vars
def inventory_retire(inventory_id: int):
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_activate(inventory_id: int):
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_delete(inventory_id: int):
    """
    Deletes an inventory item.
    """
    pass


@Decorators.check_env_vars
def inventory_quantity_by_location_return():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_line_item_locations_return():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_custom_field_history_return():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_location_based_threshold_return():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_history_return(inventory_id: int) -> list[dict]:
    """
    Gets stock history of an inventory item.
    """
    pass


@Decorators.check_env_vars
def inventory_reservations_return():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_link_to_project():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def inventory_unlink_from_project():
    """
    ()
    """
    pass
