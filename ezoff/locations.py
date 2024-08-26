"""
This module contains functions for interacting with locations in EZOfficeInventory
"""

import os
import time
from typing import Optional

import requests

from ezoff.auth import Decorators


@Decorators.check_env_vars
def get_locations(filter: Optional[dict]) -> list[dict]:
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
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get locations from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get locations from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get locations from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()
        if "locations" not in data:
            print(
                f"Error, could not get locations from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get locations from EZOfficeInventory: "
                + str(response.content)
            )

        all_locations.extend(data["locations"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

        # Potentially running into rate limiting issues with this endpoint
        # Sleep for a second to avoid this
        time.sleep(1)

    return all_locations


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
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get location from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get location from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get location from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not get location from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


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
            timeout=10,
        )
    except Exception as e:
        print(
            "Error, could not get location item quantities from EZOfficeInventory: ", e
        )
        raise Exception(
            "Error, could not get location item quantities from EZOfficeInventory: "
            + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get location item quantities from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not get location item quantities from EZOfficeInventory: "
            + str(response.content)
        )

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
    except Exception as e:
        print("Error, could not create location in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create location in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not create location in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not create location in EZOfficeInventory: "
            + str(response.content)
        )

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
            timeout=10,
        )
    except Exception as e:
        print("Error, could not activate location in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not activate location in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not activate location in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not activate location in EZOfficeInventory: "
            + str(response.content)
        )

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
            timeout=10,
        )
    except Exception as e:
        print("Error, could not deactivate location in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not deactivate location in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not deactivate location in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not deactivate location in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


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
            timeout=10,
        )
    except Exception as e:
        print("Error, could not update location in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not update location in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not update location in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not update location in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()
