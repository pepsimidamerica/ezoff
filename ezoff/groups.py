"""
Covers everything related to groups and subgroups in EZOfficeInventory
"""

import logging
import os
import time
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import DepreciationRate, Group, ResponseMessages

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def group_create(
    name: str,
    description: str | None = None,
    asset_depreciation_mode: Literal["Useful Life", "Percentage"] | None = None,
    triage_completion_period: int | None = None,
    triage_completion_period_basis: Literal[
        "minutes", "hours", "days", "weeks", "months", "indefinite"
    ]
    | None = None,
    allow_staff_to_set_checkout_duration: bool | None = None,
    staff_checkout_duration_months: int | None = None,
    staff_checkout_duration_weeks: int | None = None,
    staff_checkout_duration_days: int | None = None,
    staff_checkout_duration_hours: int | None = None,
    depreciation_rates: list[DepreciationRate] | None = None,
) -> Group | None:
    """
    Creates a group.
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"group": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating group: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating group: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating group: {e}")
        raise Exception(f"Error creating group: {e}")

    if response.status_code == 200:
        return Group(**response.json()["group"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def group_return(group_id: int) -> Group | None:
    """
    Returns a particular group.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}"

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
            f"Error getting group: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting group: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting group: {e}")
        raise Exception(f"Error getting group: {e}")

    if response.status_code == 200:
        return Group(**response.json()["group"])
    else:
        return None


@Decorators.check_env_vars
def groups_return() -> list[Group]:
    """
    Returns all groups
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups"

    all_groups = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get groups: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get groups: {e}")
            raise

        data = response.json()

        if "groups" not in data:
            logger.error(f"Error, could not get groups: {response.content}")
            raise Exception(f"Error, could not get groups: {response.content}")

        all_groups.extend(data["groups"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Group(**x) for x in all_groups]


@Decorators.check_env_vars
def group_update(group_id: int, update_data: dict) -> Group | None:
    """
    Updates a particular group.
    """

    for field in update_data:
        if field not in Group.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data=update_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating group: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating group: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating group: {e}")
        raise Exception(f"Error updating group: {e}")

    if response.status_code == 200:
        return Group(**response.json()["group"])
    else:
        return None


@Decorators.check_env_vars
def group_delete(group_id: int) -> ResponseMessages | None:
    """
    Deletes a particular group.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}"

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
            f"Error creating group: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating group: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating group: {e}")
        raise Exception(f"Error creating group: {e}")

    if response.status_code == 200:
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def subgroup_create(
    parent_id: int,
    name: str,
    description: str | None = None,
    asset_depreciation_mode: Literal["Useful Life", "Percentage"] | None = None,
    triage_completion_period: int | None = None,
    triage_completion_period_basis: Literal[
        "minutes", "hours", "days", "weeks", "months", "indefinite"
    ]
    | None = None,
    allow_staff_to_set_checkout_duration: bool | None = None,
    staff_checkout_duration_months: int | None = None,
    staff_checkout_duration_weeks: int | None = None,
    staff_checkout_duration_days: int | None = None,
    staff_checkout_duration_hours: int | None = None,
    depreciation_rates: list[DepreciationRate] | None = None,
) -> Group | None:
    """
    Creates a subgroup.
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{parent_id}/sub_groups"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data=params,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating subgroup: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating subgroup: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating subgroup: {e}")
        raise Exception(f"Error creating subgroup: {e}")

    if response.status_code == 200:
        return Group(**response.json()["sub_group"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def subgroup_return(group_id: int, subgroup_id: int) -> Group | None:
    """
    Returns a particular subgroup.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}"

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
            f"Error getting subgroup: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting subgroup: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting subgroup: {e}")
        raise Exception(f"Error getting subgroup: {e}")

    if response.status_code == 200:
        return Group(**response.json()["sub_group"])
    else:
        return None


@Decorators.check_env_vars
def subgroups_return(group_id: int) -> list[Group]:
    """
    Get all subgroups under a particular group.

    :param group_id: Filter to get subgroups of a specific group
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}"

    all_subgroups = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get subgroups: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get subgroups: {e}")
            raise

        data = response.json()

        if "groups" not in data:
            logger.error(f"Error, could not get subgroups: {response.content}")
            raise Exception(f"Error, could not get subgroups: {response.content}")

        all_subgroups.extend(data["sub_groups"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Group(**x) for x in all_subgroups]


@Decorators.check_env_vars
def subgroup_update(group_id: int, subgroup_id: int, update_data: dict) -> Group | None:
    """
    Updates a particular subgroup.
    """
    for field in update_data:
        if field not in Group.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data=update_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating subgroup: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating subgroup: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating subgroup: {e}")
        raise Exception(f"Error updating subgroup: {e}")

    if response.status_code == 200:
        return Group(**response.json()["sub_group"])
    else:
        return None


@Decorators.check_env_vars
def subgroup_delete(group_id: int, subgroup_id: int) -> ResponseMessages | None:
    """
    Deletes a particular subgroup.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}"

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
            f"Error deleting subgroup: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error deleting subgroup: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting subgroup: {e}")
        raise Exception(f"Error deleting subgroup: {e}")

    if response.status_code == 200:
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


# TODO Add group depreciation rates
