"""
This module contains functions to interact with the fixed asset v2 API in EZOfficeInventory.
"""

import os
from typing import Literal, Optional, List
from datetime import date, datetime
import requests
from pprint import pprint
import json
import pickle

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from .exceptions import *
from .data_model import *


@Decorators.check_env_vars
def get_asset_v2_pma(pma_asset_id: int) -> AssetV2:
    """Get an EZ Office asset by its identification number.

    Args:
        pma_asset_id (int): _description_

    Returns:
        AssetV2: Pydantic EZ Office Asset Object.
    """
    filter = {"filters": {"identifier": pma_asset_id}}
    asset_dict = get_assets_v2(filter=filter)

    # There "should" always be at most 1 asset returned by the above API call.
    for asset in asset_dict:
        try:
            return AssetV2(**asset)

        except Exception as e:
            print("Error in get_asset_v2_pma()")
            print(str(e))
            pprint(asset)
            exit(0)


@Decorators.check_env_vars
def get_assets_v2_pd(filter: Optional[dict]) -> Dict[int, WorkOrderV2]:
    """
    Get filtered fixed assets.
    Returns dictionary of pydantic objects keyed by asset id.
    """
    asset_dict = get_assets_v2(filter=filter)
    assets = {}

    # use_saved = True
    # Use saved pickle when running in debug mode.
    # if use_saved:
    #     print("Using saved fixed assets in get_assets_v2_pd().")
    #     with open("get_assets_v2.pkl", "rb") as f:
    #         asset_dict = pickle.load(f)
    # else:
    #     print("Getting assets in get_assets_v2_pd().")
    #     asset_dict = get_assets_v2(filter=filter)
    #     with open("get_assets_v2.pkl", "wb") as f:
    #         pickle.dump(asset_dict, f)

    for asset in asset_dict:
        try:
            assets[asset["id"]] = AssetV2(**asset)

        except Exception as e:
            print("Error in get_assets_v2_pd()")
            print(str(e))
            pprint(asset)
            exit(0)

    return assets


@_basic_retry
@Decorators.check_env_vars
def get_assets_v2(filter: Optional[dict]) -> List[dict]:
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
            raise AssetNotFound(
                f"Error, could not get fixed assets: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise AssetNotFound(f"Error, could not get fixed assets: {e}")

        data = response.json()

        if "assets" not in data:
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
