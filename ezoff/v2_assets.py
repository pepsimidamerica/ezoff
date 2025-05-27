"""
This module contains functions to interact with the fixed asset v2 API in EZOfficeInventory.
"""

import json
import logging
import os
from typing import Optional

import requests

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import AssetV2
from ezoff.exceptions import (
    AssetDuplicateIdentificationNumber,
    AssetNotFound,
    LocationNotFound,
    NoDataReturned,
)

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def get_asset_v2_pma(identification_number: int) -> AssetV2 | None:
    """Get an EZ Office asset by its identification number.

    Args:
        pma_asset_id (int): _description_

    Returns:
        AssetV2: Pydantic EZ Office Asset Object.
    """
    filter = {"filters": {"identifier": identification_number}}
    asset_dict = get_assets_v2_pd(filter=filter)

    # There "should" always be at most 1 asset returned by the above API call.
    if len(asset_dict) > 1:
        logger.error(
            f"Multiple EZ Office assets assigned to identification number: {identification_number}"
        )
        raise AssetDuplicateIdentificationNumber(
            f"Multiple EZ Office assets assigned to identification number: {identification_number}"
        )

    for asset in asset_dict:
        try:
            return asset_dict[asset]

        except Exception as e:
            logger.error(
                f"Error in get_asset_v2_pma() for identification number {identification_number}: {str(e)}"
            )
            raise


@Decorators.check_env_vars
def get_assets_v2_pd(filter: Optional[dict]) -> dict[int, AssetV2]:
    """
    Get filtered fixed assets.
    Returns dictionary of pydantic objects keyed by asset id.
    """
    asset_dict = get_assets_v2(filter=filter)
    assets = {}

    for asset in asset_dict:
        try:
            assets[asset["id"]] = AssetV2(**asset)

        except Exception as e:
            logger.error(
                f"Error in get_assets_v2_pd() for asset {asset.get('id', 'unknown')}: {str(e)}"
            )
            raise

    return assets


@Decorators.check_env_vars
def get_assets_v2(filter: Optional[dict]) -> list[dict]:
    """
    Get filtered fixed assets.
    """
    url = os.environ["EZO_BASE_URL"] + "api/v2/assets"
    all_assets = []
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }

    while True:
        try:
            response = _fetch_page(
                url,
                headers=headers,
                data=json.dumps(filter),
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get fixed assets: {e.response.status_code} - {e.response.content}"
            )
            raise AssetNotFound(
                f"Error, could not get fixed assets: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get fixed assets: {str(e)}")
            raise AssetNotFound(f"Error, could not get fixed assets: {e}")

        data = response.json()

        if "assets" not in data:
            logger.error(f"No fixed assets found: {response.content}")
            raise NoDataReturned(f"No fixed assets found: {response.content}")

        all_assets = all_assets + data["assets"]

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

    return all_assets


@Decorators.check_env_vars
def get_asset_v2_pd(asset_id: int) -> AssetV2:
    """
    Get a single asset.
    Returns a pydantic object.
    """
    asset_dict = get_asset_v2(asset_id=asset_id)
    return AssetV2(**asset_dict["asset"])


@_basic_retry
@Decorators.check_env_vars
def get_asset_v2(asset_id: int) -> dict:
    """
    Get a single asset.
    """
    url = os.environ["EZO_BASE_URL"] + f"api/v2/assets/{asset_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get asset details: {e.response.status_code} - {e.response.content}"
        )
        raise LocationNotFound(
            f"Error, could not get asset details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get asset details: {e}")
        raise LocationNotFound(f"Error, could not get asset details: {e}")

    return response.json()


@Decorators.check_env_vars
def update_asset_v2(asset_id: int, payload: dict) -> dict:
    """
    Updates a fixed asset.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = f"{os.environ['EZO_BASE_URL']}api/v2/assets/{str(asset_id)}"

    try:
        response = requests.put(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not update asset: {e.response.status_code} - {e.response.content}"
        )
        raise AssetNotFound(
            f"Error, could not update asset: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not update asset: {e}")
        raise AssetNotFound(f"Error, could not update asset: {str(e)}")

    return response.json()
