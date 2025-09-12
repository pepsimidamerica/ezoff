"""
This module contains functions for interacting with locations in EZOfficeInventory
"""

import logging
import os
import time
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Location

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def location_create(location: dict) -> dict:
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


@_basic_retry
@Decorators.check_env_vars
def location_return(location_id: int) -> Location | None:
    """
    Returns a particular location.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/locations/{location_id}"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting location: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting location: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting location: {e}")
        raise Exception(f"Error getting location: {e}")

    if response.status_code == 200 and "location" in response.json():
        return Location(**response.json()["location"])
    else:
        return None


@Decorators.check_env_vars
def locations_return(
    state: Literal["all", "active", "inactive"] | None = None,
) -> list[Location]:
    """
    Returns all locations. Optionally filter by state.
    """
    if state is not None:
        filter_data = {"filters": {"state": state}}
    else:
        filter_data = None

    url = (
        f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/locations"
    )

    all_locations = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter_data,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error getting locations: {e.response.status_code} - {e.response.content}"
            )
            raise Exception(
                f"Error getting locations: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting locations: {e}")
            raise Exception(f"Error getting locations: {e}")

        data = response.json()

        if "locations" not in data:
            logger.error(f"Error, could not get locations: {data}")
            raise Exception(f"Error, could not get locations: {response.content}")

        all_locations.extend(data["locations"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        # Potentially running into rate limiting issues with this endpoint
        # Sleep for a second to avoid this
        time.sleep(1)

    return [Location(**x) for x in all_locations]


@Decorators.check_env_vars
def location_activate(
    location_id: int, activate_children: bool | None = None
) -> Location | None:
    """
    Activates a particular location. Optionally, also activate all children locations.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/locations/{location_id}/activate"

    if activate_children:
        data = {"location": {"activate_all_children_locations": True}}
    else:
        data = None

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
            data=data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error activating location: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error activating location: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error activating location: {e}")
        raise Exception(f"Error activating location: {e}")

    if response.status_code == 200 and "location" in response.json():
        return Location(**response.json()["location"])
    else:
        return None


@Decorators.check_env_vars
def location_deactivate(location_id: int) -> Location | None:
    """
    Deactivates a particular location.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/locations/{location_id}/deactivate"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error deactivating location: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error deactivating location: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deactivating location: {e}")
        raise Exception(f"Error deactivating location: {e}")

    if response.status_code == 200 and "location" in response.json():
        return Location(**response.json()["location"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def location_update(location_id: int, update_data: dict) -> Location | None:
    """
    Updates a particular location.
    """

    for field in update_data:
        if field not in Location.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a location.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/locations/{location_id}"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"location": update_data},
            timeout=60,
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

    if response.status_code == 200 and "location" in response.json():
        return Location(**response.json()["location"])
    else:
        return None
