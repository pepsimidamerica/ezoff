"""
This module contains functions for interacting with members/roles/user setup in EZOfficeInventory
"""

import os
import time
from typing import Optional

import requests

from ezoff.auth import Decorators


@Decorators.check_env_vars
def get_members(filter: Optional[dict]) -> list[dict]:
    """
    Get members from EZOfficeInventory
    Optionally filter by email, employee_identification_number, or status
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-members
    """

    if filter is not None:
        if "filter" not in filter or "filter_val" not in filter:
            raise ValueError("filter must have 'filter' and 'filter_val' keys")
        if filter["filter"] not in [
            "email",
            "employee_identification_number",
            "status",
        ]:
            raise ValueError(
                "filter['filter'] must be one of 'email', 'employee_identification_number', 'status'"
            )

    url = os.environ["EZO_BASE_URL"] + "members.api"

    page = 1
    all_members = []

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
            print("Error, could not get members from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get members from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get members from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()
        if "members" not in data:
            print(
                f"Error, could not get members from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get members from EZOfficeInventory: "
                + str(response.content)
            )

        all_members.extend(data["members"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

        # Potentially running into rate limiting issues with this endpoint
        # Sleep for a second to avoid this
        time.sleep(1)

    return all_members


@Decorators.check_env_vars
def get_member_details(member_id: int) -> dict:
    """
    Get member from EZOfficeInventory by member_id
    https://ezo.io/ezofficeinventory/developers/#api-member-details
    """

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"include_custom_fields": "true"},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get member from EZOfficeInventory: ", e)
        raise Exception("Error, could not get member from EZOfficeInventory: " + str(e))

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get member from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not get member from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def create_member(member: dict) -> dict:
    """
    Create a new member
    https://ezo.io/ezofficeinventory/developers/#api-create-member
    """

    # Required fields
    if "user[email]" not in member:
        raise ValueError("member must have 'user[email]' key")
    if "user[first_name]" not in member:
        raise ValueError("member must have 'user[first_name]' key")
    if "user[last_name]" not in member:
        raise ValueError("member must have 'user[last_name]' key")
    if "user[role_id]" not in member:
        raise ValueError("member must have 'user[role_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "user[email]",
        "user[employee_id]",
        "user[employee_identification_number]",
        "user[role_id]",
        "user[team_id]",
        "user[user_listing_id]",
        "user[first_name]",
        "user[last_name]",
        "user[address_name]",
        "user[address]",
        "user[address_line_2]",
        "user[city]",
        "user[state]",
        "user[country]",
        "user[phone_number]",
        "user[fax]",
        "user[login_enabled]",
        "user[subscribed_to_emails]",
        "skip_confirmation_email",
    ]

    # Check for custom attributes
    member = {
        k: v
        for k, v in member.items()
        if k in valid_keys or k.startswith("user[custom_attributes]")
    }

    url = os.environ["EZO_BASE_URL"] + "members.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=member,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not create member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create member in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not create member in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not create member in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def update_member(member_id: int, member: dict) -> dict:
    """
    Update a member
    https://ezo.io/ezofficeinventory/developers/#api-update-member
    """

    # Remove any keys that are not valid
    valid_keys = [
        "user[email]",
        "user[employee_id]",
        "user[role_id]",
        "user[team_id]",
        "user[user_listing_id]",
        "user[first_name]",
        "user[last_name]",
        "user[phone_number]",
        "user[fax]",
        "skip_confirmation_email",
    ]

    # Check for custom attributes
    member = {
        k: v
        for k, v in member.items()
        if k in valid_keys or k.startswith("user[custom_attributes]")
    }

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + ".api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=member,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not update member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not update member in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not update member in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not update member in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def deactivate_member(member_id: int) -> dict:
    """
    Deactivate a member
    https://ezo.io/ezofficeinventory/developers/#api-deactivate-user
    """

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + "/deactivate.api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not deactivate member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not deactivate member in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not deactivate member in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not deactivate member in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def activate_member(member_id: int) -> dict:
    """
    Activate a member
    https://ezo.io/ezofficeinventory/developers/#api-activate-user
    """

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + "/activate.api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not activate member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not activate member in EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not activate member in EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not activate member in EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def get_custom_roles() -> list[dict]:
    """
    Get list of custom roles
    Results are technically paginated but the number of custom roles
    is usually small enough that it can be returned in one page.
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-roles
    """

    url = os.environ["EZO_BASE_URL"] + "custom_roles.api"

    pages = 1
    all_custom_roles = []

    while True:
        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": pages},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get custom roles from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get custom roles from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get custom roles from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "custom_roles" not in data:
            print(
                f"Error, could not get custom roles from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get custom roles from EZOfficeInventory: "
                + str(response.content)
            )

        all_custom_roles.extend(data["custom_roles"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if pages >= data["total_pages"]:
            break

        pages += 1

    return all_custom_roles


@Decorators.check_env_vars
def get_teams() -> list[dict]:
    """
    Get teams
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-teams
    """

    url = os.environ["EZO_BASE_URL"] + "teams.api"

    page = 1
    all_teams = []

    while True:
        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get teams from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get teams from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get teams from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "teams" not in data:
            print(
                f"Error, could not get teams from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get teams from EZOfficeInventory: "
                + str(response.content)
            )

        all_teams.extend(data["teams"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_teams
