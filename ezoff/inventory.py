"""
Covers everything related to inventory assets.
"""

import logging
import os
import time
from datetime import datetime

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import (
    CustomFieldHistoryItem,
    Inventory,
    Reservation,
    ResponseMessages,
    StockHistoryItem,
)

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def inventory_create(
    name: str,
    group_id: int,
    location_id: int,
    display_image: str | None = None,
    identifier: str | None = None,
    description: str | None = None,
    product_model_number: str | None = None,
    cost_price: float | None = None,
    vendor_id: int | None = None,
    salvage_value: float | None = None,
    sub_group_id: int | None = None,
    inventory_treshold: int | None = None,
    default_low_location_threshold: int | None = None,
    default_excess_location_threshold: int | None = None,
    initial_stock_quantity: int | None = None,
    line_item_atributes: list[dict] | None = None,
    location_thresholds_attributes: list[dict] | None = None,
    asset_detail_attributes: dict | None = None,
    custom_fields: list[dict] | None = None,
) -> Inventory | None:
    """
    Creates an inventory item
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = (
        f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory"
    )

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating inventory: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating inventory: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating inventory: {e}")
        raise Exception(f"Error creating inventory: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def inventory_return(inventory_id: int) -> Inventory | None:
    """
    Get details for an inventory item.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting inventory: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting inventory: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting inventory: {e}")
        raise Exception(f"Error getting inventory: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventories_return(filter: dict | None = None) -> list[Inventory]:
    """
    Returns all inventory items. Optionally filter by some field.
    """

    if filter:
        for field in filter:
            if field not in Inventory.model_fields:
                raise ValueError(f"'{field}' is not a valid field for an inventory.")
            filter = {"filters": filter}
    else:
        filter = None

    url = (
        f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory"
    )

    all_inventories = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                json=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get inventories: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get inventories: {e}")
            raise

        data = response.json()

        if "inventories" not in data:
            logger.error(f"Error, could not get inventories: {response.content}")
            raise Exception(f"Error, could not get inventories: {response.content}")

        all_inventories.extend(data["inventories"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Inventory(**x) for x in all_inventories]


@Decorators.check_env_vars
def inventories_search(search_term: str) -> list[Inventory]:
    """
    Searches for inventory items.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/search"

    all_inventories = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"search": search_term},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get inventories: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get inventories: {e}")
            raise

        data = response.json()

        if "inventories" not in data:
            logger.error(f"Error, could not get inventories: {response.content}")
            raise Exception(f"Error, could not get inventories: {response.content}")

        all_inventories.extend(data["inventories"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Inventory(**x) for x in all_inventories]


@Decorators.check_env_vars
def inventory_add_stock(
    inventory_id: int,
    location_id: int,
    quantity: int,
    total_price: float,
    purchased_on: datetime | None = None,
    order_by_id: int | None = None,
    vendor_id: int | None = None,
    comments: str | None = None,
    custom_fields: list[dict] | None = None,
) -> Inventory | None:
    """
    Adds stock to inventory item.
    """

    params = {k: v for k, v in locals().items() if v is not None}
    params.pop("inventory_id", None)

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/add_stock"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error adding stock: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error adding stock: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding stock: {e}")
        raise Exception(f"Error adding stock: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_remove_stock(
    inventory_id: int,
    location_id: int,
    to_location_id: int,
    quantity: int,
    total_price: float,
    purchased_on: datetime | None = None,
    order_by_id: int | None = None,
    vendor_id: int | None = None,
    comments: str | None = None,
    ignore_conflicting_reservations: bool | None = None,
    custom_fields: list[dict] | None = None,
) -> Inventory | None:
    """
    Removes stock of inventory item.
    """

    params = {k: v for k, v in locals().items() if v is not None}
    params.pop("inventory_id", None)

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/remove_stock"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error removing stock: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error removing stock: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error removing stock: {e}")
        raise Exception(f"Error removing stock: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_update_location(inventory_id: int, location_id: int) -> Inventory | None:
    """
    Updates location of inventory item.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/update_location"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": {"location_id": location_id}},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating location: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating location: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating location: {e}")
        raise Exception(f"Error updating location: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_transfer_stock(
    inventory_id: int,
    from_location_id: int,
    to_location_id: int,
    quantity: int,
    total_price: float,
    comments: str | None = None,
    custom_fields: list[dict] | None = None,
):
    """
    Transfers inventory item amount from one location to another.
    """

    params = {k: v for k, v in locals().items() if v is not None}
    params.pop("inventory_id", None)

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/transfer_stock"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error transferring stock: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error transferring stock: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error transferring stock: {e}")
        raise Exception(f"Error transferring stock: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_retire(
    inventory_id: int,
    retire_reason_id: int,
    salvage_value: float | None = None,
    retire_comments: str | None = None,
    location_id: int | None = None,
):
    """
    Retires an inventory item.
    """

    params = {k: v for k, v in locals().items() if v is not None}
    params.pop("inventory_id", None)

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/retire"

    try:
        response = requests.put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"inventory": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error retiring: {e.response.status_code} - {e.response.content}")
        raise Exception(
            f"Error retiring: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retiring: {e}")
        raise Exception(f"Error retiring: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_activate(inventory_id: int):
    """
    Activates an inventory item.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/activate"

    try:
        response = requests.put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error activating: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error activating: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error activating: {e}")
        raise Exception(f"Error activating: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_delete(inventory_id: int):
    """
    Deletes an inventory item.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}"

    try:
        response = requests.delete(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error deleting: {e.response.status_code} - {e.response.content}")
        raise Exception(
            f"Error deleting: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting: {e}")
        raise Exception(f"Error deleting: {e}")

    if response.status_code == 200 and "inventory" in response.json():
        return Inventory(**response.json()["inventory"])
    else:
        return None


@Decorators.check_env_vars
def inventory_quantity_by_location_return(
    inventory_id: int, location_id: int
) -> int | None:
    """
    Gets the current quantity of an inventory item in a particular location.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/get_quantity_by_location"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            params={"location_id": location_id},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting quantity: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting quantity: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting quantity: {e}")
        raise Exception(f"Error quantity: {e}")

    if response.status_code != 200 or "quantity" not in response.json():
        return None

    return response.json()["quantity"]


# @Decorators.check_env_vars
# def inventory_line_item_locations_return(inventory_id: int):
#     """
#     TODO Doesn't seem to return useful info when testing this endpoint.
#     Just returns a listing of all locations, not anything specific to the
#     particular item.
#     """
#     pass


@Decorators.check_env_vars
def inventory_custom_field_history_return(
    inventory_id: int, custom_field_id: int
) -> list[CustomFieldHistoryItem]:
    """
    Returns custom attribute history for a particulary inventory.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/custom_field_history/{custom_field_id}"

    all_custom_history = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get custom attribute history: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get custom attribute history: {e}")
            raise

        data = response.json()

        if "custom_field" not in data:
            logger.error(
                f"Error, could not get custom attribute history: {response.content}"
            )
            raise Exception(
                f"Error, could not get custom attribute history: {response.content}"
            )

        all_custom_history.extend(data["custom_field"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [CustomFieldHistoryItem(**x) for x in all_custom_history]


# @Decorators.check_env_vars
# def inventory_location_based_threshold_return():
#     """
#     TODO Doesn't seem to exist. Just getting a 404 when testing in Postman
#     """
#     pass


@Decorators.check_env_vars
def inventory_history_return(inventory_id: int) -> list[StockHistoryItem]:
    """
    Gets stock history of an inventory item.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/history"

    all_stock_history = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get stock history: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get stock history: {e}")
            raise

        data = response.json()

        if "stock_history" not in data:
            logger.error(f"Error, could not get stock history: {response.content}")
            raise Exception(f"Error, could not get stock history: {response.content}")

        all_stock_history.extend(data["stock_history"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [StockHistoryItem(**x) for x in all_stock_history]


@Decorators.check_env_vars
def inventory_reservations_return(inventory_id: int) -> list[Reservation]:
    """
    Returns all reservations on an inventory item.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/{inventory_id}/reservations"

    all_reservations = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get reservations: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get reservations: {e}")
            raise

        data = response.json()

        if "reservations" not in data:
            logger.error(f"Error, could not get reservations: {response.content}")
            raise Exception(f"Error, could not get reservations: {response.content}")

        all_reservations.extend(data["reservations"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Reservation(**x) for x in all_reservations]


@Decorators.check_env_vars
def inventory_link_to_project(
    project_id: int, inventory_ids: list[int]
) -> ResponseMessages | None:
    """
    Links one or more inventory items to a project.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/link_to_project"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            params={"project_id": project_id, "ids": inventory_ids},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error linking to project: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error linking to project: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error linking to project: {e}")
        raise Exception(f"Error linking to project: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def inventory_unlink_from_project(project_id: int, inventory_ids: list[int]):
    """
    Unlink one or more inventory items from a project.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/inventory/unlink_from_project"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            params={"project_id": project_id, "ids": inventory_ids},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error unlinking from project: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error unlinking from project: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error unlinking from project: {e}")
        raise Exception(f"Error unlinking from project: {e}")

    if response.status_code == 200 and "messages" in response.json(0):
        return ResponseMessages(**response.json()["messages"])
    else:
        return None
