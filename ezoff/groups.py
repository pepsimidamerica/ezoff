"""
Covers everything related to groups and subgroups in EZOfficeInventory
"""

import logging
import os
from typing import Optional

import requests

from ezoff._auth import Decorators
from ezoff._helpers import _fetch_page

logger = logging.getLogger(__name__)


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
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get subgroups: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get subgroups: {e}")
            raise

        data = response.json()

        if "sub_groups" not in data:
            logger.error(f"Error, could not get subgroups: {response.content}")
            raise Exception(f"Error, could not get subgroups: {response.content}")

        all_subgroups.extend(data["sub_groups"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_subgroups
