"""
This module contains functions to interact with the locations v2 API in EZOfficeInventory.
"""

import json
import logging
import os
from typing import Optional

import requests

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import LocationV2, WorkOrderV2
from ezoff.exceptions import LocationNotFound, NoDataReturned

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def get_loctions_v2_pd(filter: Optional[dict]) -> dict[int, WorkOrderV2]:
    """
    Get locations.
    Returns dictionary of pydantic objects keyed by location sequence number.
    """
    locations_dict = get_loctions_v2(filter=filter)
    locations = {}

    for location in locations_dict:
        try:
            locations[location["id"]] = LocationV2(**location)

        except Exception as e:
            logger.error(
                f"Error in get_loctions_v2_pd() for location {location.get('id', 'unknown')}: {str(e)}"
            )
            raise

    return locations


@_basic_retry
@Decorators.check_env_vars
def get_loctions_v2(filter: Optional[dict]) -> list[dict]:
    """
    Get locations.
    The only filter option (state) listed in the API docs does not function and has been ommitted.
    EZO returns an HTTP 500 when the state filter is specified.
    """

    url = os.environ["EZO_BASE_URL"] + "api/v2/locations"
    all_locations = []
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }

    if filter:
        payload = json.dumps(filter)
    else:
        payload = None

    while True:
        try:
            response = _fetch_page(
                url,
                headers=headers,
                data=payload,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error in get_loctions_v2() for filter {filter}: {e.response.status_code} - {e.response.content}"
            )
            raise LocationNotFound(
                f"Error, could not get locations: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get locations: {e}")
            raise LocationNotFound(f"Error, could not get locations: {e}")

        data = response.json()

        if "locations" not in data:
            logger.error(f"No locations found: {response.content}")
            raise NoDataReturned(f"No locations found: {response.content}")

        all_locations = all_locations + data["locations"]

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

    return all_locations


@Decorators.check_env_vars
def get_location_v2_pd(location_id: int) -> LocationV2:
    """
    Get a single location.
    Returns a pydantic object.
    """
    location_dict = get_location_v2(location_id=location_id)
    return LocationV2(**location_dict["location"])


@_basic_retry
@Decorators.check_env_vars
def get_location_v2(location_id: int) -> dict:
    """
    Get a single location.
    """
    url = os.environ["EZO_BASE_URL"] + f"api/v2/locations/{location_id}"
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
            f"Error, could not get location details: {e.response.status_code} - {e.response.content}"
        )
        raise LocationNotFound(
            f"Error, could not get location details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get location details: {e}")
        raise LocationNotFound(f"Error, could not get location details: {e}")

    return response.json()
