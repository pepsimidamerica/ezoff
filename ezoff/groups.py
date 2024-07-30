"""
Covers everything related to groups and subgroups in EZOfficeInventory
"""

import os
from typing import Optional

import requests

from ezoff.auth import Decorators


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
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get subgroups from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get subgroups from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get subgroups from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "sub_groups" not in data:
            print(
                f"Error, could not get subgroups from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get subgroups from EZOfficeInventory: "
                + str(response.content)
            )

        all_subgroups.extend(data["sub_groups"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_subgroups
