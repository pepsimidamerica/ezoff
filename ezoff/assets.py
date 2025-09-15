"""
Covers everything related to fixed assets in EZOffice
"""

import json
import logging
import os
import time
from datetime import date, datetime

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Asset, AssetHistoryItem, ResponseMessages, TokenInput
from ezoff.exceptions import (
    AssetNotFound,
    NoDataReturned,
)

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def asset_create(
    name: str,
    group_id: int,
    location_id: int,
    sub_group_id: int | None,
    purchased_on: datetime | None,
    display_image: str | None,
    identifier: str | None,
    description: str | None,
    vendor_id: int | None,
    product_model_number: str | None,
    cost_price: float | None,
    salvage_value: float | None,
    arbitration: int | None,
    custom_fields: list[dict] | None,
) -> Asset | None:
    """
    Creates an asset
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"asset": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating asset: {e}")
        raise Exception(f"Error creating asset: {e}")

    if response.status_code == 200 and "asset" in response.json():
        return Asset(**response.json()["asset"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def asset_return(asset_id: int) -> Asset | None:
    """
    Returns a particular asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}"

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
            f"Error getting asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting asset: {e}")
        raise Exception(f"Error getting asset: {e}")

    if response.status_code == 200 and "asset" in response.json():
        return Asset(**response.json()["asset"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def assets_return(filter: dict | None = None) -> list[Asset]:
    """
    Get assets. Optionally filter by one or more asset fields.
    """

    if filter:
        for field in filter:
            if field not in Asset.model_fields:
                raise ValueError(f"'{field}' is not a valid field for an asset.")
            filter = {"filters": filter}
    else:
        filter = None

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets"

    all_assets = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={
                    "Accept": "application/json",
                    "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                    "Cache-Control": "no-cache",
                    "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                },
                data=filter,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise AssetNotFound(
                f"Error, could not get fixed assets: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            raise AssetNotFound(f"Error, could not get fixed assets: {e}")

        data = response.json()

        if "assets" not in data:
            raise NoDataReturned(f"No fixed assets found: {response.content}")

        all_assets.extend(data["assets"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

    return [Asset(**x) for x in all_assets]


@Decorators.check_env_vars
def assets_search(search_term: str) -> list[Asset]:
    """
    Search for assets.
    The equivalent of the search bar in the EZO UI.
    May not return all assets that match the search term. Better to use the
    assets_return function with filters if you know what you're looking for.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/search"

    all_assets = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"search": search_term},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get assets: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get assets: {e}")
            raise

        data = response.json()

        if "assets" not in data:
            logger.error(f"Error, could not get assets: {response.content}")
            raise Exception(f"Error, could not get assets: {response.content}")

        all_assets.extend(data["assets"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Asset(**x) for x in all_assets]


@_basic_retry
@Decorators.check_env_vars
def assets_token_input_return(q: str) -> list[TokenInput]:
    """
    This isn't an official endpoint in the EZO API. It's used to populate
    the token input dropdowns in the EZO UI. However, still works if called
    and is needed if wanting to use the work_orders_return item filter. Which doesn't yet
    support the asset ID as a filter. But does support the ID that comes from this endpoint.
    Found this via the network tab in the browser. Not sure what the official name is
    so I'm just going off of what the URL is.

    Note: If you use "#{Asset Sequence Num}" as the q search parameter, it should
    only return one result. If you use a more general search term. like searching
    for the name, you may get multiple.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/assets/items_for_token_input.json"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"include_id": "true", "q": q},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get item token: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting item token: {e}")
        raise

    data = response.json()

    return [TokenInput(**x) for x in data]


@Decorators.check_env_vars
def asset_history_return(asset_id: int) -> list[AssetHistoryItem]:
    """
    Returns checkout history for a particular asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}/history"

    all_history = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get history: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get history: {e}")
            raise

        data = response.json()

        if "history" not in data:
            logger.error(f"Error, could not get history: {response.content}")
            raise Exception(f"Error, could not get history: {response.content}")

        all_history.extend(data["history"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [AssetHistoryItem(**x) for x in all_history]


@Decorators.check_env_vars
def asset_update(asset_id: int, update_data: dict) -> Asset | None:
    """
    Updates a fixed asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}"

    try:
        response = requests.patch(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            data=update_data,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating asset: {e}")
        raise Exception(f"Error updating asset: {e}")

    if response.status_code == 200 and "asset" in response.json():
        return Asset(**response.json()["asset"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def asset_checkin(
    asset_id: int,
    location_id: int,
    comments: str | None,
    checkin_date: date | None = None,
    custom_fields: list[dict] | None = None,
) -> ResponseMessages | None:
    """
    Check in an asset to a particular location.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}/checkin"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "asset": {
                    "comments": comments,
                    "location_id": location_id,
                    "checkin_date": checkin_date,
                    "custom_fields": custom_fields,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking in asset: {e}")
        raise Exception(f"Error checking in asset: {e}")

    if response.status_code == 200:
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def asset_checkout(
    asset_id: int,
    user_id: int,
    location_id: int,
    request_verification: bool,
    comments: str | None = None,
    checkout_forever: bool | None = None,
    till: datetime | None = None,
    project_id: int | None = None,
    ignore_conflicting_reservations: bool | None = None,
    fulfill_user_conflicting_reservations: bool | None = None,
    custom_fields: list[dict] | None = None,
) -> ResponseMessages | None:
    """
    Check out an asset to a member

    Note: If user is inactive, checkout will return a 200 status code but the
    asset will not be checked out. Response will contain a message.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}/checkout"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "asset": {
                    "user_id": user_id,
                    "comments": comments,
                    "location_id": location_id,
                    "request_verification": request_verification,
                    "checkout_forever": checkout_forever,
                    "till": till,
                    "ignore_conflicting_reservations": ignore_conflicting_reservations,
                    "fulfill_user_conflicting_reservations": fulfill_user_conflicting_reservations,
                    "custom_fields": custom_fields,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error checking out asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error checking out asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking out asset: {e}")
        raise Exception(f"Error checking out asset: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def asset_retire(
    asset_id: int,
    retired_on: datetime,
    retire_reason_id: int,
    salvage_value: float | None = None,
    retire_comments: str | None = None,
    location_id: int | None = None,
) -> Asset | None:
    """
    Retires an asset. Asset needs to be in an available state to retire.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}/retire"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "asset": {
                    "retired_on": retired_on,
                    "retire_reason_id": retire_reason_id,
                    "salvage_value": salvage_value,
                    "retire_comments": retire_comments,
                    "location_id": location_id,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error retiring asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error retiring asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retiring asset: {e}")
        raise Exception(f"Error retiring asset: {e}")

    if response.status_code == 200 and "asset" in response.json():
        return Asset(**response.json()["asset"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def asset_activate(asset_id: int, location_id: int | None = None) -> Asset | None:
    """
    Reactivates a retired asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}/activate"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"asset": {"location_id": location_id}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error activating asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error activating asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error activating asset: {e}")
        raise Exception(f"Error activating asset: {e}")

    if response.status_code == 200 and "asset" in response.json():
        return Asset(**response.json()["asset"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def verification_request(asset_id: int) -> dict:
    """
    Creates a verification request for a single asset.
    https://ezo.io/ezofficeinventory/developers/#api-verification

    Args:
        asset_id (int): The asset ID to verify.

    Raises:
        AssetNotFound: Asset ID was not found in EZ-Office.
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "assets/"
        + str(asset_id)
        + "/verification_requests.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()

    except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error(f"Error, could not create verification request: {e}")
        raise AssetNotFound(asset_id=str(asset_id))

    return response.json()


@_basic_retry
@Decorators.check_env_vars
def asset_delete(asset_id: int) -> ResponseMessages | None:
    """
    Delete a particular asset.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/assets/{asset_id}"

    try:
        response = requests.delete(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error deleting asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error deleting asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting asset: {e}")
        raise Exception(f"Error deleting asset: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


# TODO Add bulk operations

# TODO Add reservation-related operations
