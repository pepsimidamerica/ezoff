"""
Covers everything related to groups and subgroups in EZOfficeInventory
"""

import logging
import os
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _fetch_page
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

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups"

    params = {k: v for k, v in locals().items() if v is not None}

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


@Decorators.check_env_vars
def group_get(group_id: int):
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


@Decorators.check_env_vars
def group_update(group_id: int):
    """
    Updates a particular group.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={},  # TODO
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


@Decorators.check_env_vars
def group_delete():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def groups_get():
    """
    Returns all groups
    """
    pass


@Decorators.check_env_vars
def subgroup_get():
    """
    ()
    """
    pass


@Decorators.check_env_vars
def subgroups_get(group_id: int | None = None) -> list[dict]:
    """
    Get subgroups

    :param group_id: Optionally filter to get subgroups of a specific group
    """
    pass
