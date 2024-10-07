"""
Covers everything related to groups and subgroups in EZOfficeInventory
"""

import os
from typing import Optional

import requests

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page

ezo_headers = {
    "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@Decorators.check_env_vars
def get_groups() -> list[dict]:
    """
    Get all groups
    """

    url = os.environ["EZO_BASE_URL"] + "groups"

    page = 1

    all_groups = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers=ezo_headers,
                params={"page": page},
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get groups: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get groups: {e}")

        data = response.json()

        if "data" not in data:
            raise Exception(f"Error, could not get groups: {response.content}")

        all_groups.extend(data["data"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_groups


@_basic_retry
@Decorators.check_env_vars
def get_group(group_id: int):
    """
    Get a group
    NOTE: The results from this endpoint don't look correct.
    Returning assets that are in that group, rather than info about the group itself.

    :param group_id: The ID of the group to get
    """

    url = os.environ["EZO_BASE_URL"] + f"groups/{group_id}"

    try:
        response = requests.get(
            url,
            headers=ezo_headers,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error, could not get group: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not get group: {e}")

    if "group" not in response.json():
        raise Exception(f"Error, could not get group: {response.content}")

    return response.json()["data"]


@Decorators.check_env_vars
def get_subgroups(group_id: Optional[int]) -> list[dict]:
    """
    Get subgroups
    Optionally takes a group_id to get subgroups of a specific group
    """

    url = os.environ["EZO_BASE_URL"] + "groups/get_sub_groups.api"

    params = {}

    if group_id:
        params["group_id"] = group_id

    page = 1

    all_subgroups = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers=ezo_headers,
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get subgroups: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get subgroups: {e}")

        data = response.json()

        if "sub_groups" not in data:
            raise Exception(f"Error, could not get subgroups: {response.content}")

        all_subgroups.extend(data["sub_groups"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_subgroups
