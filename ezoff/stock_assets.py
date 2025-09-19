import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import ResponseMessages, StockAsset

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def stock_asset_create(
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
    inventory_threshold: int | None = None,
    default_low_location_threshold: int | None = None,
    default_excess_location_threshold: int | None = None,
    initial_stock_quantity: int | None = None,
    line_item_attributes: list[dict] | None = None,
    location_thresholds_attributes: list[dict] | None = None,
    asset_detail_attributes: dict | None = None,
    custom_fields: list[dict] | None = None,
) -> StockAsset | None:
    """
    Creates a stock asset.
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"asset_stock": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating stock asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating stock asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating stock asset: {e}")
        raise Exception(f"Error creating stock asset: {e}")

    if response.status_code == 200 and "asset_stock" in response.json(0):
        return StockAsset(**response.json()["asset_stock"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def stock_asset_return(stock_asset_id: int) -> StockAsset | None:
    """
    Returns a particular stock asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/{stock_asset_id}"

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
            f"Error getting stock asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting stock asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting stock asset: {e}")
        raise Exception(f"Error getting stock asset: {e}")

    if response.status_code == 200 and "asset_stock":
        return StockAsset(**response.json()["asset_stock"])
    else:
        return None


@Decorators.check_env_vars
def stock_assets_return(filter: dict | None = None) -> list[StockAsset]:
    """
    Returns all stock assets. Optionally, filter using one or more fields.
    """

    if filter:
        for field in filter:
            if field not in StockAsset.model_fields:
                raise ValueError(f"'{field}' is not a valid field for an inventory.")
            filter = {"filters": filter}
    else:
        filter = None

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets"

    all_stock_assets = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                json=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get stock assets: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get stock assets: {e}")
            raise

        data = response.json()

        if "asset_stock" not in data:
            logger.error(f"Error, could not get stock assets: {response.content}")
            raise Exception(f"Error, could not get stock assets: {response.content}")

        all_stock_assets.extend(data["asset_stock"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [StockAsset(**x) for x in all_stock_assets]


@Decorators.check_env_vars
def stock_assets_search(search_term: str) -> list[StockAsset]:
    """
    Search for stock assets using some search term.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/search"

    all_stock_assets = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"search": search_term},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get stock assets: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get stock assets: {e}")
            raise

        data = response.json()

        if "asset_stock" not in data:
            logger.error(f"Error, could not get stock assets: {response.content}")
            raise Exception(f"Error, could not get stock assets: {response.content}")

        all_stock_assets.extend(data["asset_stock"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [StockAsset(**x) for x in all_stock_assets]


# TODO Quantity By Location
# TODO Line Item Locations
# TODO Current Checkouts
# TODO Custom Field History
# TODO Location Based Threshold
# TODO History
# TODO Reservations

# TODO Add stock
# TODO Transfer stock
# TODO checkout
# TODO checkin
# TODO update location
# TODO retire
# TODO activate
# TODO create reservation
# TODO Link to project
# TODO Unlink from project


@Decorators.check_env_vars
def stock_asset_delete(stock_asset_id: int) -> ResponseMessages | None:
    """
    Deletes a particular stock asset.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/{stock_asset_id}"

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
        logger.error(
            f"Error deleting stock asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error deleting stock asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting stock asset: {e}")
        raise Exception(f"Error deleting stock asset: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None
