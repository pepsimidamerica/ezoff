"""
This module contains functions for interacting with locations in EZOfficeInventory
"""

import json
import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Location
from ezoff.exceptions import LocationNotFound, NoDataReturned

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def get_locations(filter: dict | None = None) -> list[dict]:
    """
    Get locations
    Optionally filter by status
    https://ezo.io/ezofficeinventory/developers/#api-retreive-locations
    """
    if filter is not None:
        if "status" not in filter:
            raise ValueError("filter must have 'status' key")
        if filter["status"] not in ["all", "active", "inactive"]:
            raise ValueError(
                "filter['status'] must be one of 'all', 'active', 'inactive'"
            )

    url = os.environ["EZO_BASE_URL"] + "locations/get_line_item_locations.api"

    page = 1
    all_locations = []

    while True:
        params = {"page": page, "include_custom_fields": "true"}
        if filter is not None:
            params.update(filter)

        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get locations: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get locations: {e}")
            raise

        data = response.json()

        if "locations" not in data:
            logger.error(f"Error, could not get locations: {data}")
            raise Exception(f"Error, could not get locations: {response.content}")

        all_locations.extend(data["locations"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

        # Potentially running into rate limiting issues with this endpoint
        # Sleep for a second to avoid this
        time.sleep(1)

    return all_locations


@_basic_retry
@Decorators.check_env_vars
def get_location_details(location_num: int) -> dict:
    """
    Get location details
    https://ezo.io/ezofficeinventory/developers/#api-location-details
    """

    url = os.environ["EZO_BASE_URL"] + "locations/" + str(location_num) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"include_custom_fields": "true"},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get location: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get location: {e}")
        raise

    return response.json()


@_basic_retry
@Decorators.check_env_vars
def get_location_item_quantities(location_num: int) -> dict:
    """
    Get quantities of each item at a location
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "locations/"
        + str(location_num)
        + "/quantities_by_asset_ids.api"
    )

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get location item quantities: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get location item quantities: {e}")
        raise

    return response.json()


@Decorators.check_env_vars
def create_location(location: dict) -> dict:
    """
    Create a location
    https://ezo.io/ezofficeinventory/developers/#api-create-location
    """

    # Required fields
    if "location[name]" not in location:
        raise ValueError("location must have 'location[name]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "location[parent_id]",
        "location[identification_number]",
        "location[name]",
        "location[city]",
        "location[state]",
        "location[zipcode]",
        "location[street1]",
        "location[street2]",
        "location[status]",
        "location[description]",
    ]

    location = {
        k: v
        for k, v in location.items()
        if k in valid_keys or k.startswith("location[custom_attributes]")
    }

    if "location[status]" in location:
        if location["location[status]"] not in ["active", "inactive"]:
            raise ValueError(
                "location['location[status]'] must be one of 'active', 'inactive'"
            )

    url = os.environ["EZO_BASE_URL"] + "locations.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=location,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not create location: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not create location: {e}")
        raise

    return response.json()


@Decorators.check_env_vars
def activate_location(location_num: int) -> dict:
    """
    Activate a location
    https://ezo.io/ezofficeinventory/developers/#api-activate-location
    """

    url = (
        os.environ["EZO_BASE_URL"] + "locations/" + str(location_num) + "/activate.api"
    )

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not activate location: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not activate location: {e}")
        raise

    return response.json()


@Decorators.check_env_vars
def deactivate_location(location_num: int) -> dict:
    """
    Deactivate a location
    https://ezo.io/ezofficeinventory/developers/#api-deactivate-location
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "locations/"
        + str(location_num)
        + "/deactivate.api"
    )

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not deactivate location: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not deactivate location: {e}")
        raise

    return response.json()


@_basic_retry
@Decorators.check_env_vars
def update_location(location_num: int, location: dict) -> dict:
    """
    Updates a location.
    Note: The location's parent ID (location[parent_id]) is a required field for this call,
    because EZOffice will wipe out whatever is currently in that field
    if you don't include it. No idea why. If you're not changing the parent
    location of the location, you just use the current parent ID. The documentation
    also suggests that location[name] is a required field, but that doesn't appear
    to be the case. Not sure if documentation is wrong or I'm misunderstanding what
    they're saying.
    https://ezo.io/ezofficeinventory/developers/#api-update-location
    """

    if "location[parent_id]" not in location:
        raise ValueError("'location[parent_id]' is a required key")

    # Remove any keys that are not valid
    valid_keys = [
        "location[parent_id]",
        "location[name]",
        "location[city]",
        "location[state]",
        "location[zipcode]",
        "location[street1]",
        "location[street2]",
        "location[status]",
        "location[description]",
    ]

    location = {
        k: v
        for k, v in location.items()
        if k in valid_keys or k.startswith("location[custom_attributes]")
    }

    url = os.environ["EZO_BASE_URL"] + "locations/" + str(location_num) + ".api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=location,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not update location: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not update location: {e}")
        raise

    return response.json()


@Decorators.check_env_vars
def get_loctions_v2_pd(filter: dict | None = None) -> dict[int, Location]:
    """
    Get locations.
    Returns dictionary of pydantic objects keyed by location sequence number.
    """
    locations_dict = get_loctions_v2(filter=filter)
    locations = {}

    for location in locations_dict:
        try:
            locations[location["id"]] = Location(**location)

        except Exception as e:
            print("Error in get_loctions_v2_pd()")
            print(str(e))

    return locations


@_basic_retry
@Decorators.check_env_vars
def get_loctions_v2(filter: dict | None = None) -> list[dict]:
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
            raise LocationNotFound(
                f"Error, could not get locations: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise LocationNotFound(f"Error, could not get locations: {e}")

        data = response.json()

        if "locations" not in data:
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
def get_location_v2_pd(location_id: int) -> Location:
    """
    Get a single location.
    Returns a pydantic object.
    """
    location_dict = get_location_v2(location_id=location_id)
    return Location(**location_dict["location"])


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
        raise LocationNotFound(
            f"Error, could not get location details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise LocationNotFound(f"Error, could not get location details: {e}")

    return response.json()
